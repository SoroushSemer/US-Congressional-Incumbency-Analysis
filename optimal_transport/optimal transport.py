"""
optimal_transport.py

@author: Soroush Semerkant

This script generates and compares redistricting plans for a given state using the ReCom algorithm,
Optimal Transport, and K-Means clustering. The multiprocessing library is utilized for parallel processing
to speed up the computation.

Instructions:
    1. Create a directory within the states and name it to the States Abbreviation (eg. Iowa would be "IA")
    2. Copy all shape files for the state into the directory
    3. Update the STATE variable in line 22 to match the state
    4. Update all other parameters in lines 23-26
    5. Install required libraries/modules
    6. Run file
    
"""


STATE = 'IA'            # state to run algorithm on
STEPS = 1000            # number of steps per plan
ENSEMBLE_SIZE = 20      # number of plans in the ensemble
CORES = 5               # number of cores to parallelize across
KMEANS_CLUSTERS = 3     # number of clusters for k-means


from gerrychain import Graph
import matplotlib.pyplot as plt
from gerrychain import (GeographicPartition,  Graph, MarkovChain,
                         updaters, constraints, accept)
from gerrychain.proposals import recom
from functools import partial
from gerrychain.random import random

import warnings
from shapely.errors import ShapelyDeprecationWarning
warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning) 

import multiprocessing as mp

import numpy as np
from wasserplan import Pair
from sklearn.manifold import MDS
from sklearn.cluster import KMeans
import save_data as sd



# Loading graph from shapefile
graph = Graph.from_file(f'./states/{STATE}/{STATE}_counties.shp')

# Setting up updaters for various attributes
my_updaters = {"population": updaters.Tally("TOTPOP", alias="population"),
                "dem_votes": updaters.Tally("PRES16D", alias="dem_votes"), 
                "rep_votes" : updaters.Tally("PRES16R", alias="rep_votes"),
                "total_votes": updaters.Tally("TOTVOT16", alias= "total_votes") ,
                  "other_votes": updaters.Tally("PRES16OTH", alias="other_votes")}
initial_partition = GeographicPartition(graph, assignment="CD", updaters=my_updaters)

# Calculate ideal population for the plan
ideal_population = sum(initial_partition["population"].values()) / len(initial_partition)

# Proposal function for the ReCom algorithm
proposal = partial(recom,
                   pop_col="TOTPOP",
                   pop_target=ideal_population,
                   epsilon=0.03,
                   node_repeats=2
                  )


# Constraint for population to be within 3% of the ideal population
pop_constraint = constraints.within_percent_of_ideal_population(initial_partition, 0.03)


# Function to generate plans using the ReCom algorithm
def gen_plan(process):    
     # Initialize an empty list to store generated partitions
    partitions = []

    # Iterate through a range of seeds for randomness, distributed among processes
    for seed in range(process * (ENSEMBLE_SIZE // CORES), (process + 1) * (ENSEMBLE_SIZE // CORES)):
        # Print progress every 100 seeds
        if (seed % 100 == 0): 
            print(seed)

        # Set the random seed for reproducibility
        random.seed(seed)

        # Create a Markov Chain for the ReCom algorithm
        chain = MarkovChain(
            proposal=proposal,  
            constraints=[pop_constraint],  
            accept=accept.always_accept,  
            initial_state=initial_partition,  
            total_steps=STEPS  
        )


        # Variable to store the final partition after the Markov Chain process
        partitions_final = None

        # Iterate through the Markov Chain with a progress bar
        for partition in chain.with_progress_bar():

            # Set the final partition at the desired step
            partitions_final = partition

        # Append the final partition to the list
        partitions.append(partitions_final)
    
    # Save the list of generated partitions to a JSON file
    sd.dump_run(f'./partitions/{process}.json', partitions)

# Function to compare plans using Optimal Transport
def compare_plans(process):
    # Initialize a matrix to store distances between plans
    distances = np.zeros((ENSEMBLE_SIZE, ENSEMBLE_SIZE))

    # Initialize an empty list to store partitions
    partitions = []

    # Load partitions from other processes and append to the list
    for subensemble in range(process, CORES):
        partitions += sd.load_run(f'./partitions/{subensemble}.json', initial_partition) 
   
    # Calculate the starting index for the current process
    starting_plan = process * (ENSEMBLE_SIZE // CORES)
    
    # Iterate through plans in the current process
    for plan_index, plan in enumerate(partitions[:ENSEMBLE_SIZE // CORES]): 
        
        # Iterate through plans for comparison
        for compared_plan_index, compared_plan in enumerate(partitions):
            
            # Calculate distance between plans using the 'Pair' class
            distance = Pair(plan, compared_plan).distance
            
            # Fill in the distance matrix symmetrically
            distances[starting_plan+plan_index, starting_plan + compared_plan_index] = distance 
            distances[starting_plan + compared_plan_index, starting_plan+plan_index] = distance
    
    # Return the distance matrix
    return distances


# Function to run the entire process
def run_recom():

    # Generate plans in parallel using multiprocessing
    p = mp.Pool(processes = CORES)
    results = [p.apply_async(gen_plan, args =(process, )) for process in range(CORES)]
    for result in results:
        result.get()



    print("Starting Optimal Transport")
    distances = np.zeros((ENSEMBLE_SIZE, ENSEMBLE_SIZE))

    # Compare plans in parallel using multiprocessing
    p = mp.Pool(processes = CORES)
    results = [p.apply_async(compare_plans, args =(process, )) for process in range(CORES)]

    for result in results:
        val = result.get()
        distances += val

    p.close()

    # Save distance matrix to a CSV file
    np.savetxt('./distances.csv', distances, delimiter=',')

    # Perform Multi-Dimensional Scaling (MDS) on the distance matrix
    mds = MDS(n_components=2, random_state=0, dissimilarity='precomputed')
    pos = mds.fit(distances).embedding_


    # Plot the pairwise distance matrix
    plt.title("Pairwise Distance matrix")
    plt.imshow(distances, cmap='jet')
    plt.show()

    # Scatter plot of 2D embedding of plan distances
    plt.scatter(pos[:, 0], pos[:, 1])
    plt.title('2D embedding of plan distances')
    plt.show()

    # Perform K-Means clustering on the embedded plans
    kmeans = KMeans(n_clusters=KMEANS_CLUSTERS, init='k-means++')
    kmeans.fit(pos)
    labels = kmeans.labels_

    # Scatter plot of clustered plans
    plt.scatter(pos[:, 0], pos[:, 1],c=labels)
    plt.title("K-Means Clustering")
    plt.show()




if __name__ == '__main__':
    print("=====SETTINGS=====")
    print("Cores:",CORES)
    print("Steps per Plan:",STEPS)
    print("Ensemble Size:",ENSEMBLE_SIZE)
    print()
    print(f'Running on: {STATE}')
    print("Nodes in Graph:",graph.number_of_nodes())
    run_recom()
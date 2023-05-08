import geopandas as gpd
from gerrychain import Graph
from gerrychain.partition import Partition
from gerrychain.updaters import Tally, cut_edges
import matplotlib.pyplot as plt
from gerrychain import (GeographicPartition, Partition, Graph, MarkovChain,
                        proposals, updaters, constraints, accept, Election)
from gerrychain.proposals import recom
from functools import partial
import pandas as pd
from gerrychain.random import random
import json
# from random import randint


def boxplot(df):
    data = []
    outliers = []
    for column in df.columns:
        max = df[column].max()
        min = df[column].min()
        median = df[column].median()
        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)
        iqr = q3 - q1
        outlier = df[column][(df[column] < (q1 - 1.5 * iqr)) | (df[column] > (q3 + 1.5 * iqr))]
        data.append({
            'x':column,
            'y':[min,q1,median,q3,max],
        })
        for item in outlier:
            outliers.append({'x':column, 'y':item})
    box = {
        'name': 'box',
        'type':'boxPlot',
        'data': data,
        
    }
    scatter = {
        'name': 'outliers',
        'type':'scatter',
        'data': outliers,
    }
    return [box, scatter]

def run_recom(precincts_filename, ensemble_size, steps):
    #read precincts file into gpd
    precincts = gpd.read_file(precincts_filename)

    #create graph
    graph = Graph.from_geodataframe(
        precincts,ignore_errors=True
    )

    print("Maryland 2020 Graph Created")
    print("num nodes:",graph.number_of_nodes())

    #create election object for the r/d votes
    election = Election("election", {"Republican": "REP Votes", "Democratic": "DEM Votes"}, alias="election")

    #create partitions with vap, races, election
    initial_partition = Partition(
        graph,
        assignment="DISTRICT",
        updaters={
            "cut_edges": cut_edges,
            "population": Tally("Tot_2020_vap", alias="population"),
            "wh_population": Tally("Wh_2020_vap", alias="wh_population"),
            "his_population": Tally("His_2020_vap", alias="his_population"),
            "blc_population": Tally("BlC_2020_vap", alias="blc_population"),
            "natc_population": Tally("NatC_2020_vap", alias="natc_population"),
            "asnc_population": Tally("AsnC_2020_vap", alias="asnc_population"),
            "pacc_population": Tally("PacC_2020_vap", alias="pacc_population"),
            "election": election
        }
    )


    #create ideal populations of mean
    ideal_population = sum(initial_partition["population"].values()) / len(initial_partition)


    #establish proposal for recom
    proposal = partial(recom,
                    pop_col="Tot_2020_vap",
                    pop_target=ideal_population,
                    epsilon=0.02,
                    node_repeats=2
                    )

    #create contraint for compactness bound
    compactness_bound = constraints.UpperBound(
        lambda p: len(p["cut_edges"]),
        3*len(initial_partition["cut_edges"])
    )

    #create constraint for population to be within param2 of the ideal population
    pop_constraint = constraints.within_percent_of_ideal_population(initial_partition, 0.10)


    election_results = []
    for seed in range(ensemble_size):
        print(seed)
        random.seed(seed)
        #create chain
        chain = MarkovChain(
            proposal=proposal,
            constraints=[
                # compactness_bound,
                pop_constraint
            ],
            accept=accept.always_accept,
            initial_state=initial_partition,
            total_steps=steps
        )
        count = 1
        for partition in chain.with_progress_bar():
            if(count < steps):
                count+=1
                continue
            # print(partition['election'].percents('REP Votes'))
            election_results.append(sorted(partition['election'].percents('Republican')))
            # print(partition['election'].percents('Republican'))
            # partition.plot()
            # plt.axis('off')
            # plt.show()


    # print("Election results" , election_results)
    data = pd.DataFrame(data = election_results)      
    # print(boxplot(data))

    boxplotData = boxplot(data)
    with open('./out/ensemble.json', 'w') as f:
        json.dump(boxplotData, f)

    fig, ax = plt.subplots(figsize=(8, 6))

    # Draw 50% line
    ax.axhline(0.5, color="#cccccc")

    # Draw boxplot
    data.boxplot(ax=ax, positions=range(len(data.columns)))

    # Draw initial plan's Democratic vote %s (.iloc[0] gives the first row)
    plt.plot(data.iloc[0], "ro")

    # Annotate
    ax.set_title("Comparing the 2020 plan to an ensemble")
    ax.set_ylabel("Rep Vote % (2020)")
    ax.set_xlabel("Sorted districts")
    ax.set_ylim(0, 1)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1])

    plt.show()




run_recom("./Maryland/md_2020_precincts.json",10,10)
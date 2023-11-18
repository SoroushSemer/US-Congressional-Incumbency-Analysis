import geopandas as gpd
from gerrychain import Graph
from gerrychain.partition import Partition
from gerrychain.updaters import Tally, cut_edges, county_splits
import matplotlib.pyplot as plt
from gerrychain import (GeographicPartition, Partition, Graph, MarkovChain,
                        proposals, updaters, constraints, accept, Election)
from gerrychain.proposals import recom
from functools import partial
import pandas as pd
from gerrychain.random import random

from gerrychain.constraints import no_vanishing_districts

import multiprocessing as mp

import numpy as np
import cvxpy as cp
from typing import Dict
from scipy.optimize import linear_sum_assignment
from networkx.linalg.graphmatrix import incidence_matrix
# from wasserplan import Pair
from sklearn.manifold import MDS
from sklearn.cluster import KMeans
import save_data as sd



STEPS = 1000
ENSEMBLE_SIZE = 100
FILENAME = "./states/Iowa/IA_counties.shp"
CORES = 5



class Pair:
    """A pair of isomorphic districting plans to compare."""

    def __init__(self,
                 partition_a: Partition,
                 partition_b: Partition,
                 indicator: str = 'node',
                 pop_col: str = None):
        """
        :param partition_a: The first GerryChain partition to compare.
        :param partition_b: The second GerryChain partition to compare.
        :param indicator: The name of the district indicator scheme to use.
            Valid indicators are "node" (equal population assumed for
            all nodes in the dual graph) and "population" (nodes are weighted
            proportional to population).
        :param pop_col: The name of the attribute specifying a node's
            population. Required for the "population" indicator only.
        """

        if indicator == 'population' and not pop_col:
            raise EmbeddingError('Cannot generate population-based indicators '
                                 'without population data. Specify a '
                                 'population column.')
        if indicator not in ('population', 'node'):
            raise EmbeddingError(f'Unknown indicator type "{indicator}"!')

        self.indicator_type = indicator
        self.pop_col = pop_col
        self.partition_a = partition_a
        self.partition_b = partition_b

        self.node_ordering = {
            node: idx
            for idx, node in enumerate(sorted(partition_a.graph.nodes))
        }

        self.district_ordering = {
            district: idx
            for idx, district in enumerate(sorted(partition_a.parts.keys()))
        }

        self._a_indicators = indicators(partition_a, indicator, pop_col,
                                        self.node_ordering,
                                        self.district_ordering)
        self._b_indicators = indicators(partition_b, indicator, pop_col,
                                        self.node_ordering,
                                        self.district_ordering)
        self._pairwise_distances = None  # lazy-loaded
        self._edge_incidence = None  # lazy-loaded
        self._assignment = None  # lazy-loaded

    def district_distance(self, a_label, b_label) -> np.float64:
        """Calculates the 1-Wasserstein distance between districts.
        Districts are compared across plans only, as districts within
        a plan are disjoint by definition.
        :param a_index: The label of the district to compare in the
           first district (``partition_a``).
        :param b_index: The label of the district to compare in the
           second district (``partition_b``).
        """

        a_idx = self.district_ordering[a_label]
        b_idx = self.district_ordering[b_label]

        if self._pairwise_distances:
            # Avoid recomputation if district distances have already been
            # computed in the course of computing the plan distance.
            return self._pairwise_distances[a_idx][b_idx]
        if self._edge_incidence is None:
            self._edge_incidence = incidence_matrix(self.partition_a.graph,
                                                    oriented=True)

        return district_distance(self._a_indicators[a_idx],
                                 self._b_indicators[b_idx],
                                 self._edge_incidence)

    @property
    def distance(self) -> np.float64:
        """Calculates the 1-Wasserstein distance between plans."""
        if self._pairwise_distances is None:
            self._pairwise_distances = self._get_pairwise_distances()
        if self._assignment is None:
            dist = self._pairwise_distances
            # pylint: disable=invalid-unary-operand-type
            a_indices, b_indices = linear_sum_assignment(dist)
            self._assignment = {
                a_index: b_index
                for a_index, b_index in zip(a_indices, b_indices)
            }

        total_dist = 0
        for a_index, b_index in self._assignment.items():
            total_dist += self._pairwise_distances[a_index][b_index]
        return total_dist

    def _get_pairwise_distances(self) -> np.ndarray:
        """Generates all pairwise distances between districts.
        For a pair of districting plans with :math:`n` districts each,
        there are :math:`n^2` pairs.
        """
        n_districts = len(self.partition_a)
        distances = np.zeros((n_districts, n_districts))
        for a_label, a_idx in self.district_ordering.items():
            for b_label, b_idx in self.district_ordering.items():
                dist = self.district_distance(a_label, b_label)
                distances[a_idx][b_idx] = dist
        return distances


def district_distance(a_indicator: np.ndarray, b_indicator: np.ndarray,
                      edge_incidence: np.ndarray) -> np.float64:
    """Calculates the 1-Wasserstein distance between two districts.
    :param a_indicator: The indicator vector of one district.
    :param b_indicator: The indicator vector of the other district.
    :param edge_incidence: The edge incidence matrix for the districts'
        underlying graph.
    """
    n_edges = edge_incidence.shape[1]
    edge_weights = cp.Variable(n_edges)
    diff = b_indicator - a_indicator
    objective = cp.Minimize(cp.sum(cp.abs(edge_weights)))
    conservation = (edge_incidence @ edge_weights) == diff
    prob = cp.Problem(objective, [conservation])
    prob.solve(solver='ECOS')
    return np.sum(np.abs(edge_weights.value))


def indicators(partition: Partition, indicator_type: str, pop_col: str,
               node_ordering: Dict, district_ordering: Dict) -> np.ndarray:
    """Generates indicator vectors for all districts in a partition."
    :param partition: The partition to generate indicator vectors for.
    :param indicator_type: The type of indicator to use.
    :param pop_col: The node attribute with population counts.
    :param node_ordering: A dictionary mapping NetworkX node labels to
        indicator matrix column indices.
    :param district_ordering: A dictionary mapping district labels to
        indicator matrix row indices.
    :returns: A matrix of indicator vectors (# of districts X # of nodes).
    """
    n_districts = len(partition)
    n_nodes = len(partition.graph.nodes)
    indicator = np.zeros((n_districts, n_nodes))
    if indicator_type == 'node':
        for district_label, district_idx in district_ordering.items():
            nodes_in_district = [
                node_ordering[node] for node in partition.parts[district_label]
            ]
            indicator[district_idx][nodes_in_district] = 1
    elif indicator_type == 'population':
        for district_label, district_idx in district_ordering.items():
            for node_label in partition.parts[district_label]:
                node = partition.graph.nodes[node_label]
                try:
                    node_pop = node[pop_col]
                except KeyError:
                    raise EmbeddingError('Cannot create population '
                                         f'indicator. Node {node_label} '
                                         f'has no "{pop_col}" attribute.')
                node_idx = node_ordering[node_label]
                indicator[district_idx][node_idx] = node_pop

    # Norm so that rows sum to 1.
    return indicator / np.sum(indicator, axis=1).reshape(-1, 1)


class EmbeddingError(Exception):
    """Raised for invalid indicator schemes."""


class IsomorphismError(Exception):
    """Raised if the graphs of a pair of partitions are not isomorphic."""




graph = Graph.from_file(FILENAME)

my_updaters = {"population": updaters.Tally("TOTPOP", alias="population"), "dem_votes": updaters.Tally("PRES16D", alias="dem_votes"), "rep_votes" : updaters.Tally("PRES16R", alias="rep_votes"),"total_votes": updaters.Tally("TOTVOT16", alias= "total_votes") , "other_votes": updaters.Tally("PRES16OTH", alias="other_votes")}
initial_partition = GeographicPartition(graph, assignment="CD", updaters=my_updaters)

#create ideal populations of mean
ideal_population = sum(initial_partition["population"].values()) / len(initial_partition)

proposal = partial(recom,
                   pop_col="TOTPOP",
                   pop_target=ideal_population,
                   epsilon=0.03,
                   node_repeats=2
                  )


#create constraint for population to be within param2 of the ideal population
pop_constraint = constraints.within_percent_of_ideal_population(initial_partition, 0.03)



def gen_plan(process):    
    partitions = []
    for seed in range(process * (ENSEMBLE_SIZE // CORES), (process+1) * (ENSEMBLE_SIZE // CORES)):
        if (seed % 100 == 0): print(seed)
        random.seed(seed)
        chain = MarkovChain(
                proposal=proposal,
                constraints=[pop_constraint],
                accept=accept.always_accept,
                initial_state=initial_partition,
                total_steps=STEPS
            )
        count = 1
        partitions_final = None
        for partition in chain.with_progress_bar():
            if(count < STEPS):
                count+=1
                continue
            partitions_final = partition
        partitions.append(partitions_final)
    
    sd.dump_run(f'./partitions/{process}.json', partitions)
    return True

plans = None
def compare_plans(process):
    distances = np.zeros((ENSEMBLE_SIZE, ENSEMBLE_SIZE))
    partitions = []
    for subensemble in range(process, CORES):
        partitions += sd.load_run(f'./partitions/{subensemble}.json', initial_partition) #10 8 6 4 2
    starting_plan = process * (ENSEMBLE_SIZE // CORES) # 0 2 4 6 8
    
    for plan_index, plan in enumerate(partitions[:ENSEMBLE_SIZE // CORES]): # 0 1
        for compared_plan_index, compared_plan in enumerate(partitions):
            distance = Pair(plan, compared_plan).distance
            distances[starting_plan+plan_index, starting_plan + compared_plan_index] = distance #0 1 2 3 4 5 6 7 8 9, 
            distances[starting_plan + compared_plan_index, starting_plan+plan_index] = distance


    return distances


def run_recom():
    p = mp.Pool(processes = CORES)
    results = [p.apply_async(gen_plan, args =(process, )) for process in range(CORES)]
    for result in results:
        result.get()

    print("Starting Optimal Transport")
    distances = np.zeros((ENSEMBLE_SIZE, ENSEMBLE_SIZE))


    p = mp.Pool(processes = CORES)
    results = [p.apply_async(compare_plans, args =(process, )) for process in range(CORES)]

    for result in results:
        val = result.get()
        distances += val

    p.close()
    np.savetxt('./distances.csv', distances, delimiter=',')


    mds = MDS(n_components=2, random_state=0, dissimilarity='precomputed')
    pos = mds.fit(distances).embedding_

    plt.title("pairwise distance matrix")
    plt.imshow(distances, cmap='jet')
    plt.show()

    plt.scatter(pos[:, 0], pos[:, 1])
    plt.title('2D embedding of plan distances')
    plt.show()

    plt.figure(figsize=(3, 3))
    n_clusters = 3
    kmeans = KMeans(n_clusters=n_clusters, init='k-means++')
    kmeans.fit(pos)
    labels = kmeans.labels_
    plt.scatter(pos[:, 0], pos[:, 1],c=labels)
    plt.title("K-Means Clustering")
    plt.show()




if __name__ == '__main__':
    print("=====SETTINGS=====")
    print("num cores:",CORES)
    print("num steps:",STEPS)
    print("num ensemble:",ENSEMBLE_SIZE)
    print()
    print(f'Running on: {FILENAME}')
    print("num nodes:",graph.number_of_nodes())
    run_recom()
else:
    print("parallel process running")
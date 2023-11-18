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
import json
import os.path

# from random import randint


STEPS = 1000
ENSEMBLE_SIZE = 100
# FILENAME = "./Maryland/md_2020_precincts.json"
# FILENAME = "./Arizona/az_2020_precincts.json"
FILENAME = "./Louisiana/la_2020_precincts.json"
CORES = 5




import numpy as np
import cvxpy as cp
import networkx as nx
from typing import List, Dict
from scipy.optimize import linear_sum_assignment
from networkx.linalg.graphmatrix import incidence_matrix
from tqdm import tqdm
from random import sample
# from wasserplan import Pair
from sklearn.manifold import MDS
from sklearn.cluster import KMeans
import save_data as sd
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







precincts = gpd.read_file(FILENAME)

#create graph
graph = Graph.from_geodataframe(
    precincts,ignore_errors=True
)



#create election object for the r/d votes
election = Election("election", {"Republican": "REP Votes", "Democratic": "DEM Votes"}, alias="election")

#create partitions with vap, races, election

initial_partition = Partition(
    graph,
    assignment="DISTRICT",
    updaters={
        "cut_edges": cut_edges,
        "population": Tally("Tot_2020_vap", alias="population", dtype=int),
        "wh_population": Tally("Wh_2020_vap", alias="wh_population", dtype=int),
        "his_population": Tally("His_2020_vap", alias="his_population", dtype=int),
        "blc_population": Tally("BlC_2020_vap", alias="blc_population", dtype=int),
        "natc_population": Tally("NatC_2020_vap", alias="natc_population", dtype=int),
        "asnc_population": Tally("AsnC_2020_vap", alias="asnc_population", dtype=int),
        "pacc_population": Tally("PacC_2020_vap", alias="pacc_population", dtype=int),
        "area": Tally("AREA", alias="area", dtype=float),
        
        "election": election
    }
)

#create ideal populations of mean
ideal_population = sum(initial_partition["population"].values()) / len(initial_partition)


#establish proposal for recom
proposal = partial(recom,
                pop_col="Tot_2020_vap",
                pop_target=ideal_population,
                epsilon=0.2,
                node_repeats=1
                )
    #create contraint for compactness bound
compactness_bound = constraints.UpperBound(
    lambda p: len(p["cut_edges"]),
    2*len(initial_partition["cut_edges"])
)

#create constraint for population to be within param2 of the ideal population
pop_constraint = constraints.within_percent_of_ideal_population(initial_partition, 0.50)




def export_plan(initial_partition, partition, precincts, description):
    if(partition == None): return
    if(os.path.isfile("./Louisiana_GeneratedPlan_"+description+".json")): return
    temp = partition.graph
    incumbent_dist_map = {}
    for i, district in enumerate(initial_partition['population'].items()):
        incumbent_dist_map[district[0]] =( "NO INCUMBENT DISTRICT #"+district[0], "N/A")
        
    for i in range(len(temp.nodes)):
        if(temp.nodes[i]['HOME_PRECINCT']):
            incumbent_dist_map[partition.assignment[i]] = (temp.nodes[i]['INCUMBENT'], temp.nodes[i]['PARTY'])
        node_in_geo = precincts[precincts['GEOID20'] == temp.nodes[i]['GEOID20']].iloc[0]
        if(partition.assignment[i] != node_in_geo.DISTRICT):
            precincts.loc[precincts['GEOID20'] == temp.nodes[i]['GEOID20'],"DISTRICT"] = partition.assignment[i]
    
    for i in partition['population'].items():
        precincts.loc[precincts['DISTRICT'] == i[0],"INCUMBENT"] = incumbent_dist_map[i[0]][0]
        precincts.loc[precincts['DISTRICT'] == i[0],"PARTY"] = incumbent_dist_map[i[0]][1]
        
    
    #precincts['NEIGHBORS'] = precincts['NEIGHBORS'].apply(lambda x: ", ".join(x))

    district = precincts.dissolve('DISTRICT')
    republican = partition['election'].counts('Republican')
    democrat = partition['election'].counts('Democratic')
    colors = ['red', 'blue', 'green', 'yellow', 'cyan', 'magenta', 'purple', 'orange', 'teal', 'gray']

    for index, i in enumerate(partition['population'].items()):
        district.loc[i[0],"Tot_2020_vap"] = i[1]
        district.loc[i[0],"REP Votes"] = republican[index]
        district.loc[i[0],"DEM Votes"] = democrat[index]
        district.loc[i[0],"COLOR"] = colors[index]
        
    for i in partition['wh_population'].items():
        district.loc[i[0],"Wh_2020_vap"] = i[1]
    for i in partition['his_population'].items():
        district.loc[i[0],"His_2020_vap"] = i[1]
    for i in partition['blc_population'].items():
        district.loc[i[0],"BlC_2020_vap"] = i[1]
    for i in partition['natc_population'].items():
        district.loc[i[0],"NatC_2020_vap"] = i[1]
    for i in partition['asnc_population'].items():
        district.loc[i[0],"AsnC_2020_vap"] = i[1]
    for i in partition['pacc_population'].items():
        district.loc[i[0],"PacC_2020_vap"] = i[1]
    for i in partition['area'].items():
        district.loc[i[0],"AREA"] = i[1]
    
    del district['NEIGHBORS']
    del district['GEOID20']
    del district['NAMELSAD20']
    del district['HOME_PRECINCT']
 

    district.to_file("./Maryland_NewGeneratedPlan_"+description+".json")
    print("Generated", description)

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


def calc_var(initial_partition, new_partition):
    var = {
            'popVar': [],'whVar': [],'hisVar': [],'blcVar': [],'natcVar': [],'asncVar': [],'paccVar': [],'areaVar': [],}
    for district in initial_partition.assignment.parts.keys():
        b = new_partition.assignment.parts[district] - initial_partition.assignment.parts[district]
        gb = new_partition.assignment.parts[district].union(initial_partition.assignment.parts[district])
        graph = initial_partition.graph
        sum_gb = {'population':0,  'wh_population':0, 'his_population':0, 'blc_population':0, 'natc_population':0, 'asnc_population':0, 'pacc_population':0, 'area':0}
        for node in gb:
            sum_gb['population'] += graph.nodes[node]['Tot_2020_vap']
            sum_gb['wh_population'] += graph.nodes[node]['Wh_2020_vap']
            sum_gb['his_population'] += graph.nodes[node]['His_2020_vap']
            sum_gb['blc_population'] += graph.nodes[node]['BlC_2020_vap']
            sum_gb['natc_population'] += graph.nodes[node]['NatC_2020_vap']
            sum_gb['asnc_population'] += graph.nodes[node]['AsnC_2020_vap']
            sum_gb['pacc_population'] += graph.nodes[node]['PacC_2020_vap']
            sum_gb['area'] += graph.nodes[node]['AREA']
        sum_b={'population':0,  'wh_population':0, 'his_population':0, 'blc_population':0, 'natc_population':0, 'asnc_population':0, 'pacc_population':0, 'area':0}
        for node in b:
            sum_b['population'] += graph.nodes[node]['Tot_2020_vap']
            sum_b['wh_population'] += graph.nodes[node]['Wh_2020_vap']
            sum_b['his_population'] += graph.nodes[node]['His_2020_vap']
            sum_b['blc_population'] += graph.nodes[node]['BlC_2020_vap']
            sum_b['natc_population'] += graph.nodes[node]['NatC_2020_vap']
            sum_b['asnc_population'] += graph.nodes[node]['AsnC_2020_vap']
            sum_b['pacc_population'] += graph.nodes[node]['PacC_2020_vap']
            sum_b['area'] += graph.nodes[node]['AREA']
        var['popVar'].append(round(sum_b['population']/sum_gb['population'],3))
        var['whVar'].append(round(sum_b['wh_population']/sum_gb['wh_population'],3))
        var['hisVar'].append(round(sum_b['his_population']/sum_gb['his_population'],3))
        var['blcVar'].append(round(sum_b['blc_population']/sum_gb['blc_population'],3))
        var['natcVar'].append(round(sum_b['natc_population']/sum_gb['natc_population'],3))
        var['asncVar'].append(round(sum_b['asnc_population']/sum_gb['asnc_population'],3))
        var['paccVar'].append(round(sum_b['pacc_population']/sum_gb['pacc_population'],3))
        var['areaVar'].append(round(sum_b['area']/sum_gb['area'],3))
        
        
    return var     



def gen_plan(process):
    
    partitions = []
    for seed in range(process * (ENSEMBLE_SIZE // CORES), (process+1) * (ENSEMBLE_SIZE // CORES)):
        if (seed % 100 == 0): print(seed)
        random.seed(seed)
        chain = MarkovChain(
                proposal=proposal,
                constraints=[no_vanishing_districts, pop_constraint, compactness_bound],
                accept=accept.always_accept,
                initial_state=initial_partition,
                total_steps=STEPS
            )
        count = 1
        var = None
        election = None
        paritions_final = None
        for partition in chain.with_progress_bar():
            if(count < STEPS):
                count+=1
                continue
            var = calc_var(initial_partition, partition)
            election = sorted(partition['election'].percents('Republican'))
            # partition.plot()
            if(partition['election'].seats('Republican')>10):
                export_plan(initial_partition, partition, precincts, "REP_Favored ("+str(partition['election'].seats('Republican'))+" wins)")       
        
            elif(partition['election'].seats('Democratic')>10):
                export_plan(initial_partition, partition, precincts, "DEM_Favored ("+str(partition['election'].seats('Democratic'))+" wins)")
        
            if(max(var['popVar']) > 1.0):
                export_plan(initial_partition, partition, precincts, "High_Pop_Var ("+str(round(max(var['popVar']),2))+" max)")
        
            if(max(var['areaVar']) > 1.0):
                export_plan(initial_partition, partition, precincts, "High_Geo_Var ("+str(round(max(var['areaVar']),2))+" max)")
            partition_final = partition
        partitions.append(partition_final)
    
    sd.dump_run(f'./partitions/{process}.json', partitions)
    return var, election

plans = None
def compare_plans(process):
    distances = np.zeros((ENSEMBLE_SIZE, ENSEMBLE_SIZE))
    partitions = []
    for subensemble in range(process, CORES):
        partitions += sd.load_run(f'./partitions/{subensemble}.json', initial_partition) #10 8 6 4 2
    # print(len(partitions))
    starting_plan = process * (ENSEMBLE_SIZE // CORES) # 0 2 4 6 8
    
    for plan_index, plan in enumerate(partitions[:ENSEMBLE_SIZE // CORES]): # 0 1
        for compared_plan_index, compared_plan in enumerate(partitions):
            # if(starting_plan+plan_index >=ENSEMBLE_SIZE or starting_plan+plan_index+compared_plan_index>=ENSEMBLE_SIZE):
            #     break
            distance = Pair(plan, compared_plan).distance
            distances[starting_plan+plan_index, starting_plan + compared_plan_index] = distance #0 1 2 3 4 5 6 7 8 9, 
            distances[starting_plan + compared_plan_index, starting_plan+plan_index] = distance
            # print(f'({starting_plan+plan_index},{starting_plan + compared_plan_index})')


    return distances

def run_recom():

    # election_results = []
    box_whiskers = {'election':[], 'popVar':[], 'whVar':[], 'hisVar':[], 'blcVar':[], 'natcVar':[], 'asncVar':[], 'paccVar':[], 'areaVar':[]}
   

    p = mp.Pool(processes = CORES)
    results = [p.apply_async(gen_plan, args =(process, )) for process in range(CORES)]
    for result in results:
        # var, percRepublican,plan = result.get()
        var, percRepublican = result.get()


        box_whiskers['election'].append(percRepublican)
        
        
        box_whiskers['popVar'].append(sorted(var['popVar']))
        box_whiskers['whVar'].append(sorted(var['whVar']))
        box_whiskers['hisVar'].append(sorted(var['hisVar']))
        box_whiskers['blcVar'].append(sorted(var['blcVar']))
        box_whiskers['natcVar'].append(sorted(var['natcVar']))
        box_whiskers['asncVar'].append(sorted(var['asncVar']))
        box_whiskers['paccVar'].append(sorted(var['paccVar']))
        box_whiskers['areaVar'].append(sorted(var['areaVar']))

        
    # p.close()
    # n = 8
    print("Starting Optimal Transport")
    # distances = np.zeros((n+1, n+1))
    distances = np.zeros((ENSEMBLE_SIZE, ENSEMBLE_SIZE))
    # distances = []
    #plans = sample(parts, n)
    # plans = plans[:n]

   

    p = mp.Pool(processes = CORES)
    results = [p.apply_async(compare_plans, args =(process, )) for process in range(CORES)]

    for i, result in enumerate(results):
        val = result.get()
        distances += val

    p.close()

    # distances = np.asarray(distances)
    # for outer_idx in range(n+1):
    #     for inner_idx in range(outer_idx + 1, n):
    #         distances[inner_idx, outer_idx] = distances[outer_idx, inner_idx]
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
    plt.subplot(221)
    plt.scatter(pos[:, 0], pos[:, 1],c=labels)
    plt.title("K-Means Clustering")
    plt.show()


    election_data = pd.DataFrame(data = box_whiskers['election'])      
    population_data = pd.DataFrame(data = box_whiskers['popVar'])
    wh_data = pd.DataFrame(data = box_whiskers['whVar'])
    his_data = pd.DataFrame(data = box_whiskers['hisVar'])
    blc_data = pd.DataFrame(data = box_whiskers['blcVar'])
    natc_data = pd.DataFrame(data = box_whiskers['natcVar'])
    asnc_data = pd.DataFrame(data = box_whiskers['asncVar'])
    pacc_data = pd.DataFrame(data = box_whiskers['paccVar'])
    area_data = pd.DataFrame(data = box_whiskers['areaVar'])


    electionBoxplotData = boxplot(election_data)
    populationBoxplotData = boxplot(population_data)
    whBoxplotData = boxplot(wh_data)
    hisBoxplotData = boxplot(his_data)
    blcBoxplotData = boxplot(blc_data)
    natcBoxplotData = boxplot(natc_data)
    asncBoxplotData = boxplot(asnc_data)
    paccBoxplotData = boxplot(pacc_data)
    areaBoxplotData = boxplot(area_data)

    ensembleData = {
        "election":electionBoxplotData,
        "popVar":populationBoxplotData,
        "whVar":whBoxplotData,
        "hisVar":hisBoxplotData,
        "blcVar":blcBoxplotData,
        "natcVar":natcBoxplotData,
        "asncVar":asncBoxplotData,
        "paccVar":paccBoxplotData,
        "areaVar":areaBoxplotData
    }
    print("Generated Ensemble Data")
    with open('./Louisiana_ensemble.json', 'w') as f:
        json.dump(ensembleData, f)





if __name__ == '__main__':
    print("=====SETTINGS=====")
    print("num cores:",CORES)
    print("num steps:",STEPS)
    print("num ensemble:",ENSEMBLE_SIZE)
    print()
    print("Lousiana 2020 Graph Created")
    print("num nodes:",graph.number_of_nodes())
    run_recom()
else:
    print("parallel process running")
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
# from random import randint


STEPS = 100
ENSEMBLE_SIZE = 10000
FILENAME = "./Maryland/md_2020_precincts.json"
CORES = 4 






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
pop_constraint = constraints.within_percent_of_ideal_population(initial_partition, 0.20)




def export_plan(initial_partition, partition, precincts, description):
    if(partition == None): return
   
    temp = partition.graph
    incumbent_dist_map = {}
    for i, district in enumerate(initial_partition['population'].items()):
        incumbent_dist_map[district[0]] = "NO INCUMBENT DISTRICT #"+district[0]
        
    for i in range(len(temp.nodes)):
        if(temp.nodes[i]['HOME_PRECINCT']):
            incumbent_dist_map[partition.assignment[i]] = temp.nodes[i]['INCUMBENT']
        node_in_geo = precincts[precincts['GEOID20'] == temp.nodes[i]['GEOID20']].iloc[0]
        if(partition.assignment[i] != node_in_geo.DISTRICT):
            precincts.loc[precincts['GEOID20'] == temp.nodes[i]['GEOID20'],"DISTRICT"] = partition.assignment[i]
    
    for i in partition['population'].items():
        precincts.loc[precincts['DISTRICT'] == i[0],"INCUMBENT"] = incumbent_dist_map[i[0]]
        
    
    precincts['NEIGHBORS'] = precincts['NEIGHBORS'].apply(lambda x: ", ".join(x))

    district = precincts.dissolve('DISTRICT')
    republican = partition['election'].counts('Republican')
    democrat = partition['election'].counts('Democratic')
    colors = ['red', 'blue', 'green', 'yellow', 'cyan', 'magenta', 'purple', 'orange']

    for index, i in enumerate(partition['population'].items()):
        district.loc[i[0],"Tot_2020_vap"] = i[1]
        district.loc[i[0],"REP Votes"] = republican[index]
        district.loc[i[0],"DEM Votes"] = democrat[index]
        if(democrat[index] > republican[index]):
            district.loc[i[0],"PARTY"] = "DEM"
        else:
            district.loc[i[0],"PARTY"] = "REP"
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
 

    district.to_file("./out/GeneratedPlan_"+description+".json")
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
    vars = {
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
        vars['popVar'].append(sum_b['population']/sum_gb['population'])
        vars['whVar'].append(sum_b['wh_population']/sum_gb['wh_population'])
        vars['hisVar'].append(sum_b['his_population']/sum_gb['his_population'])
        vars['blcVar'].append(sum_b['blc_population']/sum_gb['blc_population'])
        vars['natcVar'].append(sum_b['natc_population']/sum_gb['natc_population'])
        vars['asncVar'].append(sum_b['asnc_population']/sum_gb['asnc_population'])
        vars['paccVar'].append(sum_b['pacc_population']/sum_gb['pacc_population'])
        vars['areaVar'].append(sum_b['area']/sum_gb['area'])
        
        
    return vars     



def gen_plan(seed):
    if seed % 100 ==0 : print(seed)
    random.seed(seed)
    chain = MarkovChain(
            proposal=proposal,
            constraints=[no_vanishing_districts, pop_constraint, compactness_bound],
            accept=accept.always_accept,
            initial_state=initial_partition,
            total_steps=STEPS
        )
    count = 1
    vars = None
    election = None
    for partition in chain.with_progress_bar():
        if(count < STEPS):
            count+=1
            continue
        vars = calc_var(initial_partition, partition)
        election = sorted(partition['election'].percents('Republican'))
        # partition.plot()
        if(partition['election'].seats('Republican')>2):
            export_plan(initial_partition, partition, precincts, "REP_Favored ("+str(partition['election'].seats('Republican'))+" wins)")       
    
        # elif(partition['election'].seats('Democratic')>7):
        #     export_plan(initial_partition, partition, precincts, "DEM_Favored ("+str(partition['election'].seats('Democratic'))+" wins)")
    
        if(max(vars['popVar']) > 0.6):
            export_plan(initial_partition, partition, precincts, "High_Pop_Var ("+str(round(max(vars['popVar']),2))+" max)")
    
        if(max(vars['areaVar']) > 0.95):
            export_plan(initial_partition, partition, precincts, "High_Geo_Var ("+str(round(max(vars['areaVar']),2))+" max)")

    return vars, election
    

def run_recom():

    # election_results = []
    box_whiskers = {'election':[], 'popVar':[], 'whVar':[], 'hisVar':[], 'blcVar':[], 'natcVar':[], 'asncVar':[], 'paccVar':[], 'areaVar':[]}


    p = mp.Pool(processes = CORES)
    results = [p.apply_async(gen_plan, args =(seed,)) for seed in range(ENSEMBLE_SIZE)]
    for result in results:
        vars, percRepublican = result.get()
        box_whiskers['election'].append(percRepublican)
        
        
        box_whiskers['popVar'].append(sorted(vars['popVar']))
        box_whiskers['whVar'].append(sorted(vars['whVar']))
        box_whiskers['hisVar'].append(sorted(vars['hisVar']))
        box_whiskers['blcVar'].append(sorted(vars['blcVar']))
        box_whiskers['natcVar'].append(sorted(vars['natcVar']))
        box_whiskers['asncVar'].append(sorted(vars['asncVar']))
        box_whiskers['paccVar'].append(sorted(vars['paccVar']))
        box_whiskers['areaVar'].append(sorted(vars['areaVar']))

        
    p.close()

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
    with open('./out/ensemble.json', 'w') as f:
        json.dump(ensembleData, f)





if __name__ == '__main__':
    print("=====SETTINGS=====")
    print("num cores:",CORES)
    print("num steps:",STEPS)
    print("num ensemble:",ENSEMBLE_SIZE)
    print()
    print("Maryland 2020 Graph Created")
    print("num nodes:",graph.number_of_nodes())
    run_recom()
else:
    print("parallel process running")
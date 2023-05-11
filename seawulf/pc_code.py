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


import json
# from random import randint


def export_plan(initial_partition, partition, precincts, description):
    if(partition == None): return
   
    temp = partition.graph
    incumbent_dist_map = {}
    for i, district in enumerate(initial_partition['population'].items()):
        incumbent_dist_map[district[0]] = "NO INCUMBENT DISTRICT #"+district[0]
        
    for i in range(len(temp.nodes)):
        if(temp.nodes[i]['HOME_PRECINCT']):
            incumbent_dist_map[partition.assignment[i]] = (temp.nodes[i]['INCUMBENT'], temp.nodes[i]['PARTY'])
        node_in_geo = precincts[precincts['GEOID20'] == temp.nodes[i]['GEOID20']].iloc[0]
        if(partition.assignment[i] != node_in_geo.DISTRICT):
            precincts.loc[precincts['GEOID20'] == temp.nodes[i]['GEOID20'],"DISTRICT"] = partition.assignment[i]
    
    for i in partition['population'].items():
        precincts.loc[precincts['DISTRICT'] == i[0],"INCUMBENT"] = incumbent_dist_map[i[0]][0]
        precincts.loc[precincts['DISTRICT'] == i[0],"PARTY"] = incumbent_dist_map[i[0]][1]
        
    
    precincts['NEIGHBORS'] = precincts['NEIGHBORS'].apply(lambda x: ", ".join(x))

    district = precincts.dissolve('DISTRICT')
    republican = partition['election'].counts('Republican')
    democrat = partition['election'].counts('Democratic')
    colors = ['red', 'blue', 'green', 'yellow', 'cyan', 'magenta', 'purple', 'orange']

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
 

    district.to_file("C:/Users/fahee/Desktop/CSE-416-Project/seawulf/out/GeneratedPlan_"+description+".json")
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
                    epsilon=0.02,
                    node_repeats=1
                    )

    #create contraint for compactness bound
    compactness_bound = constraints.UpperBound(
        lambda p: len(p["cut_edges"]),
        2*len(initial_partition["cut_edges"])
    )

    #create constraint for population to be within param2 of the ideal population
    pop_constraint = constraints.within_percent_of_ideal_population(initial_partition, 0.20)


    # election_results = []
    box_whiskers = {'election':[], 'popVar':[], 'whVar':[], 'hisVar':[], 'blcVar':[], 'natcVar':[], 'asncVar':[], 'paccVar':[], 'areaVar':[]}
    republican_favored_val = 2
    republican_favored = None
    democrat_favored_val = 8
    democrat_favored = None
    high_pop_var_val = 0.534
    high_pop_var = None
    high_geo_var_va = 0.930
    high_geo_var = None
    
    for seed in range(ensemble_size):
        
        if seed %100 ==0: 
            print(seed)
            random.seed(seed+5)
        # random.seed(seed*17)
        #create chain
        chain = MarkovChain(
            proposal=proposal,
            constraints=[no_vanishing_districts, pop_constraint, compactness_bound],
            accept=accept.always_accept,
            initial_state=initial_partition,
            total_steps=steps
        )
        count = 1
        for partition in chain.with_progress_bar():
            if(count < steps):
                count+=1
                continue
            box_whiskers['election'].append(sorted(partition['election'].percents('Republican')))
            
            vars = calc_var(initial_partition, partition)
            box_whiskers['popVar'].append(sorted(vars['popVar']))
            box_whiskers['whVar'].append(sorted(vars['whVar']))
            box_whiskers['hisVar'].append(sorted(vars['hisVar']))
            box_whiskers['blcVar'].append(sorted(vars['blcVar']))
            box_whiskers['natcVar'].append(sorted(vars['natcVar']))
            box_whiskers['asncVar'].append(sorted(vars['asncVar']))
            box_whiskers['paccVar'].append(sorted(vars['paccVar']))
            box_whiskers['areaVar'].append(sorted(vars['areaVar']))

            # partition.plot()
            if(partition['election'].seats('Republican')>republican_favored_val):
                republican_favored_val = partition['election'].seats('Republican')
                republican_favored = partition
            elif(partition['election'].seats('Democratic')>democrat_favored_val):
                democrat_favored_val = partition['election'].seats('Democratic')
                democrat_favored = partition
            
            if(max(vars['popVar']) > high_pop_var_val):
                high_pop_var_val = max(vars['popVar'])
                high_pop_var = partition
            if(max(vars['areaVar']) > high_geo_var_va):
                high_geo_var_va = max(vars['areaVar'])
                high_geo_var = partition
    
    export_plan(initial_partition, republican_favored, precincts, "REP_Favored ("+str(republican_favored_val)+" wins)")       
    export_plan(initial_partition, democrat_favored, precincts, "DEM_Favored ("+str(democrat_favored_val)+" wins)")
    export_plan(initial_partition, high_pop_var, precincts, "High_Pop_Var ("+str(high_pop_var_val)+" max)")
    export_plan(initial_partition, high_geo_var, precincts, "High_Geo_Var ("+str(high_geo_var_va)+" max)")

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
    with open('C:/Users/fahee/Desktop/CSE-416-Project/seawulf/out/ensemble.json', 'w') as f:
        json.dump(ensembleData, f)


    fig, ax = plt.subplots(figsize=(8, 6))

    # Draw 50% line
    ax.axhline(0.5, color="#cccccc")

    # Draw boxplot
    population_data.boxplot(ax=ax, positions=range(len(population_data.columns)))

    plt.plot(population_data.iloc[0], "ro")

    # Annotate
    ax.set_title("Comparing the 2020 plan to an ensemble")
    ax.set_ylabel("Population Variation (2020 v. Ensemble)")
    ax.set_xlabel("Sorted districts")
    ax.set_ylim(0, 1)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1])

    plt.show()

    fig, ax = plt.subplots(figsize=(8, 6))

    # Draw 50% line
    ax.axhline(0.5, color="#cccccc")

    # Draw boxplot
    area_data.boxplot(ax=ax, positions=range(len(area_data.columns)))

    plt.plot(area_data.iloc[0], "ro")

    # Annotate
    ax.set_title("Comparing the 2020 plan to an ensemble")
    ax.set_ylabel("Geographic Variation (2020 v. Ensemble)")
    ax.set_xlabel("Sorted districts")
    ax.set_ylim(0, 1)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1])

    plt.show()




run_recom("C:/Users/fahee/Desktop/CSE-416-Project/seawulf/Maryland/md_2020_precincts.json",1000,10)
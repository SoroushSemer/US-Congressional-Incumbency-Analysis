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
random.seed(212479002)

precincts = gpd.read_file("md_2020_complete.json")
#print(precincts.head()['geometry'])
# print("read file")

graph = Graph.from_geodataframe(
    precincts,ignore_errors=True
)



# graph = Graph.from_json("PA_VTDs.json")
# graph = Graph.from_file("PA_2020_vtds.zip", ignore_errors = True)
print("graph created")
print("num nodes:",graph.number_of_nodes())
bl = Election("BL", {"Black": "BlC_2020_vap", "Total": "Tot_2020_vap"})
# initial_partition = Partition(graph, "incumbent", {node: graph.nodes[node]["INCUMBENT"] for node in graph.nodes})
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
        "BL": bl
    }
)
print("num partitions:",len(initial_partition.parts))


print("-----------2020 District Plan-------------")
for i in initial_partition['population'].items():
    print("District",i[0],":",i[1])

ideal_population = sum(initial_partition["population"].values()) / len(initial_partition)


proposal = partial(recom,
                   pop_col="Tot_2020_vap",
                   pop_target=ideal_population,
                   epsilon=0.02,
                   node_repeats=2
                  )

compactness_bound = constraints.UpperBound(
    lambda p: len(p["cut_edges"]),
    3*len(initial_partition["cut_edges"])
)

pop_constraint = constraints.within_percent_of_ideal_population(initial_partition, 0.10)

chain = MarkovChain(
    proposal=proposal,
    constraints=[
        compactness_bound,
        pop_constraint
    ],
    accept=accept.always_accept,
    initial_state=initial_partition,
    total_steps=10000
)


# data = pd.DataFrame(
#     sorted(partition["BL"].percents("Black"))
#     for partition in chain.with_progress_bar()
# )
# # print(data.head())
# fig, ax = plt.subplots(figsize=(8, 6))

# # Draw 50% line
# ax.axhline(0.5, color="#cccccc")

# # Draw boxplot
# data.boxplot(ax=ax, positions=range(len(data.columns)))

# # Draw initial plan's Democratic vote %s (.iloc[0] gives the first row)
# plt.plot(data.iloc[0], "ro")

# # Annotate
# ax.set_title("Comparing the 2020 plan to an ensemble")
# ax.set_ylabel("Black Population % (2020)")
# ax.set_xlabel("Sorted districts")
# ax.set_ylim(0, 1)
# ax.set_yticks([0, 0.25, 0.5, 0.75, 1])

# plt.show()




count = 0
# test = gpd.read_file("md_2020_complete.json",encoding='latin1')
# test['NEIGHBORS'] = test['NEIGHBORS'].apply(lambda x: ", ".join(x))
# test = test.to_crs(4326)
# test.to_file('md_2020_reproj.json', driver="GeoJSON")
for partition in chain.with_progress_bar():
    if(count < 9999):
        # if(count %1000 == 0):
        #     partition.plot()
        count+=1
        continue
    print("-----------Randomly Generated District Plan #",count,"-------------")
    partition.plot()
    plt.axis('off')
    plt.show()
    # for i in range(0, len(partition.graph.nodes), 100): 
    #     print(partition.graph.nodes[i])
    # print(partition.items())
    for i in partition['population'].items():
        print("District",i[0],":",i[1])

    temp = partition.graph
    print(temp.nodes[0])
    
    print(partition.assignment[0])
    # print(temp.nodes[0])
    # print(precincts[precincts['GEOID20'] == temp.nodes[0]['GEOID20']])

    incumbent_dist_map = {}
    for i, district in enumerate(initial_partition['population'].items()):
        incumbent_dist_map[district[0]] = "NO INCUMBENT DISTRICT #"+district[0]
        print(district)
    for i in range(len(temp.nodes)):
        if(temp.nodes[i]['HOME_PRECINCT']):
            incumbent_dist_map[partition.assignment[i]] = temp.nodes[i]['INCUMBENT']
        node_in_geo = precincts[precincts['GEOID20'] == temp.nodes[i]['GEOID20']].iloc[0]
        if(partition.assignment[i] != node_in_geo.DISTRICT):
            print(temp.nodes[i]['GEOID20'], "moved")
            precincts.loc[precincts['GEOID20'] == temp.nodes[i]['GEOID20'],"DISTRICT"] = partition.assignment[i]
    
    for i in partition['population'].items():
        precincts.loc[precincts['DISTRICT'] == i[0],"INCUMBENT"] = incumbent_dist_map[i[0]]
    
    precincts['NEIGHBORS'] = precincts['NEIGHBORS'].apply(lambda x: ", ".join(x))

    district = precincts.dissolve('DISTRICT')
    precincts = precincts.to_crs(4326)
    district = district.to_crs(4326)
    print(district.head())
    # district['NEIGHBORS'] = district['NEIGHBORS'].apply(lambda x: ", ".join(x))
    district.to_file("GeneratedPlan2.json")
    # precincts.to_file("GeneratedPlan"+str(count)+".json")
    count+=1
    if count > 3: break
    # temp.to_json("test.json")

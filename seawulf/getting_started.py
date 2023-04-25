import geopandas as gpd
from gerrychain import Graph
from gerrychain.partition import Partition
from gerrychain.updaters import Tally, cut_edges
import matplotlib.pyplot as plt
from gerrychain import (GeographicPartition, Partition, Graph, MarkovChain,
                        proposals, updaters, constraints, accept, Election)
from gerrychain.proposals import recom
from functools import partial


precincts = gpd.read_file("md_2020_complete.json")
precincts = precincts.to_crs(4326)
#print(precincts.head()['geometry'])
# print("read file")

graph = Graph.from_geodataframe(
    precincts,ignore_errors=True
)

# graph = Graph.from_json("PA_VTDs.json")
# graph = Graph.from_file("PA_2020_vtds.zip", ignore_errors = True)
print("graph created")
print("num nodes:",graph.number_of_nodes())

# initial_partition = Partition(graph, "incumbent", {node: graph.nodes[node]["INCUMBENT"] for node in graph.nodes})
initial_partition = Partition(
    graph,
    assignment="DISTRICT",
    updaters={
        "cut_edges": cut_edges,
        "population": Tally("Tot_2020_vap", alias="population")
        
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
    2*len(initial_partition["cut_edges"])
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
    total_steps=1000
)
count = 0
# test = gpd.read_file("md_2020_complete.json",encoding='latin1')
# test['NEIGHBORS'] = test['NEIGHBORS'].apply(lambda x: ", ".join(x))
# test = test.to_crs(4326)
# test.to_file('md_2020_reproj.json', driver="GeoJSON")
for partition in chain:
    if(count == 0):
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
    for i in range(len(temp.nodes)):
        node_in_geo = precincts[precincts['GEOID20'] == temp.nodes[i]['GEOID20']].iloc[0]
        if(partition.assignment[i] != node_in_geo.DISTRICT):
            print(temp.nodes[i]['GEOID20'], "moved")
            node_in_geo.DISTRICT = partition.assignment[i]
    precincts['NEIGHBORS'] = precincts['NEIGHBORS'].apply(lambda x: ", ".join(x))
    precincts.to_file("GeneratedPlan"+str(count)+".json")
    count+=1
    if count > 3: break
    # temp.to_json("test.json")
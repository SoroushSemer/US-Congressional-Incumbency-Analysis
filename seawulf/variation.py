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

FILENAME = "./final/Arizona/az_2020_precincts.json"
FILENAME2 = "./final/Arizona/az_2022_precincts.json"

precincts2020 = gpd.read_file(FILENAME)
precincts2020['Tot_2020_vap'] = precincts2020['Tot_2020_vap'].astype(int)
precincts2020['AREA'] = precincts2020['AREA'].astype(int)

precincts2022 = gpd.read_file(FILENAME2)
precincts2022['Tot_2022_vap'] = precincts2022['Tot_2022_vap'].astype(int)
precincts2022['AREA'] = precincts2022['AREA'].astype(int)

for i in range(1,10):
    precincts1_2020 = set(precincts2020.loc[precincts2020["DISTRICT"] == "0"+str(i), 'GEOID20'])
    precincts1_2022 = set(precincts2022.loc[precincts2020["DISTRICT"] == "0"+str(i), 'VTD'])

    b = precincts1_2022 - precincts1_2020

    denom = precincts2020.loc[precincts2020["DISTRICT"] == "0"+str(i), 'Tot_2020_vap'].sum()

    num = precincts2022.loc[precincts2022["VTD"].isin(b), 'Tot_2022_vap'].sum()

    print(num/denom)

    denom = precincts2020.loc[precincts2020["DISTRICT"] == "0"+str(i), 'AREA'].sum()

    num = precincts2022.loc[precincts2022["VTD"].isin(b), 'AREA'].sum()

    print(num/denom)
    print()

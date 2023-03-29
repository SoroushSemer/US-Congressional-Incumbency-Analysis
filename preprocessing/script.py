# 2 files
# One file for Precincts and all their demographic and incumbent data
# Another is district and it states what precincts are in it for that year

import geopandas as gpd
import pandas as pd
import maup

from shapely.ops import unary_union
from shapely.geometry import Point
from shapely.geometry import Polygon

# Read CSV with Pandas
# demographics = pd.read_csv("2020_census_MD-3.csv")
# Read Shapefile with Geopandas
precincts2020 = gpd.read_file("./Maryland2020/tl_2020_24_vtd20.shp") # GEOID20
precincts2022 = gpd.read_file("./Maryland2022/Maryland_Election_Boundaries_-_Precincts_2022.geojson") # VTD
precincts2022["NEIGHBORS"] = False

# for index, row in precincts2020.iterrows():
#     # get 'not disjoint' countries   
#     neighbors = precincts2020[~precincts2020.geometry.disjoint(country.geometry)].NAME20.tolist()

#     # remove own name of the country from the list
#     neighbors = [ name for name in neighbors if country.NAME20 != name ]

#     # add names of neighbors as NEIGHBORS value
#     precincts2020.at[index, "NEIGHBORS"] = ", ".join(neighbors)
   
# save GeoDataFrame as a new file
# precincts2020.to_file("newfile.shp")

# Make buffer, check intersection and distance from geometry to current selected precinct geometry

#precincts2020 = precincts2020.to_crs(crs=26910) 
# print(precincts2022)
# for index, row in precincts2022.iterrows():
#     print(row['geometry'].boundary)
#     break
# for index, row in precincts2020.iterrows():  
#     # neighbors = precincts2020[precincts2020.geometry.touches(row['geometry'])].GEOID20.tolist() 
#     neighbors = precincts2020[precincts2020.geometry.touches(row['geometry'])]
#     neighbors = neighbors[neighbors.geometry.distance(row['geometry']) <= 60.96]
#     # print(precincts2020[precincts2020.geometry.touches(row['geometry'])])
#     if row.GEOID20 in neighbors:
#         neighbors = neighbors.remove(row.GEOID20)
#     # print(row.GEOID20)
#     precincts2020.at[index, "NEIGHBORS"] = ", ".join(neighbors.GEOID20)
#     print(neighbors.GEOID20)

# # Save old CRS in case needed
# oldCRS = precincts2020.crs
# oldData = precincts2020.copy(True)
# # Change CRS from degrees to meters
# precincts2020 = precincts2020.to_crs(crs=26910) 
# # Buffer all geometries by 60.96 meters = 200 ft
# precincts2020_buffered = precincts2020.copy(True)
# precincts2020_buffered['geometry'] = precincts2020_buffered['geometry'].buffer(60.96)


# for index, row in precincts2020_buffered.iterrows():  
#     other_geoms = precincts2020[precincts2020['GEOID20'] != row['GEOID20']].geometry.tolist()
#     union_geom = unary_union(other_geoms)
#     intersect_geom = row['geometry'].intersection(union_geom)
    
#     # Create a point within the intersected geometry to use for spatial join
#     if intersect_geom.geom_type == 'Polygon':
#         point = Point(intersect_geom.representative_point())
#     else:
#         point = Point(intersect_geom.centroid)

#     neighbors = gpd.sjoin(precincts2020, gpd.GeoDataFrame(geometry=[point], crs=26910), op='intersects', how='inner')   
#     # Filter the neighbors based on shared boundary distance
#     neighbors = neighbors[neighbors.GEOID20 != row['GEOID20']]
#     # neighbors = neighbors[neighbors.geometry.touches(row['geometry'])]
#     print(neighbors) 
#     print(neighbors.geometry.touches(row['geometry'])) 

#     # # Filter the neighbors based on edge distance
#     # neighbors = neighbors[neighbors.geometry.distance(row['geometry']) <= 60.96]

#     # print(neighbors.GEOID20.tolist())

def calculate_neighbors(gdf, prec):
    '''
    Function that takes a GDF and uses whatever the key the precinct is attached to in the file
    to figure out neighbors
    '''    
    # CRS conversion from degrees to meters
    gdf = gdf.to_crs(3857)
    # Keep a copy and add a buffer of 60.96 meters = 200ft to the geometry 
    gdf_buffer = gdf.copy(deep=True)
    gdf_buffer['geometry'] = gdf.buffer(60.96)
    
    # Intersect the buffered GDF with normal GDF
    check_intersect = gpd.overlay(gdf_buffer, gdf, how='intersection')
    # Create a tuple of zips of the prec pairs present in intersection
    check_intersect_tuples = tuple(zip(check_intersect[prec + '_1'], check_intersect[prec + '_2']))
    
    # Define a dictionary that will map from a prec value to a list of other prec it is adjacent to
    res = {}
    for val in check_intersect_tuples:
        # remove self intersecting tuples
        if val[0] != val[1]:
            # If the shape is already in the dict
            if val[0] in list(res.keys()):
                # Append adj regions to list
                holder = res[val[0]]
                holder.append(val[1])
                res[val[0]] = holder
            else:
                # Otherwise create key in dict and map to a list with adj regions
                res[val[0]] = [val[1]]
                
    # Some regions only intersect with themselves so no need to add 
    for val in [i for i in gdf[prec] if i not in list(res.keys())]:
        # Add a empty list for these self intersecters
        res[val] = []    
    return res

def insert_neighbors(gdf, neigh):
    '''
    Inserts neighbors into GDF
    '''
    for key in neigh:
        gdf.loc[gdf['VTD'] == key, 'NEIGHBORS'] = ", ".join(neigh[key])
def insert_demographic(gdf, demo):
    return
# There exists 2 rows that have bad data but geometries that work
# print(precincts2022[precincts2022['VTD'].isnull()])
precincts2022 = precincts2022.dropna()
precincts2022 = precincts2022.reset_index(drop=True)
neighbors = calculate_neighbors(precincts2022, 'VTD')
insert_neighbors(precincts2022, neighbors)

print(precincts2022)
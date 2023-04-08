import geopandas as gpd
import pandas as pd
import maup

from shapely.ops import unary_union
from shapely.geometry import Point
from shapely.geometry import Polygon

# CSV Files for each state and each year, holding data
# for demographics and incumbency

# Maryland
md_demo_raceAge_20 = pd.read_csv("./Maryland/2020/MD2020_VAP for each race.csv")

# Louisana

# Arizona 

# Shapefile/GeoJSON files converted to geoDataFrames to be edited
# for each state and each year

# Maryland
# md_2020 = gpd.read_file("./Maryland2020/tl_2020_24_vtd20.shp") # GEOID20
md_2020 = gpd.read_file("./Maryland/2020/tl_2020_24_vtd20.shp") # GEOID20
md_2022 = gpd.read_file("./Maryland/2022/MD2022_Precincts.geojson") # VTD
md_2022['NEIGHBORS'] = False


# Louisana

# Arizona 

def clean_table(gdf):
    '''
    Clean geometries with Maup and clean out bad entries from GDF
    '''
    return

def calculate_neighbors(gdf, prec): # Check this over 
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

def insert_neighbors(gdf, neigh, tag):
    '''
    Inserts neighbors into GDF by tag. Tag is column name for precinct id. 
    '''
    for key in neigh:
        gdf.loc[gdf[tag] == key, 'NEIGHBORS'] = ", ".join(neigh[key])

def drop_columns(gdf):
    '''
    Drop columns from gdf that we do not care about. Usually only need geometries and
    precinct ids. May keep precinct names as well.  
    '''
    return

def insert_demographic(gdf, demo_file, tag):
    '''
    Function to enter a specfic demographic stat into the GDF from a file
    '''
    # print(gdf)

    # print(demo_file.head())

    # Merge the CSV and GDF on tag
    # mergedData = pd.merge(
    # gdf,
    # demo_file,
    # on=tag)

    # mergedData = mergedData[['GEOID20', 'geometry']]
    # print(mergedData.head())
    return

def aggregate_data(gdf, src):
    '''
    Function to aggregate data to precinct level. Should use Maup methods
    '''
    return

def generate_GEOJSON(gdf, filename):
    '''
    Function to generate the GEOJSON from the GDF that is given.  
    '''
    return


# ------------------TESTING/GENERATION--------------------#

# There exists 2 rows that have bad data but geometries that work
# print(precincts2022[precincts2022['VTD'].isnull()])
# md_2022 = md_2022.dropna()
# md_2022 = md_2022.reset_index(drop=True)
# neighbors = calculate_neighbors(md_2022, 'VTD')
# insert_neighbors(md_2022, neighbors, 'VTD')

# print(md_2022)

insert_demographic(md_2020, md_demo_raceAge_20, 'GEOID20')

test = gpd.read_file("./Test/md_vest_20.shp")
print(test)
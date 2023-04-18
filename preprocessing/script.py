import geopandas as gpd
import pandas as pd
import maup

# CSV Files for each state and each year, holding data
# for demographics and incumbency

# Maryland
#---2020---#
md_demo_20 = pd.read_csv("./Maryland/2020/MD2020_VAP for each race.csv")
md_adj_20 = pd.read_csv("./Maryland/2020/md_vtd_2020_rook_adjacency.csv")

#---2022---#

# Shapefile/GeoJSON files converted to geoDataFrames to be edited
# for each state and each year

# Maryland
#---2020---#
md_2020 = gpd.read_file("./Maryland/2020/md_2020.json") # GEOID20
md_2020_districts = gpd.read_file("./Maryland/2020/md_2020_districts.json") 
#---2022---#
md_2022 = gpd.read_file("./Maryland/2022/MD2022_Precincts.geojson") # VTD

def clean_table(gdf):
    '''
    Clean geometries with Maup and clean out bad entries from GDF. Keep valid columns like name, geometry, and id
    '''
    # CURRENTLY IMPLEMENTED FOR MARYLAND. WILL MAKE 2 OTHER SCRIPTS FOR OTHER STATES

    # Iterate over the column names and only keep certain ones

    # Change CRS first
    gdf = gdf.to_crs(3857)

    for col in gdf.columns:
        # Tags we want from Maryland
        if col != 'GEOID20' and col != 'NAMELSAD20' and col != 'geometry': 
            gdf.drop(col, axis=1, inplace=True)

    # Close gaps and clean up overlaps
    gdf['geometry'] = maup.close_gaps(gdf['geometry']) 
    gdf['geometry'] = maup.resolve_overlaps(gdf['geometry'])
    return gdf

def calculate_neighbors(gdf, prec): 
    '''
    Function that takes a GDF and uses whatever the key the precinct is attached to in the file
    to figure out neighbors then inserts it into gdf. Returns modified gdf
    '''    
    # Make column for neighbors
    gdf['NEIGHBORS'] = False
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
    
    # Insert neighbors into gdf from res list
    for key in res:
        gdf.loc[gdf[prec] == key, 'NEIGHBORS'] = ", ".join(res[key])
    
    return gdf

def insert_demographic(gdf, demo_file, tag):
    '''
    Function to enter a specfic demographic stat into the GDF from a file
    '''
    for col in demo_file.columns:
        # Tags we want from demographic
        if "_vap" not in col and col != "GEOID20": 
            demo_file.drop(col, axis=1, inplace=True)
    # Merge the CSV and GDF on tag (Here being GEOID20)
    gdf = pd.merge(gdf, demo_file, on=tag)
    return gdf

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
def insert_district(gdf, districts):
    '''
    Function to assign precincts to Congressional districts. Use maup.assign
    '''
    # Convert to meters 
    districts = districts.to_crs(3857)
    # Assign precincts to districts
    assignment = maup.assign(gdf['geometry'], districts['geometry'])
    # Convert to correct ids
    for index, item in assignment.items():
        assignment[index] = f"0{item + 1}"
    # Add to gdf
    gdf['DISTRICT'] = assignment 
    return gdf


# ------------------GENERATION--------------------#

# There exists 2 rows that have bad data but geometries that work
# print(precincts2022[precincts2022['VTD'].isnull()])
# md_2022 = md_2022.dropna()
# md_2022 = md_2022.reset_index(drop=True)
# neighbors = calculate_neighbors(md_2022, 'VTD')
# insert_neighbors(md_2022, neighbors, 'VTD')

# print(md_2022)

# insert_demographic(md_2020, md_demo_raceAge_20, 'GEOID20')

# test2 = gpd.read_file("./Louisiana/2020/la_pl2020_cd.shp")
# test3 = gpd.read_file("./Arizona/2020/az_vtd_2020_bound.shp")

# print(test2)
# print(test3)

# print(gdf['geometry'])
# print(gdf.loc[:, 'geometry'])
# Create 2020 complete dataframe
md_2020 = clean_table(md_2020)
md_2020 = insert_district(md_2020, md_2020_districts)
md_2020 = insert_demographic(md_2020, md_demo_20, 'GEOID20')
md_2020.to_file('TEST.json', driver="GeoJSON")
print(md_2020.head())

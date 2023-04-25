import geopandas as gpd
import pandas as pd
import maup
import math

''' CSV Files holding data for demographics and incumbency for each year '''
az_demo_20 = pd.read_csv("./Arizona/2020/AZ2020_VAP for each race.csv")
az_adj_20 = pd.read_csv("./Arizona/2020/az_vtd_2020_rook_adjacency.csv")
az_incumbent = pd.read_csv("./Arizona/2022/az_2022_primary_cand_data.csv")

''' Shapefile/GeoJSON files converted to geoDataFrames to be edited '''
az_2020_precincts = gpd.read_file("./Arizona/2020/2020.zip!az_2020_precincts.json") 
az_2020_districts = gpd.read_file("./Arizona/2020/2020.zip!az_2020_districts.json") 

az_2022_precincts = gpd.read_file("./Arizona/2020/2020.zip!az_2020_precincts.json")
az_2022_districts = gpd.read_file("./Arizona/2022/az_2022_districts.json")

def clean_table(gdf, key_arr):
    '''
    Clean geometries with Maup and clean out bad entries from GDF. Keep valid columns like name, geometry, and id
    '''
    gdf = gdf.dropna()
    gdf = gdf.reset_index(drop=True)
    gdf = gdf.to_crs(3857)                                                    # Change CRS first to meters
    for col in gdf.columns:
        if col not in key_arr:                                                # Tags we want from Maryland
            gdf.drop(col, axis=1, inplace=True)

    gdf['geometry'] = maup.close_gaps(gdf['geometry'])                        # Close gaps and clean up overlaps
    # gdf['geometry'] = maup.resolve_overlaps(gdf['geometry'])
    return gdf

def calculate_neighbors(gdf, prec): 
    '''
    Function that takes a GDF and uses whatever the key the precinct is attached to in the file
    to figure out neighbors then inserts it into gdf. Returns modified gdf
    '''    
    gdf['NEIGHBORS'] = False
    gdf = gdf.to_crs(3857)                                                                            # CRS conversion from degrees to meters
    gdf_buffer = gdf.copy(deep=True)                                                                  # Keep a copy and add a buffer of 60.96 meters = 200ft to the geometry 
    gdf_buffer['geometry'] = gdf.buffer(60.96) 
    check_intersect = gpd.overlay(gdf_buffer, gdf, how='intersection')                                # Intersect the buffered GDF with normal GDF
    check_intersect_tuples = tuple(zip(check_intersect[prec + '_1'], check_intersect[prec + '_2']))   # Create a tuple of zips of the prec pairs present in intersection

    res = {}                                                                                          # Define a dictionary that will map from a prec value to a list of other prec it is adjacent to
    for val in check_intersect_tuples:
        if val[0] != val[1]:                                                                          # remove self intersecting tuples
            if val[0] in list(res.keys()):                                                            # If the shape is already in the dict, append adj regions to list
                holder = res[val[0]]
                holder.append(val[1])
                res[val[0]] = holder
            else:
                res[val[0]] = [val[1]]                                                                # Otherwise create key in dict and map to a list with adj regions
    for val in [i for i in gdf[prec] if i not in list(res.keys())]:                                   # Some regions only intersect with themselves so no need to add 
        res[val] = []                                                                                 # Add a empty list for these self intersecters
    for key in res:                                                                                   # Insert neighbors into gdf from res list
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
    pieces = maup.intersections(src, gdf, area_cutoff=0)
    # print(pieces)
    columns = ['Tot_2020_vap', 'Wh_2020_vap', 'His_2020_vap', 'BlC_2020_vap', 'NatC_2020_vap', 'AsnC_2020_vap', 'PacC_2020_vap']
    weights = src['Tot_2020_vap']
    weights = maup.normalize(weights, level=0)
    gdf[columns] = maup.prorate(pieces, src[columns], weights=weights)
    return gdf

def calc_demographic(gdf, src):
    '''
    Function to calculate 2022 demographic data
    '''
    # test = gpd.read_file("./Test/la_cvap_2020_2020_b.shp") 
    # print(test) 

    columns = ['Tot_2020_vap', 'Wh_2020_vap', 'His_2020_vap', 'BlC_2020_vap', 'NatC_2020_vap', 'AsnC_2020_vap', 'PacC_2020_vap']
    new_columns = ['Tot_2022_vap', 'Wh_2022_vap', 'His_2022_vap', 'BlC_2022_vap', 'NatC_2022_vap', 'AsnC_2022_vap', 'PacC_2022_vap']
    gdf[new_columns] = False

    for old_id in src['GEOID20']:
        pop_val = []
        for tag in columns:
            pop_val.append(src.loc[src['GEOID20'] == old_id, tag].iloc[0])
        for i in range(len(pop_val)):
            gdf.loc[gdf['GEOID20'] == old_id, new_columns[i]] = pop_val[i]
    
    return gdf

def insert_district(gdf, districts):
    '''
    Function to assign precincts to Congressional districts. Use maup.assign
    '''
    districts = districts.to_crs(3857)                                     # Convert to meters 
    assignment = maup.assign(gdf['geometry'], districts['geometry'])       # Assign precincts to districts
    for index, item in assignment.items():                                 # Convert to correct ids by adding and adjusting a 0
        if not math.isnan(item):
            assignment[index] = f"0{int(item) + 1}" 

    gdf['DISTRICT'] = assignment 
    return gdf

def insert_incumbent(tab_2020, tab_2022, tab_incumbent):
    columns = ['HOME_PRECINCT', 'INCUMBENT', 'PARTY']
    incumbent_columns = ['Candidate', 'Party']
    tab_2020[columns] = False
    tab_2022[columns] = False
    incumbent_only = tab_incumbent[tab_incumbent['Incumbent'] == 'Yes']    # New dataframe with only incumbents 
    columns = columns[1:] 
    home_set = False

    for dist_id in incumbent_only['District']:
        incumbent_val = []
        for tag in incumbent_columns:
            incumbent_val.append(incumbent_only.loc[incumbent_only['District'] == dist_id, tag].iloc[0])
        for i in range(len(incumbent_val)):
            if not home_set:
                home_20_id = tab_2020.loc[tab_2020['DISTRICT'] == f'0{dist_id}'].iloc[0]['GEOID20']
                tab_2020.loc[tab_2020['GEOID20'] == home_20_id, 'HOME_PRECINCT'] = True
                tab_2022.loc[tab_2022['GEOID20'] == home_20_id, 'HOME_PRECINCT'] = True
                home_set = True
            tab_2020.loc[tab_2020['DISTRICT'] == f'0{dist_id}', columns[i]] = incumbent_val[i]
            tab_2022.loc[tab_2022['DISTRICT'] == f'0{dist_id}', columns[i]] = incumbent_val[i]
        home_set = False
    
    return tab_2020, tab_2022


# ------------------GENERATION--------------------#

''' Create and generate 2020 and 2022 complete json '''
az_2020_precincts = clean_table(az_2020_precincts, ['GEOID20', 'NAMELSAD20', 'geometry'])
az_2020_precincts = insert_district(az_2020_precincts, az_2020_districts)
az_2020_precincts = insert_demographic(az_2020_precincts, az_demo_20, 'GEOID20')
az_2020_precincts = pd.merge(az_2020_precincts, az_adj_20, on='GEOID20')
az_2020_precincts = az_2020_precincts.rename(columns={"ADJ_GEOMS": "NEIGHBORS"})

az_2022_precincts = clean_table(az_2022_precincts, ['GEOID20', 'NAMELSAD20', 'geometry'])
az_2022_precincts = insert_district(az_2022_precincts, az_2022_districts)
az_2022_precincts = insert_demographic(az_2022_precincts, az_demo_20, 'GEOID20')
az_2022_precincts = pd.merge(az_2022_precincts, az_adj_20, on='GEOID20')
az_2022_precincts = az_2022_precincts.rename(columns={"ADJ_GEOMS": "NEIGHBORS"})
az_2020_precincts, az_2022_precincts = insert_incumbent(az_2020_precincts, az_2022_precincts, az_incumbent)

print(az_2020_precincts.head())
print(az_2022_precincts.head())

# az_2020_precincts.to_file('az_2020_final.json', driver="GeoJSON")
# az_2022_precincts.to_file('az_2022_final.json', driver="GeoJSON")
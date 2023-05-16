import geopandas as gpd
import pandas as pd
import maup
import math
import warnings

from shapely.errors import ShapelyDeprecationWarning

# Ignore Shapely deprecation warnings
warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)

''' CSV Files holding data for demographics and incumbency for each year '''
la_demo_20 = pd.read_csv("./Louisiana/2020/LA2020_VAP for each race.csv")
la_adj_20 = pd.read_csv("./Louisiana/2020/la_vtd_official_2020_rook_adjacency.csv")
la_incumbent = pd.read_csv("./Louisiana/2022/la_2022_primary_cand_data.csv")
la_votes = pd.read_csv("./Louisiana/2020/2020_election_LA-1.csv")

''' Shapefile/GeoJSON files converted to geoDataFrames to be edited '''
la_2020_precincts = gpd.read_file("./Louisiana/2020/2020.zip!la_2020_precincts.json") 
la_2020_districts = gpd.read_file("./Louisiana/2020/2020.zip!la_2020_districts.json") 

la_2022_precincts = gpd.read_file("./Louisiana/2022/2022.zip!la_2022_precincts.json")
la_2022_districts = gpd.read_file("./Louisiana/2022/2022.zip!la_2022_districts.json")

def clean_table(gdf, key_arr):
    '''
    Clean geometries with Maup and clean out bad entries from GDF. 
    Keep valid columns like name, geometry, and id. Give it an area column.
    '''
    gdf = gdf.dropna()
    gdf = gdf.reset_index(drop=True)
    gdf = gdf.to_crs(3857)                                                    # Change CRS first to meters
    for col in gdf.columns:
        if col not in key_arr:                                                # Tags we want from Maryland
            gdf.drop(col, axis=1, inplace=True)

    gdf['geometry'] = maup.close_gaps(gdf['geometry'])                        # Close gaps and clean up overlaps
    # gdf['geometry'] = maup.resolve_overlaps(gdf['geometry'])
    gdf['AREA'] = gdf.area
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
    Function to enter a specfic demographic stat into the GDF from a file using a id/tag
    '''
    for col in demo_file.columns:
        if "_vap" not in col and col != "GEOID20": 
            demo_file.drop(col, axis=1, inplace=True)

    gdf = pd.merge(gdf, demo_file, on=tag)
    return gdf

def aggregate_data(gdf, src):
    '''
    Function to aggregate data to precinct level. Should use Maup methods
    '''
    pieces = maup.intersections(src, gdf, area_cutoff=0)
    print(pieces)
    columns = ['Tot_2020_vap', 'Wh_2020_vap', 'His_2020_vap', 'BlC_2020_vap', 'NatC_2020_vap', 'AsnC_2020_vap', 'PacC_2020_vap']
    weights = src['Tot_2020_vap']
    weights = maup.normalize(weights, level=0)
    gdf[columns] = maup.prorate(pieces, src[columns], weights=weights)
    return gdf

def calc_demographic(gdf, src):
    '''
    Function to calculate 2022 demographic data
    '''
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
    '''
    Function to insert the incumbent of a particular precinct into the gdf of both years. 
    '''
    columns = ['HOME_PRECINCT', 'INCUMBENT', 'PARTY']
    incumbent_columns = ['Candidate', 'Party']
    tab_2020[columns] = False
    tab_2022[columns] = False
    incumbent_only = tab_incumbent[tab_incumbent['Incumbent'] == 'Yes']    # New dataframe with only incumbents 
    columns = columns[1:] 

    for dist_id in incumbent_only['District']:
        incumbent_val = []
        for tag in incumbent_columns:
            incumbent_val.append(incumbent_only.loc[incumbent_only['District'] == dist_id, tag].iloc[0])
        for i in range(len(incumbent_val)):
            tab_2020.loc[tab_2020['DISTRICT'] == f'0{dist_id}', columns[i]] = incumbent_val[i]
            tab_2022.loc[tab_2022['DISTRICT'] == f'0{dist_id}', columns[i]] = incumbent_val[i]

        home_20_index = round(len(tab_2020.loc[tab_2020['DISTRICT'] == f'0{dist_id}']) / 2)
        home_20_id = tab_2020.iloc[home_20_index]['GEOID20']
        tab_2020.loc[tab_2020['GEOID20'] == home_20_id, 'HOME_PRECINCT'] = True
        tab_2022.loc[tab_2022['GEOID20'] == home_20_id, 'HOME_PRECINCT'] = True
    
    return tab_2020, tab_2022

def insert_votes(gdf_20, gdf_22):
    '''
    Function to insert the votes of a particular precinct into the gdf of both years. 
    '''
    columns = ['REP Votes', 'DEM Votes']
    gdf_20[columns] = False
    gdf_22[columns] = False 

    for prec_id in gdf_20['GEOID20']:
        data_reported = la_votes.loc[(la_votes['GEOID20'] == prec_id)]                         # Check if precinct reported voting
        if not data_reported.empty:
            rep_votes_20 = data_reported['R_2020_sen'].iloc[0]
            dem_votes_20 = data_reported['D_2020_sen'].iloc[0]
            gdf_20.loc[gdf_20['GEOID20'] == prec_id, 'REP Votes'] = int(rep_votes_20)
            gdf_20.loc[gdf_20['GEOID20'] == prec_id, 'DEM Votes'] = int(dem_votes_20)

    for prec_id in gdf_22['GEOID20']:
        data_reported = la_votes.loc[(la_votes['GEOID20'] == prec_id)]
        if not data_reported.empty:
            rep_votes_22 = data_reported['R_2020_pres'].iloc[0]
            dem_votes_22 = data_reported['D_2020_pres'].iloc[0]
            gdf_22.loc[gdf_22['GEOID20'] == prec_id, 'REP Votes'] = int(rep_votes_22)
            gdf_22.loc[gdf_22['GEOID20'] == prec_id, 'DEM Votes'] = int(dem_votes_22)

    return gdf_20, gdf_22

def clean_districts(district, tab_incumbent, precs, p_id, demo_columns):
    '''
    Function to clean a district json and insert incumbent, color, and total population
    '''
    key_arr = ['DISTRICT', 'geometry']
    columns = ['COLOR', 'INCUMBENT', 'PARTY']
    incumbent_columns = ['Candidate', 'Party']
    vote_columns = ['REP Votes', 'DEM Votes']

    district = district.to_crs(3857)

    for col in district.columns:
        if col not in key_arr:                                               
            district.drop(col, axis=1, inplace=True)
    colors = ['red', 'blue', 'green', 'yellow', 'cyan', 'magenta', 'purple', 'orange']
    district['AREA'] = district.area
    district[columns] = False
    columns = columns[1:]
    
    color_index = 1
    for dist_id in district['DISTRICT']:
        district.loc[district['DISTRICT'] == f'0{color_index}', 'COLOR'] = colors[color_index - 1] 
        color_index = color_index + 1

    incumbent_only = tab_incumbent[tab_incumbent['Incumbent'] == 'Yes']
    for dist_id in incumbent_only['District']:
        incumbent_val = []
        for tag in incumbent_columns:
            incumbent_val.append(incumbent_only.loc[incumbent_only['District'] == dist_id, tag].iloc[0])
        for i in range(len(incumbent_val)):
            district.loc[district['DISTRICT'] == f'0{dist_id}', columns[i]] = incumbent_val[i]
    
    district[demo_columns] = False
    for dist_id in district['DISTRICT']:                                                                 # This inserts the population per precinct
        demo_vals = {demo_columns[i]: 0 for i in range(len(demo_columns))}
        for prec_id in precs.loc[precs['DISTRICT'] == dist_id][p_id]:
            for tag in demo_columns:
                demo_vals[tag] = demo_vals[tag] + precs[precs[p_id] == prec_id][tag].iloc[0]
        for vap_key in demo_vals.keys():
            district.loc[district['DISTRICT'] == dist_id, vap_key] = int(demo_vals[vap_key])

    district[vote_columns] = False
    for dist_id in district['DISTRICT']:                                                                 # This inserts the votes per precinct
        vote_vals = {vote_columns[i]: 0 for i in range(len(vote_columns))}
        for prec_id in precs.loc[precs['DISTRICT'] == dist_id][p_id]:
            for tag in vote_columns:
                vote_vals[tag] = vote_vals[tag] + precs[precs[p_id] == prec_id][tag].iloc[0]
        for vote_key in vote_vals.keys():
            district.loc[district['DISTRICT'] == dist_id, vote_key] = int(vote_vals[vote_key])

        
    district = district.to_crs(4326)
    return district

def calculate_variations(data_20, data_22):
    ''' 
    Calculate percentage variations between two GeoDataFrames. 
    '''
# Determine the set of all unique districts
    districts = set(data_20['DISTRICT']).union(data_22['DISTRICT'])

    variations = {}

    for district in districts:
        # Filter data by district
        data_20_district = data_20[data_20['DISTRICT'] == district]
        data_22_district = data_22[data_22['DISTRICT'] == district]

        # Define the sets
        G = set(data_20_district['GEOID20']) - set(data_22_district['GEOID20'])
        B = set(data_22_district['GEOID20']) - set(data_20_district['GEOID20'])
        GBG = set(data_22_district['GEOID20']).intersection(set(data_20_district['GEOID20']))
        
        # Calculate population difference
        Pop_B = data_22_district.loc[data_22_district['GEOID20'].isin(B), 'Tot_2022_vap'].sum()
        Pop_GB_G = data_20_district['Tot_2020_vap'].sum() + data_22_district.loc[data_22_district['GEOID20'].isin(B), 'Tot_2022_vap'].sum()  # Assuming 'data_22_district' is the 2022 district
        pop_difference = Pop_B / Pop_GB_G

        # Calculate area difference
        Area_B = data_22_district.loc[data_22_district['GEOID20'].isin(B), 'AREA'].sum()
        Area_GB_G = data_20_district['AREA'].sum() + Area_B # Assuming 'data_22_district' is the 2022 district
        area_difference = Area_B / Area_GB_G

        # Store the results for this district
        variations[district] = {'pop_difference': pop_difference, 'area_difference': area_difference}

    return variations

''' Create and generate 2020 and 2022 complete json '''
la_2020_precincts = clean_table(la_2020_precincts, ['GEOID20', 'NAMELSAD20', 'geometry'])
la_2020_precincts = insert_district(la_2020_precincts, la_2020_districts)
la_2020_precincts = insert_demographic(la_2020_precincts, la_demo_20, 'GEOID20')
la_2020_precincts = pd.merge(la_2020_precincts, la_adj_20, on='GEOID20')
la_2020_precincts = la_2020_precincts.rename(columns={"Adjacencies": "NEIGHBORS"})

la_2022_precincts = clean_table(la_2022_precincts, ['GEOID20', 'NAMELSAD20', 'geometry'])
la_2022_precincts = insert_district(la_2022_precincts, la_2022_districts)
la_2022_precincts = calc_demographic(la_2022_precincts, la_2020_precincts)
la_2022_precincts = calculate_neighbors(la_2022_precincts, 'GEOID20')

la_2020_precincts, la_2022_precincts = insert_incumbent(la_2020_precincts, la_2022_precincts, la_incumbent)
la_2020_precincts, la_2022_precincts = insert_votes(la_2020_precincts, la_2022_precincts)

la_2020_districts.rename(columns={"CD116FP": "DISTRICT"}, inplace=True)
la_2022_districts.rename(columns={"DISTRICT_I": "DISTRICT"}, inplace=True)
la_2022_districts['DISTRICT'] = '0' + la_2022_districts['DISTRICT'].astype(str)

la_2020_districts = clean_districts(la_2020_districts, la_incumbent, la_2020_precincts, 'GEOID20', ['Tot_2020_vap', 'Wh_2020_vap', 'His_2020_vap', 'BlC_2020_vap', 'NatC_2020_vap', 'AsnC_2020_vap', 'PacC_2020_vap'])
la_2022_districts = clean_districts(la_2022_districts, la_incumbent, la_2022_precincts, 'GEOID20', ['Tot_2022_vap', 'Wh_2022_vap', 'His_2022_vap', 'BlC_2022_vap', 'NatC_2022_vap', 'AsnC_2022_vap', 'PacC_2022_vap'])
# Get unique districts
districts = la_2022_precincts['DISTRICT'].unique()

# Initialize empty DataFrame to store results
results = pd.DataFrame(columns=['DISTRICT', 'pop_var', 'geo_var'])

# Loop through each district
for district in districts:
    # Select data for this district
    data_20_district = la_2020_precincts[la_2020_precincts['DISTRICT'] == district]
    data_22_district = la_2022_precincts[la_2022_precincts['DISTRICT'] == district]

    # Calculate variations
    pop_var, geo_var = calculate_variations(data_20_district, data_22_district)
    
    # Append results to DataFrame
    results = results.append({'DISTRICT': district, 'pop_var': pop_var, 'geo_var': geo_var}, ignore_index=True)

la_2020_precincts = la_2020_precincts.to_crs(4326)
la_2022_precincts = la_2022_precincts.to_crs(4326)

la_2020_precincts['REP Votes'] = la_2020_precincts['REP Votes'].astype(int)
la_2020_precincts['DEM Votes'] = la_2020_precincts['DEM Votes'].astype(int)
la_2022_precincts['REP Votes'] = la_2022_precincts['REP Votes'].astype(int)
la_2022_precincts['DEM Votes'] = la_2022_precincts['DEM Votes'].astype(int)

print(la_2020_precincts.head())
print(la_2022_precincts.head())

print(la_2020_districts)
print(la_2022_districts)

la_2020_precincts.to_file('la_2020_complete.json', driver="GeoJSON")
# la_2022_precincts.to_file('la_2022_complete.json', driver="GeoJSON")

la_2020_districts.to_file('la_2020_districts.json', driver="GeoJSON")
la_2022_districts.to_file('la_2022_districts.json', driver="GeoJSON")

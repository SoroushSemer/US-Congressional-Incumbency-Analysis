import geopandas as gpd
import pandas as pd
import maup
import math

''' CSV Files for Maryland and each year, holding data for demographics and incumbency '''
md_demo_20 = pd.read_csv("./Maryland/2020/MD2020_VAP for each race.csv")
md_adj_20 = pd.read_csv("./Maryland/2020/md_vtd_2020_rook_adjacency.csv")
md_incumbent = pd.read_csv("./Maryland/2022/md_2022_primary_cand_data.csv")
md_votes = pd.read_csv("./Maryland/2020/2020_election_MD-1.csv")

''' Shapefile/GeoJSON files converted to geoDataFrames to be edited '''
md_2020_precincts = gpd.read_file("./Maryland/2020/2020.zip!md_2020_precincts.json") 
md_2020_districts = gpd.read_file("./Maryland/2020/2020.zip!md_2020_districts.json") 

md_2022_precincts = gpd.read_file("./Maryland/2022/2022.zip!MD2022_Precincts.geojson")
md_2022_districts = gpd.read_file("./Maryland/2022/2022.zip!MD2022_Districts.json")

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
    to figure out neighbors then inserts it into gdf. 
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
        if "_vap" not in col and col != tag: 
            demo_file.drop(col, axis=1, inplace=True)

    gdf = pd.merge(gdf, demo_file, on=tag)
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
            gdf.loc[gdf['VTD'] == old_id, new_columns[i]] = int(pop_val[i])
    
    return gdf

def insert_district(gdf, districts):
    '''
    Function to assign precincts to Congressional districts. Uses maup.assign
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
    home_set = False

    for dist_id in incumbent_only['District']:
        incumbent_val = []
        for tag in incumbent_columns:
            incumbent_val.append(incumbent_only.loc[incumbent_only['District'] == dist_id, tag].iloc[0])
        for i in range(len(incumbent_val)):
            if not home_set:
                home_20_id = tab_2020.loc[tab_2020['DISTRICT'] == f'0{dist_id}'].iloc[0]['GEOID20']
                tab_2020.loc[tab_2020['GEOID20'] == home_20_id, 'HOME_PRECINCT'] = True
                tab_2022.loc[tab_2022['VTD'] == home_20_id, 'HOME_PRECINCT'] = True
                home_set = True
            tab_2020.loc[tab_2020['DISTRICT'] == f'0{dist_id}', columns[i]] = incumbent_val[i]
            tab_2022.loc[tab_2022['DISTRICT'] == f'0{dist_id}', columns[i]] = incumbent_val[i]
        home_set = False
    
    return tab_2020, tab_2022

def insert_votes(gdf_20, gdf_22):
    '''
    Function to insert the votes of a particular precinct into the gdf of both years. 
    '''
    columns = ['REP Votes', 'DEM Votes']
    gdf_20[columns] = False
    gdf_22[columns] = False 

    for prec_id in gdf_20['GEOID20']:
        data_reported = md_votes.loc[(md_votes['GEOID20'] == prec_id)]                         # Check if precinct reported voting
        if not data_reported.empty:
            rep_votes_20 = data_reported['R_2018_sen'].iloc[0]
            dem_votes_20 = data_reported['D_2018_sen'].iloc[0]
            gdf_20.loc[gdf_20['GEOID20'] == prec_id, 'REP Votes'] = int(rep_votes_20)
            gdf_20.loc[gdf_20['GEOID20'] == prec_id, 'DEM Votes'] = int(dem_votes_20)

    for prec_id in gdf_22['VTD']:
        data_reported = md_votes.loc[(md_votes['GEOID20'] == prec_id)]
        if not data_reported.empty:
            rep_votes_22 = data_reported['R_2020_pres'].iloc[0]
            dem_votes_22 = data_reported['D_2020_pres'].iloc[0]
            gdf_22.loc[gdf_22['VTD'] == prec_id, 'REP Votes'] = int(rep_votes_22)
            gdf_22.loc[gdf_22['VTD'] == prec_id, 'DEM Votes'] = int(dem_votes_22)

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
    Need to calculate area of districts and precincts. 
    '''
    
    return

''' Create and generate 2020 and 2022 complete json '''
md_2020_precincts = clean_table(md_2020_precincts, ['GEOID20', 'NAMELSAD20', 'geometry'])
md_2020_precincts = insert_district(md_2020_precincts, md_2020_districts)
md_2020_precincts = insert_demographic(md_2020_precincts, md_demo_20, 'GEOID20')
md_2020_precincts = pd.merge(md_2020_precincts, md_adj_20, on='GEOID20')
md_2020_precincts = md_2020_precincts.rename(columns={"ADJ_GEOMS": "NEIGHBORS"})

md_2022_precincts = clean_table(md_2022_precincts, ['VTD', 'NAME', 'geometry'])
md_2022_precincts = insert_district(md_2022_precincts, md_2022_districts)
md_2022_precincts = calc_demographic(md_2022_precincts, md_2020_precincts)
md_2022_precincts = calculate_neighbors(md_2022_precincts, 'VTD')

md_2020_precincts, md_2022_precincts = insert_incumbent(md_2020_precincts, md_2022_precincts, md_incumbent)
md_2020_precincts, md_2022_precincts = insert_votes(md_2020_precincts, md_2022_precincts)

md_2020_districts.rename(columns={"CD116FP": "DISTRICT"}, inplace=True)
md_2020_districts = clean_districts(md_2020_districts, md_incumbent, md_2020_precincts, 'GEOID20', ['Tot_2020_vap', 'Wh_2020_vap', 'His_2020_vap', 'BlC_2020_vap', 'NatC_2020_vap', 'AsnC_2020_vap', 'PacC_2020_vap'])
md_2022_districts = clean_districts(md_2022_districts, md_incumbent, md_2022_precincts, 'VTD', ['Tot_2022_vap', 'Wh_2022_vap', 'His_2022_vap', 'BlC_2022_vap', 'NatC_2022_vap', 'AsnC_2022_vap', 'PacC_2022_vap'])

demo_columns = ['Tot_2022_vap', 'Wh_2022_vap', 'His_2022_vap', 'BlC_2022_vap', 'NatC_2022_vap', 'AsnC_2022_vap', 'PacC_2022_vap']
dist_8 = [849846, 511148, 129138, 109645, 22756, 76654, 1629]
index = 0
for val_8 in dist_8:
    md_2022_districts.loc[md_2022_districts['DISTRICT'] == '08', demo_columns[index]] = int(val_8)
    index = index + 1

md_2020_precincts = md_2020_precincts.to_crs(4326)
md_2022_precincts = md_2022_precincts.to_crs(4326)

md_2020_precincts['REP Votes'] = md_2020_precincts['REP Votes'].astype(int)
md_2020_precincts['DEM Votes'] = md_2020_precincts['DEM Votes'].astype(int)
md_2022_precincts['REP Votes'] = md_2022_precincts['REP Votes'].astype(int)
md_2022_precincts['DEM Votes'] = md_2022_precincts['DEM Votes'].astype(int)

print(md_2020_precincts.head())
print(md_2022_precincts.head())

print(md_2020_districts.head())
print(md_2022_districts.head())

# md_2020_districts.to_file('md_2020_districts.json', driver="GeoJSON")
# md_2022_districts.to_file('md_2022_districts.json', driver="GeoJSON")

md_2020_precincts.to_file('md_2020_precincts.json', driver="GeoJSON")
# md_2022_precincts.to_file('md_2022_complete.json', driver="GeoJSON")


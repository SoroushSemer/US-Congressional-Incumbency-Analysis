# US Congressional Incumbency Analysis

## Project Goals 
- Were some incumbents disadvantaged as a result of the 2022 redistricting? 
- Did the political party most responsible for redistricting unfavorably impact incumbents of 
the opposing party? 

## Technical Goals
- Build a large, complex system that requires teamwork to integrate multiple components
- Use multiple programming styles and languages (JavaScript, Python, and Java)
- Incorporate 
  - Data base design and development 
  - User interface design 
  - Requirements analysis (application domain knowledge) 
  - Algorithmic analysis and mathematical thinking
- Use Data Analysis techniques in performing analysis

## Terminology 
- Population – the population of a region (e.g., state, precinct, etc.) refers to the total population as defined by the US Census Bureau. Some calculations might refer to the voting age population (VAP) or citizen voting age population (CVAP). You can use any measure of population, but it should be done consistently throughout the application. 
- Ensemble – a collection of district plans generated on the SeaWulf. Each such district plan will be random and will be a subset of all of the possible graph partitions that are constrained by the user-specified limits on population equality. 


## Use-case List

### GUI
- Display a pan-able and zoom-able map of the US 
- Select state to display 
- Display the current district plan by default 
- Display incumbent districts on the state map
- Display summary of district plan 
- Display safe seats 
- Display a summary table of incumbents
- Coordinate incumbent table with map.
- Display district detail 
- Display summary of ensembles
- Display incumbent box & whisker data
- Display demographic box & whisker data
- Demography heatmap 
- Display available district plans
- Map view filter
- Compare a sample plan with the current plan on the map
- Display Detailed Election Data for Simulated Elections
- Reset state
- Reset page

### Preprocessing
- Integrate multiple data sources
- Store preprocessed data
- Integrate approved plan with dataset
- Determine the political party that most influenced the 2022 districting in your states 
- Estimate the geolocation of incumbent representatives
- Identify precinct neighbors 
- Generate data files required for SeaWulf processing 
- Store SeaWulf data

### Seawulf Supercomputer
- Server dispatcher
- Run MGGG Recom algorithm on the SeaWulf for SMD 
- Coordinate/aggregate SeaWulf core generated data 
- Calculate incumbent summary data 
- Calculate demographic incumbent summary data 
- Calculate the geometric difference in district plans 
- Calculate the population difference in district plans 
- Calculate the demographic difference in district plans
- Calculate election winners 
- Calculate box & whisker data 
- Identify and store additional random district plans of note 
- Calculate district correspondence between random plan and 2020 plan
- Calculate Republican/Democratic splits for each random district plan 
- Calculate safe representative seats for a random district plan
- Determine incumbent for a random district

## Running the Code
Clone the repository ```git clone https://github.com/SoroushSemer/US-Congressional-Incumbency-Analysis.git```

### Front-end 
- Navigate to the client directory ```cd client/```
- Install the necessary packages ```npm install```
- Start the React Server ```npm start```

### Back-end
- Open the ```server``` directory in a Java Spring supported Code Editor (ie. VS Code)
- Start the Spring server

### Accessing the Website
- Navigate to ```localhost:3000``` on your browser



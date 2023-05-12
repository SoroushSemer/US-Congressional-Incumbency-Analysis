/* 
    Written By: Soroush Semerkant
    Last Updated By: Soroush Semerkant
    Last Update Date: 02/16/2023
*/

import { createContext, useState } from "react";
import api from "./axios/api";
export const GlobalStoreContext = createContext({});

function GlobalStoreContextProvider(props) {
  // THESE ARE ALL THE THINGS OUR DATA STORE WILL MANAGE

  // fill in with store variables
  const [store, setStore] = useState({
    currentState: null,
    currentDistrict: null,
    currentMaps: ["2022 District Plan"],
    currentMapGeoJSONs: [],
    currentMapSubType: ["Incumbent"],
    states: null,
    currentEnsembleAnalysis: "election",
    incumbent: null,
    loading: false,
    currentEnsemble: null,
  });

  //BEGINNNING OF STORE FUNCTIONS: TEMPLATE BELOW
  /*
        store.FUNCTION_NAME = function () {

        }
    */

  store.getCurrentEnsemble = function () {
    console.log("hello");
    if (store.currentState == null) {
      return null;
    }
    async function asyncGetEnsemble() {
      const response = await api.getEnsemble(store.currentState.name);
      if (response.status === 200) {
        console.log(response.data);
        for (const plot of Object.keys(response.data.plots)) {
          var outliers = [];
          var count = 0;
          for (const coords of response.data.plots[plot][1].data) {
            if (count === coords.x) {
              outliers.push(coords);
              count++;
            }
          }
          response.data.plots[plot][1].data = outliers;
        }
        setStore({
          ...store,
          currentEnsemble: response.data,
        });
      }
    }
    asyncGetEnsemble();
  };
  store.setCurrentState = function (state) {
    setStore({ ...store, loading: true });
    for (const map of store.currentMaps) {
      async function asyncGetGeoJSON() {
        // console.log(state.name, map);
        const response = await api.getMap(state, map);
        // const response = await api.getHello();
        console.log(response);
        if (response.status === 200) {
          let geojson = response.data;
          console.log(response);
          var currentMapGeoJSONs = store.currentMapGeoJSONs;
          currentMapGeoJSONs.push(geojson);

          setStore({
            ...store,
            currentDistrict: null,
            currentMapGeoJSONs: currentMapGeoJSONs,
            loading: false,
          });

          async function asyncGetState() {
            // console.log(state.name, map);
            const response = await api.getState(state);
            // const response = await api.getHello();
            console.log(response);
            if (response.status === 200) {
              setStore({
                ...store,
                currentState: response.data,
              });
            }
            // console.log(store);
          }
          asyncGetState();
        }
      }
      asyncGetGeoJSON();
    }
  };

  store.setCurrentDistrict = function (district) {
    if (district === store.currentDistrict) {
      district = null;
    }
    setStore({
      ...store,
      currentState: store.currentState,
      currentDistrict: district,
    });
  };

  store.getCurrentIncumbent = function () {
    if (store.currentDistrict == null || store.currentState == null) {
      return null;
    }
    var incumbentInfo = null;
    for (const incumbent of store.currentState.incumbents) {
      if (incumbent.name === store.currentDistrict) {
        incumbentInfo = { ...incumbent };
      }
    }
    if (store.currentMapGeoJSONs.length > 0)
      for (const district of store.currentMapGeoJSONs[0].features) {
        if (district.properties.INCUMBENT === store.currentDistrict) {
          incumbentInfo = { ...incumbentInfo, ...district.properties };
        }
      }
    console.log(incumbentInfo);
    return incumbentInfo;
  };

  store.getPlanInfo = function () {
    if (store.currentState == null || store.currentMapGeoJSONs.length === 0) {
      return null;
    }
    var planInfo = {
      name: store.currentMaps[0],
      districts: 0,
      rep: 0.0,
      dem: 0.0,
      incumbents: 0,
      summary: store.currentMapGeoJSONs[0].summary,
    };
    for (const district of store.currentMapGeoJSONs[0].features) {
      planInfo.districts++;
      if (
        parseInt(district.properties["REP Votes"]) >
        parseInt(district.properties["DEM Votes"])
      ) {
        planInfo.rep += 1;
      } else {
        planInfo.dem += 1;
      }
      if (
        district.properties["PARTY"] !== "N/A" &&
        district.properties["INCUMBENT"] !== "0"
      ) {
        planInfo.incumbents++;
      }
    }
    return planInfo;
  };

  store.getIncumbent = function (district) {
    if (district == null || store.currentState == null) {
      return null;
    }
    for (const incumbent of store.currentState.incumbents) {
      if (incumbent.name === district) {
        return incumbent;
      }
    }
    return null;
  };

  store.toggleMap = function (mapId) {
    var newArray = store.currentMaps;
    var newGeoJSONs = store.currentMapGeoJSONs;
    var index = newArray.indexOf(mapId);

    if (index < 0) {
      newArray.push(mapId);
      setStore({
        ...store,
        currentDistrict: null,
        currentMaps: newArray,
        loading: true,
      });
      async function asyncGetGeoJSON() {
        const response = await api.getMap(store.currentState.name, mapId);
        if (response.status === 200) {
          let geojson = response.data;
          console.log(response);
          newGeoJSONs.push(geojson);
          setStore({
            ...store,
            currentDistrict: null,
            currentMaps: newArray,
            currentMapGeoJSONs: newGeoJSONs,
            loading: false,
          });
        }
      }
      asyncGetGeoJSON();
    } else {
      newArray.splice(index, 1);
      newGeoJSONs.splice(index, 1);
      setStore({
        ...store,
        currentMaps: newArray,
        currentMapGeoJSONs: newGeoJSONs,
      });
    }
  };
  store.clearMaps = function () {
    setStore({
      ...store,
      currentMaps: [],
      // currentMapSubType: ["Incumbent"],
      currentMapGeoJSONs: [],
    });
  };
  store.getMap = function (mapId) {
    var index = store.currentMaps.indexOf(mapId);
    return index;
  };
  store.toggleMapSubType = function (subtype) {
    setStore({ ...store, currentMapSubType: [subtype] });
  };
  store.clearMapSubType = function () {
    setStore({ ...store, currentMapSubType: ["Incumbent"] });
  };
  store.getMapSubType = function (subtype) {
    var index = store.currentMapSubType.indexOf(subtype);
    return index;
  };

  store.getMapGeoJSON = function (state, map) {
    async function asyncGetStates() {
      const response = await api.getMap(state, map);
      if (response.status === 200) {
        let states = response.data;
        // console.log(states);
        setStore({ ...store, states: states });
      }
    }
    asyncGetStates();
  };
  store.setCurrentEnsembleAnalysis = function (ensembleAnalysis) {
    setStore({ ...store, currentEnsembleAnalysis: ensembleAnalysis });
  };

  //should not need to edit below
  return (
    <GlobalStoreContext.Provider
      value={{
        store,
      }}
    >
      {props.children}
    </GlobalStoreContext.Provider>
  );
}
export default GlobalStoreContext;
export { GlobalStoreContextProvider };

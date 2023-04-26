/* 
    Written By: Soroush Semerkant
    Last Updated By: Soroush Semerkant
    Last Update Date: 02/16/2023
*/

import { createContext, useContext, useState } from "react";
import { alignPropType } from "react-bootstrap/esm/types";
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
    currentMapSubType: [],
    states: null,
  });

  //BEGINNNING OF STORE FUNCTIONS: TEMPLATE BELOW
  /*
        store.FUNCTION_NAME = function () {

        }
    */

  store.setCurrentState = function (state) {
    for (const map of store.currentMaps) {
      async function asyncGetGeoJSON() {
        // console.log(state.name, map);
        const response = await api.getMap(state, map);
        // const response = await api.getHello();
        console.log(response);
        if (response.status == 200) {
          let geojson = response.data;
          console.log(response);
          var currentMapGeoJSONs = store.currentMapGeoJSONs;
          currentMapGeoJSONs.push(geojson);

          setStore({
            ...store,
            currentDistrict: null,
            currentMapGeoJSONs: currentMapGeoJSONs,
          });

          async function asyncGetState() {
            // console.log(state.name, map);
            const response = await api.getState(state);
            // const response = await api.getHello();
            console.log(response);
            if (response.status == 200) {
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
    for (const incumbent of store.currentState.incumbents) {
      if (incumbent.district == store.currentDistrict) {
        return incumbent;
      }
    }
    return null;
  };
  store.getIncumbent = function (district) {
    if (district == null || store.currentState == null) {
      return null;
    }
    for (const incumbent of store.currentState.incumbents) {
      if (incumbent.district == district) {
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
      async function asyncGetGeoJSON() {
        const response = await api.getMap(store.currentState.name, mapId);
        if (response.status == 200) {
          let geojson = response.data;
          console.log(response);
          newGeoJSONs.push(geojson);
          setStore({
            ...store,
            currentMaps: newArray,
            currentMapGeoJSONs: newGeoJSONs,
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
      currentMapSubType: [],
      currentMapGeoJSONs: [],
    });
  };
  store.getMap = function (mapId) {
    var index = store.currentMaps.indexOf(mapId);
    return index;
  };
  store.toggleMapSubType = function (subtype) {
    var newArray = store.currentMapSubType;
    var index = newArray.indexOf(subtype);
    if (index < 0) {
      newArray.push(subtype);
      setStore({ ...store, currentMapSubType: newArray });
    } else {
      newArray.splice(index, 1);
      setStore({ ...store, currentMapSubType: newArray });
    }
  };
  store.clearMapSubType = function () {
    setStore({ ...store, currentMapSubType: [] });
  };
  store.getMapSubType = function (subtype) {
    var index = store.currentMapSubType.indexOf(subtype);
    return index;
  };

  store.getMapGeoJSON = function (state, map) {
    async function asyncGetStates() {
      const response = await api.getMap(state, map);
      if (response.status == 200) {
        let states = response.data;
        // console.log(states);
        setStore({ ...store, states: states });
      }
    }
    asyncGetStates();
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

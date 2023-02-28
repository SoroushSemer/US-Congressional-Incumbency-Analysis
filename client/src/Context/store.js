/* 
    Written By: Soroush Semerkant
    Last Updated By: Soroush Semerkant
    Last Update Date: 02/16/2023
*/

import { createContext, useContext, useState } from "react";

export const GlobalStoreContext = createContext({});

function GlobalStoreContextProvider(props) {
  // THESE ARE ALL THE THINGS OUR DATA STORE WILL MANAGE

  // fill in with store variables
  const [store, setStore] = useState({
    currentState: null,
    currentDistrict: null,
  });

  //BEGINNNING OF STORE FUNCTIONS: TEMPLATE BELOW
  /*
        store.FUNCTION_NAME = function () {

        }
    */

  store.setCurrentState = function (state) {
    setStore({ ...store, currentState: state, currentDistrict: null });
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

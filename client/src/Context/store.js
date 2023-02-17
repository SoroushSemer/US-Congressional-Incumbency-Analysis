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
      
    });



    //BEGINNNING OF STORE FUNCTIONS: TEMPLATE BELOW
    /*
        store.FUNCTION_NAME = function () {

        }
    */





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
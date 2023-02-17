/* 
    Written By: Soroush Semerkant
    Last Updated By: Soroush Semerkant
    Last Update Date: 02/16/2023
*/

import "./IncumbentTable.css";

import React, { useContext, useEffect } from "react";
import { GlobalStoreContext } from "../../Context/store";

const IncumbentTable = () => {
  const { store } = useContext(GlobalStoreContext);

  return (
    <div>
      <h2>Scrollable Table</h2>

      <table>
        <tr>
          <th>Incumbent Name</th>
          <th>Political Party</th>
          <th>2022 Election Results</th>
          <th>Geographic Variation</th>
          <th>Population Variations</th>
        </tr>
        {store &&
        store.currentState &&
        store.currentState.incumbents.length > 0 ? (
          store.currentState.incumbents.map((incumbent) => (
            <tr>
              <td>{incumbent.name}</td>
              <td>{incumbent.party}</td>
              <td>{incumbent.electionResult ? "Win" : "Lose"}</td>
              <td>{incumbent.geoVar}</td>
              <td>{incumbent.populationVar}</td>
            </tr>
          ))
        ) : (
          <div />
        )}
      </table>
    </div>
  );
};

export default IncumbentTable;

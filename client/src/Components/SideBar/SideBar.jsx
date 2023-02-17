/* 
    Written By: Soroush Semerkant
    Last Updated By: Soroush Semerkant
    Last Update Date: 02/16/2023
*/

import React, { useContext, useEffect } from "react";
import { GlobalStoreContext } from "../../Context/store";
import IncumbentTable from "../IncumbentTable/IncumbentTable";

const SideBar = () => {
  const { store } = useContext(GlobalStoreContext);

  return (
    <aside class="sidebar">
      <h3>Sidebar</h3>
      <p>This is the sidebar.</p>
      <IncumbentTable />
    </aside>
  );
};

export default SideBar;

/* 
    Written By: Soroush Semerkant
    Last Updated By: Soroush Semerkant
    Last Update Date: 02/16/2023
*/

import React, { useContext, useEffect } from "react";
import { GlobalStoreContext } from "../../Context/store";
import IncumbentTable from "../IncumbentTable/IncumbentTable";
import Col from "react-bootstrap/Col";
const SideBar = () => {
  const { store } = useContext(GlobalStoreContext);

  return (
    // <aside class="sidebar">
    <Col xs={5}>
      <IncumbentTable />
    </Col>
    // </aside>
  );
};

export default SideBar;

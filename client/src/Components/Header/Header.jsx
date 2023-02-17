/* 
    Written By: Soroush Semerkant
    Last Updated By: Soroush Semerkant
    Last Update Date: 02/16/2023
*/

import React, { useContext, useEffect } from "react";
import { GlobalStoreContext } from "../../Context/store";

const Header = () => {
  const { store } = useContext(GlobalStoreContext);

  return (
    <div>
      <h1>CSE 416 Project</h1>
    </div>
  );
};

export default Header;

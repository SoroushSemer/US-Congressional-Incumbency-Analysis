/* 
    Written By: Soroush Semerkant
    Last Updated By: Soroush Semerkant
    Last Update Date: 02/16/2023
*/

import React, { useContext, useEffect } from "react";
import Header from "../../Components/Header/Header";
import MyMap from "../../Components/Map/Map";
import SideBar from "../../Components/SideBar/SideBar";
import { GlobalStoreContext } from "../../Context/store";

const Home = () => {
  const { store } = useContext(GlobalStoreContext);

  return (
    <div className="container">
      <Header className="header" />
      <div className="main">
        <MyMap />
        <SideBar />
      </div>
    </div>
  );
};

export default Home;

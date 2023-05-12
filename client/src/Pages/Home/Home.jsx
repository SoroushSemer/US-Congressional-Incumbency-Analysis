/* 
    Written By: Soroush Semerkant
    Last Updated By: Soroush Semerkant
    Last Update Date: 02/16/2023
*/
import "./Home.css";

import React from "react";
import Header from "../../Components/Header/Header";
import MyMap from "../../Components/Map/Map";
import SideBar from "../../Components/SideBar/SideBar";
import Row from "react-bootstrap/Row";

const Home = () => {
  return (
    <div>
      {/* <Row> */}
      <Header className="header" />
      {/* </Row> */}
      {/* <Row className=""> */}
      <Row className="m-3 mb-1">
        <MyMap />
        <SideBar />
      </Row>
      {/* </Row> */}
      {/* <h4 style={{ textAlign: "right" }}>Built By Pirates</h4> */}
    </div>
  );
};

export default Home;

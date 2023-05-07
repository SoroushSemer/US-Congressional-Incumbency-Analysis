/* 
    Written By: Soroush Semerkant
    Last Updated By: Soroush Semerkant
    Last Update Date: 02/16/2023
*/
import "./Home.css";

import React, { useContext, useEffect } from "react";
import Header from "../../Components/Header/Header";
import MyMap from "../../Components/Map/Map";
import SideBar from "../../Components/SideBar/SideBar";
import { GlobalStoreContext } from "../../Context/store";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";

const Home = () => {
  const { store } = useContext(GlobalStoreContext);

  return (
    <div>
      {/* <Row> */}
      <Header className="header" />
      {/* </Row> */}
      {/* <Row className=""> */}
      <Row>
        <MyMap />
        <SideBar />
      </Row>
      {/* </Row> */}
      {/* <h4 style={{ textAlign: "right" }}>Built By Pirates</h4> */}
    </div>
  );
};

export default Home;

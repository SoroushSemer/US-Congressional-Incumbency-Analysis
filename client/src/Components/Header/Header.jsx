/* 
    Written By: Soroush Semerkant
    Last Updated By: Soroush Semerkant
    Last Update Date: 02/16/2023
*/

import React, { useContext, useEffect } from "react";
import { GlobalStoreContext } from "../../Context/store";
import Button from "react-bootstrap/Button";
import Dropdown from "react-bootstrap/Dropdown";
const states = require("../../states.json");

const Header = () => {
  const { store } = useContext(GlobalStoreContext);

  return (
    <nav className="navbar">
      <h1>CSE 416 Project</h1>
      <h2>{store && store.currentState ? store.currentState.name : ""}</h2>
      <Dropdown>
        <Dropdown.Toggle variant="success" id="dropdown-basic">
          {store.currentState ? store.currentState.name : "Select State"}
        </Dropdown.Toggle>

        <Dropdown.Menu>
          <Dropdown.Item onClick={() => store.setCurrentState(states.arizona)}>
            Arizona
          </Dropdown.Item>
          <Dropdown.Item
            onClick={() => store.setCurrentState(states.louisiana)}
          >
            Louisiana
          </Dropdown.Item>
          <Dropdown.Item onClick={() => store.setCurrentState(states.maryland)}>
            Maryland
          </Dropdown.Item>
        </Dropdown.Menu>
      </Dropdown>
      {/* <Button
        variant="primary"
        onClick={() => store.setCurrentState(states.arizona)}
      >
        Arizona
      </Button>{" "}
      <Button
        variant="primary"
        onClick={() => store.setCurrentState(states.louisiana)}
      >
        Louisiana
      </Button>{" "}
      <Button
        variant="primary"
        onClick={() => store.setCurrentState(states.maryland)}
      >
        Maryland
      </Button>{" "} */}
    </nav>
  );
};

export default Header;

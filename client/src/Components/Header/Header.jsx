/* 
    Written By: Soroush Semerkant
    Last Updated By: Soroush Semerkant
    Last Update Date: 02/16/2023
*/

import React, { useContext, useEffect } from "react";
import { GlobalStoreContext } from "../../Context/store";
import Button from "react-bootstrap/Button";
import Dropdown from "react-bootstrap/Dropdown";
import { Checkbox } from "@mui/material";
import Container from "react-bootstrap/esm/Container";
import Col from "react-bootstrap/esm/Col";
import Row from "react-bootstrap/esm/Row";
const states = require("../../states.json");

const maps = require("../../Data/maps.json");

const MapTypes = maps.Maps.map((map) => map.name);

const MapSubTypes = maps.Subtypes.map((subtype) => subtype.name);

const Header = () => {
  const { store } = useContext(GlobalStoreContext);

  return (
    <Container className="w-100 mt-3">
      <Row>
        <Col xs={6}>
          <h3>
            <img
              src="https://th.bing.com/th/id/R.63c10a159449db7c79783bfc32b4cb38?rik=ZsmmieKK%2b%2bmpsw&pid=ImgRaw&r=0"
              width="100px"
              style={{ borderRadius: "50%", cursor: "pointer" }}
              onClick={() => window.location.reload(false)}
            />
            <span className="mx-3 inline">
              US Congressional Incumbent Analysis
            </span>
          </h3>
        </Col>
        <Col xs={2}>
          <Dropdown>
            <Dropdown.Toggle variant="primary" id="dropdown-basic">
              {store.currentState ? store.currentState.name : "Select State"}
            </Dropdown.Toggle>

            <Dropdown.Menu>
              <Dropdown.Item
                onClick={() => {
                  store.setCurrentState(states.arizona);
                }}
              >
                Arizona
              </Dropdown.Item>
              <Dropdown.Item
                onClick={() => store.setCurrentState(states.louisiana)}
              >
                Louisiana
              </Dropdown.Item>
              <Dropdown.Item
                onClick={() => store.setCurrentState(states.maryland)}
              >
                Maryland
              </Dropdown.Item>
              <Button
                className="mx-3"
                variant="warning"
                onClick={() => store.setCurrentState(null)}
              >
                Clear Filters
              </Button>
            </Dropdown.Menu>
          </Dropdown>
        </Col>
        <Col xs={2}>
          <Dropdown autoClose="outside">
            <Dropdown.Toggle variant="success" id="dropdown-basic">
              Select Map Filter
            </Dropdown.Toggle>

            <Dropdown.Menu>
              {MapTypes.map((map, index) => (
                <Dropdown.Item key={index} onClick={() => store.toggleMap(map)}>
                  <Checkbox checked={store.getMap(map) >= 0} />
                  {map}
                </Dropdown.Item>
              ))}
              <Button
                className="mx-3"
                variant="warning"
                onClick={() => store.clearMaps()}
              >
                Clear Filters
              </Button>
            </Dropdown.Menu>
          </Dropdown>
        </Col>

        <Col xs={2}>
          {store && store.currentMaps.length >= 0 ? (
            <Dropdown autoClose="outside">
              <Dropdown.Toggle variant="danger" id="dropdown-basic">
                Select Map SubType
              </Dropdown.Toggle>

              <Dropdown.Menu>
                {MapSubTypes.map((subtype, index) => (
                  <Dropdown.Item
                    key={index}
                    onClick={() => store.toggleMapSubType(subtype)}
                  >
                    <Checkbox checked={store.getMapSubType(subtype) >= 0} />
                    {subtype}
                  </Dropdown.Item>
                ))}

                <Button
                  className="mx-3"
                  variant="warning"
                  onClick={() => store.clearMapSubType()}
                >
                  Clear Filters
                </Button>
              </Dropdown.Menu>
            </Dropdown>
          ) : (
            <div />
          )}
        </Col>
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
      </Row>
    </Container>
  );
};

export default Header;

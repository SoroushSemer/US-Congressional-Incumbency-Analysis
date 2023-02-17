/* 
    Written By: Soroush Semerkant
    Last Updated By: Soroush Semerkant
    Last Update Date: 02/16/2023
*/

import React, { useContext, useEffect } from "react";
import { GlobalStoreContext } from "../../Context/store";
import Button from "react-bootstrap/Button";

const states = {
  arizona: {
    name: "Arizona",
    coords: [34, -111],
    zoom: 6,
    incumbents: [
      {
        name: "John Doe",
        party: "Democrat",
        electionResult: true,
        geoVar: "Urban",
        populationVar: "High",
      },
      {
        name: "Jane Smith",
        party: "Republican",
        electionResult: false,
        geoVar: "Rural",
        populationVar: "Low",
      },
      {
        name: "Bill Johnson",
        party: "Independent",
        electionResult: true,
        geoVar: "Suburban",
        populationVar: "Medium",
      },
      {
        name: "Sarah Williams",
        party: "Green",
        electionResult: false,
        geoVar: "Exurban",
        populationVar: "High",
      },
      {
        name: "Mary Jones",
        party: "Libertarian",
        electionResult: true,
        geoVar: "Urban",
        populationVar: "Low",
      },
    ],
  },
  louisiana: {
    name: "Louisiana",
    coords: [30, -91],
    zoom: 7,
    incumbents: [
      {
        name: "Bob Anderson",
        party: "Democrat",
        electionResult: true,
        geoVar: "Suburban",
        populationVar: "Medium",
      },
      {
        name: "Tom Taylor",
        party: "Republican",
        electionResult: false,
        geoVar: "Exurban",
        populationVar: "High",
      },
      {
        name: "Kate Harris",
        party: "Independent",
        electionResult: true,
        geoVar: "Urban",
        populationVar: "Low",
      },
      {
        name: "Mike Brown",
        party: "Green",
        electionResult: false,
        geoVar: "Rural",
        populationVar: "Medium",
      },
      {
        name: "Joe Smith",
        party: "Libertarian",
        electionResult: true,
        geoVar: "Suburban",
        populationVar: "High",
      },
    ],
  },
  maryland: {
    name: "Maryland",
    coords: [39, -76],
    zoom: 8,
    incumbents: [
      {
        name: "Lisa Wilson",
        party: "Democrat",
        electionResult: false,
        geoVar: "Exurban",
        populationVar: "Low",
      },
      {
        name: "Richard Davis",
        party: "Republican",
        electionResult: true,
        geoVar: "Urban",
        populationVar: "High",
      },
      {
        name: "Sarah Miller",
        party: "Independent",
        electionResult: false,
        geoVar: "Rural",
        populationVar: "Medium",
      },
      {
        name: "Mark Johnson",
        party: "Green",
        electionResult: true,
        geoVar: "Suburban",
        populationVar: "Low",
      },
      {
        name: "Amy Anderson",
        party: "Libertarian",
        electionResult: false,
        geoVar: "Exurban",
        populationVar: "High",
      },
    ],
  },
};

const Header = () => {
  const { store } = useContext(GlobalStoreContext);

  return (
    <nav className="navbar">
      <h1>CSE 416 Project</h1>
      <h2>{store && store.currentState ? store.currentState.name : ""}</h2>
      <Button
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
      </Button>{" "}
    </nav>
  );
};

export default Header;

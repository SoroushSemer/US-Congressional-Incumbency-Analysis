// /*
//     Written By: Soroush Semerkant
//     Last Updated By: Soroush Semerkant
//     Last Update Date: 02/16/2023
// */
import "./Map.css";

import React, { useContext } from "react";
import { GlobalStoreContext } from "../../Context/store";
import { MapContainer, TileLayer, useMap } from "react-leaflet";
import Col from "react-bootstrap/Col";
import State from "../State/State";

// const arizonaGeoJSON = require("../../Data/gz_2010_us_500_11_5m.json");

const marylandJSON = require("../../Data/maryland.json");
const arizonaJSON = require("../../Data/arizona.json");
const louisianaJSON = require("../../Data/louisiana.json");

const Map = () => {
  const { store } = useContext(GlobalStoreContext);
  //   const map = useMap();
  var coords = [37, -95];
  var zoom = 4;
  if (store && store.currentState) {
    coords = store.currentState.coords;
    zoom = store.currentState.zoom;
    // map.flyTo(coords, zoom);
  }

  function MyComponent() {
    const map = useMap();
    map.flyTo(coords, zoom);
    return null;
  }

  function MyMap() {
    return (
      <Col xs={6}>
        <MapContainer center={coords} zoom={zoom} scrollWheelZoom={false}>
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
          />
          <MyComponent />
          {store && store.currentState ? (
            <div>
              <State data={arizonaJSON} state="Arizona" />
              <State data={marylandJSON} state="Maryland" />
              <State data={louisianaJSON} state="Louisiana" />
            </div>
          ) : (
            <div />
          )}
        </MapContainer>
      </Col>
    );
  }
  return MyMap();
};

export default Map;

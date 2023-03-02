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

const maps = require("../../Data/maps.json");

// const marylandJSON = require("../../Data/districts/maryland2010.json");
// const arizonaJSON = require("../../Data/districts/arizona2010.json");
// const louisianaJSON = require("../../Data/districts/louisiana2010.json");

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
      <Col xs={store && store.currentState ? 6 : 12}>
        <MapContainer center={coords} zoom={zoom} scrollWheelZoom={false}>
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
          />
          <MyComponent />

          {store  ? (
            maps.Maps.map((map) => {
              if (store.getMap(map.name) != -1) {
                const arizonaJSON = require("../../Data/" + map.arizona);
                const marylandJSON = require("../../Data/" + map.maryland);
                const louisianaJSON = require("../../Data/" + map.louisiana);
                return (
                  <div>
                    <State data={arizonaJSON} state="Arizona" />
                    <State data={marylandJSON} state="Maryland" />
                    <State data={louisianaJSON} state="Louisiana" />
                  </div>
                );
              }
            })
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

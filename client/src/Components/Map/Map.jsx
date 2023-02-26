// /*
//     Written By: Soroush Semerkant
//     Last Updated By: Soroush Semerkant
//     Last Update Date: 02/16/2023
// */
import "./Map.css";

import React, { useContext, useEffect } from "react";
import { GlobalStoreContext } from "../../Context/store";
import {
  MapContainer,
  TileLayer,
  useMap,
  Marker,
  Popup,
  GeoJSON,
} from "react-leaflet";
import Col from "react-bootstrap/Col";

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
      <Col xs={7}>
        <MapContainer center={coords} zoom={zoom} scrollWheelZoom={false}>
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
          />
          <MyComponent />
          <GeoJSON data={arizonaJSON} />
          <GeoJSON data={marylandJSON} />
          <GeoJSON data={louisianaJSON} />

          {/* <Marker
            position={
              store && store.currentState
                ? {
                    lat: store.currentState.coords[0],
                    lng: store.currentState.coords[1],
                  }
                : {
                    lat: 0,
                    lng: 0,
                  }
            }
          >
            <Popup>
              A pretty CSS3 popup.
              <br />
              Easily customizable.
            </Popup>
          </Marker> */}
        </MapContainer>
      </Col>
    );
  }
  return MyMap();
};

export default Map;

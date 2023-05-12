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
import { GeoJSON } from "react-leaflet";
import "leaflet-spin";
// const arizonaGeoJSON = require("../../Data/gz_2010_us_500_11_5m.json");


const maryland = require("../../Data/maryland.json");
const arizona = require("../../Data/arizona.json");
const louisiana = require("../../Data/louisiana.json");

const Map = () => {
  const { store } = useContext(GlobalStoreContext);
  //   const map = useMap();
  var coords = [37, -95];
  var zoom = 4.8;
  if (store && store.currentState) {
    coords = store.currentState.coords;
    zoom = store.currentState.zoom;
    // map.flyTo(coords, zoom);
  }
  function SetHeightOnChange({ height }) {
    const map = useMap();

    const mapContainer = map.getContainer();
    mapContainer.style.cssText = `height: ${height}; width: 100%; position: relative;`;

    return null;
  }
  function MyComponent() {
    const map = useMap();
    map.flyTo(coords, zoom);
    map.spin(store.loading);
    return null;
  }

  function MyMap() {
    var planInfo = null;
    if (store && store.currentState && store.currentMapGeoJSONs.length > 0) {
      planInfo = store.getPlanInfo();
    }
    return (
      <Col xs={store && store.currentState ? 5 : 12}>
        <h2 style={{ textAlign: "center" }} className="mx-5">
          {store && store.currentState ? store.currentState.name : ""}
        </h2>
        <div>
          <MapContainer
            center={coords}
            zoom={zoom}
            scrollWheelZoom={false}
            style={{
              height: "87vh",
              width: "100%",
            }}
          >
            <TileLayer
              url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
              attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
            />
            <MyComponent />
            {!store.currentState ? (
              <div>
                <GeoJSON
                  data={arizona}
                  onEachFeature={(feature, layer) => {
                    layer.on({
                      click: () => store.setCurrentState("Arizona"),
                    });
                    layer.bindTooltip("Arizona", {
                      direction: "center",
                    });
                  }}
                />
                <GeoJSON
                  data={louisiana}
                  onEachFeature={(feature, layer) => {
                    layer.on({
                      click: () => store.setCurrentState("Louisiana"),
                    });
                    layer.bindTooltip("Louisiana", {
                      direction: "center",
                    });
                  }}
                />
                <GeoJSON
                  data={maryland}
                  onEachFeature={(feature, layer) => {
                    layer.on({
                      click: () => store.setCurrentState("Maryland"),
                    });
                    layer.bindTooltip("Maryland", {
                      direction: "center",
                    });
                  }}
                />
              </div>
            ) : (
              <div />
            )}

            {store && store.currentState ? (
              store.currentMapGeoJSONs.map((data, index) => {
                // console.log(data);
                return (
                  <State
                    key={index}
                    color={data.color}
                    data={data}
                    state={store.currentState}
                  />
                );
              })
            ) : (
              // maps.Maps.map((map) => {
              //   if (store.getMap(map.name) != -1) {
              //     const arizonaJSON = require("../../Data/" + map.arizona);
              //     const marylandJSON = require("../../Data/" + map.maryland);
              //     const louisianaJSON = require("../../Data/" + map.louisiana);
              //     return (
              //       <div>
              //         <State color={map.color} data={arizonaJSON} state="Arizona" />
              //         <State color={map.color} data={marylandJSON} state="Maryland" />
              //         <State color={map.color} data={louisianaJSON} state="Louisiana" />
              //       </div>
              //     );
              //   }
              // })
              <div />
            )}
            <SetHeightOnChange
              height={store && store.currentState ? "50vh" : "87vh"}
            />
          </MapContainer>
        </div>
        {store && store.currentState && planInfo ? (
          <div className="m-3">
            <h5>{planInfo.name}</h5>
            <ul>
              <li>
                <strong>Districts: </strong> {planInfo.districts}
              </li>
              <li>
                <strong>Incumbents: </strong> {planInfo.incumbents}
              </li>
              <li>
                <strong>R/D Split: </strong>{" "}
                {planInfo.dem !== 0
                  ? (planInfo.rep / planInfo.dem).toFixed(2)
                  : 0.0}
              </li>
            </ul>
            <h5>Plan Summary</h5>
            <p>{planInfo.summary}</p>
          </div>
        ) : (
          <div />
        )}
      </Col>
    );
  }
  return MyMap();
};

export default Map;

/* 
    Written By: Soroush Semerkant
    Last Updated By: Soroush Semerkant
    Last Update Date: 02/16/2023
*/
import "./Map.css";

import React, { useContext, useEffect } from "react";
import { GlobalStoreContext } from "../../Context/store";
import { MapContainer, TileLayer, useMap, Marker, Popup } from "react-leaflet";

const Map = () => {
  const { store } = useContext(GlobalStoreContext);

  return (
    <div>
      <MapContainer center={[40.09, -95.71]} zoom={4} scrollWheelZoom={true}>
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
        />
      </MapContainer>
    </div>
  );
};

export default Map;

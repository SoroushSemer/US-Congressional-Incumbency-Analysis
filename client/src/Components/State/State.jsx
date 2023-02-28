import React, { useContext } from "react";
import { GlobalStoreContext } from "../../Context/store";
import { GeoJSON } from "react-leaflet";

const states = require("../../states.json");

const State = (props) => {
  const { store } = useContext(GlobalStoreContext);
  return (
    <GeoJSON
      style={(feature) => {
        if (
          store.currentState.name == props.state &&
          store.currentDistrict == feature.properties.district
        ) {
          return { fillColor: "red", color: "red" };
        } else {
          var color = "green";
          for (const incumbent of store.currentState.incumbents) {
            if (incumbent.district == feature.properties.district) {
              color = "blue";
            }
          }
          return { fillColor: color, color: color };
        }
      }}
      onEachFeature={(feature, layer) => {
        layer.on({
          //   mouseover: (e) => {
          //     if (feature.properties.district != store.currentDistrict) {
          //       e.target.setStyle({ fillColor: "red" });
          //     }
          //   },
          //   mouseout: (e) => {
          //     e.target.setStyle({
          //       fillColor: "blue",
          //     });
          //   },
          click: () => {
            if (store.getIncumbent(feature.properties.district) != null) {
              store.setCurrentDistrict(feature.properties.district);
            }
          },
        });

        layer.bindTooltip(feature.properties.district, {
          // permanent: true,
          sticky: true,
          direction: "left",
          offset: [-10, 0],
          // className: "number-label",
        });
      }}
      data={props.data}
    />
  );
};
export default State;

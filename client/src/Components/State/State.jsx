import React, { useContext } from "react";
import { GlobalStoreContext } from "../../Context/store";
import { GeoJSON } from "react-leaflet";

const states = require("../../states.json");

const color_mappings = {
  "01": "blue",
  "02": "red",
  "03": "yellow",
  "04": "cyan",
  "05": "purple",
  "06": "green",
  "07": "orange",
  "08": "black",
};

const State = (props) => {
  const { store } = useContext(GlobalStoreContext);
  return (
    <GeoJSON
      style={(feature) => {
        return {
          fillColor: color_mappings[feature.properties.DISTRICT],
          color: color_mappings[feature.properties.DISTRICT],
        };
      }}
      //   if (
      //     store.currentState &&
      //     store.currentState.name == props.state &&
      //     store.currentDistrict == feature.properties.DISTRICT
      //   ) {
      //     return { fillColor: "red", color: "red" };
      //   } else if (store.currentState) {
      //     var color = "white";
      //     for (const incumbent of store.currentState.incumbents) {
      //       if (incumbent.district == feature.properties.DISTRICT) {
      //         color = "green";
      //       }
      //     }
      //     return { fillColor: color, color: props.color };
      //   }
      // }}
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
            if (store.getIncumbent(feature.properties.DISTRICT) != null) {
              store.setCurrentDistrict(feature.properties.DISTRICT);
            }
          },
        });

        layer.bindTooltip(feature.properties.DISTRICT, {
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

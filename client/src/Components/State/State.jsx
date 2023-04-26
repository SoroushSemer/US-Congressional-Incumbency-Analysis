import React, { useContext } from "react";
import { GlobalStoreContext } from "../../Context/store";
import { GeoJSON } from "react-leaflet";

const states = require("../../states.json");

const State = (props) => {
  const { store } = useContext(GlobalStoreContext);
  const colors = [
    "blue",
    "red",
    "yellow",
    "cyan",
    "purple",
    "green",
    "orange",
    "black",
  ];
  var color_count = 0;
  var color_mappings = {};
  return (
    <GeoJSON
      style={(feature) => {
        var color = "none";
        var fillOpacity = 0.5;
        console.log(store.currentDistrict);
        console.log(feature.properties.DISTRICT);
        if (
          store.currentState &&
          // store.currentState.name == props.state &&
          store.currentDistrict == feature.properties.DISTRICT
        ) {
          fillOpacity = 1.0;
        } else if (store.currentState) {
          // color = "white";
          for (const incumbent of store.currentState.incumbents) {
            if (incumbent.district == feature.properties.DISTRICT) {
              fillOpacity = 0.75;
              color = feature.properties.COLOR;
            }
          }
        }
        // var fillColor;
        // fillColor = color_mappings[feature.properties.INCUMBENT];
        // console.log(fillColor);
        // if (fillColor === undefined) {
        //   color_mappings[feature.properties.INCUMBENT] = colors[color_count];
        //   color_count++;
        // }

        return {
          fillColor: feature.properties.COLOR,
          color: color,
          fillOpacity: fillOpacity,
          // color: color_mappings[feature.properties.DISTRICT],
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

        layer.bindTooltip(
          `<div><p>District: ${feature.properties.DISTRICT}</p><p>Incumbent: ${
            feature.properties.INCUMBENT == "0"
              ? "NONE"
              : feature.properties.INCUMBENT
          }</p><p>Party: ${
            feature.properties.PARTY == "0" ? "N/A" : feature.properties.PARTY
          }</p>`,
          {
            // permanent: true,
            sticky: true,
            direction: "left",
            offset: [-10, 0],
            // className: "number-label",
          }
        );
      }}
      data={props.data}
    />
  );
};
export default State;

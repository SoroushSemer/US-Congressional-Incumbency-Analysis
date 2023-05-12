import React, { useContext } from "react";
import { GlobalStoreContext } from "../../Context/store";
import { GeoJSON } from "react-leaflet";

const State = (props) => {
  const { store } = useContext(GlobalStoreContext);

  return (
    <GeoJSON
      style={(feature) => {
        var color = props.data.color;
        var fillOpacity = 0.75;
        var fillColor = "white";
        // console.log(store.currentDistrict);
        // console.log(feature.properties.DISTRICT);s
        if (
          store.currentState &&
          // store.currentState.name == props.state &&
          store.currentDistrict === feature.properties.INCUMBENT
        ) {
          fillOpacity = 1.0;
          color = "black";
        }
        if (
          feature.properties.PARTY &&
          feature.properties.PARTY !== "N/A" &&
          feature.properties.INCUMBENT !== "0"
        ) {
          fillColor = feature.properties.COLOR;
        }

        // } else if (store.currentState) {
        //   // color = "white";
        //   for (const incumbent of store.currentState.incumbents) {
        //     if (incumbent.district == feature.properties.DISTRICT) {
        //       // fillOpacity = 0.75;
        //       fillColor = feature.properties.COLOR;
        //     }
        //   }
        // }
        if (
          store &&
          store.currentMapSubType &&
          store.currentMapSubType[0] === "Election Vote"
        ) {
          if (
            store.currentState &&
            // store.currentState.name == props.state &&
            store.currentDistrict === feature.properties.INCUMBENT
          ) {
            color = "black";
          }
          if (
            parseInt(feature.properties["REP Votes"]) >
            parseInt(feature.properties["DEM Votes"])
          ) {
            fillColor = "red";
          } else {
            fillColor = "blue";
          }
        }
        if (
          store &&
          store.currentMapSubType &&
          store.currentMapSubType[0] === "None"
        ) {
          if (
            store.currentState &&
            // store.currentState.name == props.state &&
            store.currentDistrict === feature.properties.INCUMBENT
          ) {
            color = "black";
          }
          fillColor = "none";
        }
        if (
          store &&
          store.currentMapSubType &&
          store.currentMapSubType[0] === "Population Heat Map"
        ) {
          if (
            store.currentState &&
            // store.currentState.name == props.state &&
            store.currentDistrict === feature.properties.INCUMBENT
          ) {
            color = "black";
          }
          let pop = 0;
          if (feature.properties["Tot_2020_vap"]) {
            pop = feature.properties["Tot_2020_vap"];
          } else {
            pop = feature.properties["Tot_2022_vap"];
          }
          let scalar = 1.0 - (parseFloat(pop) - 500000) / 200000.0;
          let red = 0 * scalar;
          let green = 255 * scalar;
          let blue = 0 * scalar;
          fillColor = `rgb(${red}, ${green}, ${blue})`;
          fillOpacity = 1;
        }

        // var fillColor;
        // fillColor = color_mappings[feature.properties.INCUMBENT];
        // console.log(fillColor);
        // if (fillColor === undefined) {
        //   color_mappings[feature.properties.INCUMBENT] = colors[color_count];
        //   color_count++;
        // }

        return {
          fillColor: fillColor,
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
            if (store.getIncumbent(feature.properties.INCUMBENT) != null) {
              store.setCurrentDistrict(feature.properties.INCUMBENT);
            }
          },
        });

        layer.bindTooltip(
          `<div><p>District: ${feature.properties.DISTRICT}</p><p>Incumbent: ${
            feature.properties.INCUMBENT === "0"
              ? "NONE"
              : feature.properties.INCUMBENT +
                " (" +
                feature.properties.PARTY +
                ")"
          }</p><p>Winning Party: ${
            parseInt(feature.properties["REP Votes"]) <
            parseInt(feature.properties["DEM Votes"])
              ? "DEM"
              : "REP"
          }</p><p>Total Population (VAP): ${
            feature.properties["Tot_2020_vap"]
              ? parseInt(feature.properties["Tot_2020_vap"]).toLocaleString()
              : parseInt(feature.properties["Tot_2022_vap"]).toLocaleString()
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

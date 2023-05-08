/* 
    Written By: Soroush Semerkant
    Last Updated By: Soroush Semerkant
    Last Update Date: 02/16/2023
*/

import "./SideBar.css";

import React, { useContext, useEffect } from "react";
import { GlobalStoreContext } from "../../Context/store";
import IncumbentTable from "../IncumbentTable/IncumbentTable";
import Col from "react-bootstrap/Col";
import Chart from "react-apexcharts";
import Tabs from "react-bootstrap/Tabs";
import Tab from "react-bootstrap/Tab";
import ReactApexChart from "react-apexcharts";
import Nav from "react-bootstrap/Nav";
import Row from "react-bootstrap/Row";

import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Paper from "@mui/material/Paper";
import { Checkbox } from "@mui/material";
// const series = [
//   {
//     name: "box",
//     type: "boxPlot",
//     data: [
//       {
//         x: new Date("2017-01-01").getTime(),
//         y: [54, 66, 69, 75, 88],
//       },
//       {
//         x: new Date("2018-01-01").getTime(),
//         y: [43, 65, 69, 76, 81],
//       },
//       {
//         x: new Date("2019-01-01").getTime(),
//         y: [31, 39, 45, 51, 59],
//       },
//       {
//         x: new Date("2020-01-01").getTime(),
//         y: [39, 46, 55, 65, 71],
//       },
//       {
//         x: new Date("2021-01-01").getTime(),
//         y: [29, 31, 35, 39, 44],
//       },
//     ],
//   },
//   {
//     name: "outliers",
//     type: "scatter",
//     data: [
//       {
//         x: new Date("2017-01-01").getTime(),
//         y: 32,
//       },
//       {
//         x: new Date("2018-01-01").getTime(),
//         y: 25,
//       },
//       {
//         x: new Date("2019-01-01").getTime(),
//         y: 64,
//       },
//       {
//         x: new Date("2020-01-01").getTime(),
//         y: 27,
//       },
//       {
//         x: new Date("2020-01-01").getTime(),
//         y: 78,
//       },
//       {
//         x: new Date("2021-01-01").getTime(),
//         y: 15,
//       },
//     ],
//   },
// ];
const series = [
  {
    name: "box",
    type: "boxPlot",
    data: [
      {
        x: 0,
        y: [
          0.0707981220657277, 0.14829796577321397, 0.15679091744732773,
          0.18552720413191467, 0.21980800046829155,
        ],
      },
      {
        x: 1,
        y: [
          0.14342597998972706, 0.17566282904731728, 0.1822335989760682,
          0.19791588074230668, 0.24734107360424282,
        ],
      },
      {
        x: 2,
        y: [
          0.1706257294191579, 0.22240471954709914, 0.23534598797436102,
          0.24326000191928165, 0.2619630955203547,
        ],
      },
      {
        x: 3,
        y: [
          0.24562535718312267, 0.24995657551598, 0.2594128160694649,
          0.28994814688013604, 0.3200253244259624,
        ],
      },
      {
        x: 4,
        y: [
          0.25360027047500033, 0.2972646840569902, 0.32340207799102116,
          0.36194283215619255, 0.3788581823134016,
        ],
      },
      {
        x: 5,
        y: [
          0.3319431204321576, 0.3657194007194984, 0.38048866102099704,
          0.39486695190340476, 0.4314221266754613,
        ],
      },
      {
        x: 6,
        y: [
          0.36941179114877165, 0.39783494959096843, 0.479804655727078,
          0.48657583857892905, 0.4930927596236225,
        ],
      },
      {
        x: 7,
        y: [
          0.48190808609656777, 0.5177698826529322, 0.5506223680113993,
          0.5659428516474725, 0.5750637639548983,
        ],
      },
    ],
  },
  {
    name: "outliers",
    type: "scatter",
    data: [
      { x: 0, y: 0.07296047701147072 },
      { x: 0, y: 0.0707981220657277 },
      { x: 1, y: 0.24734107360424282 },
      { x: 2, y: 0.1706257294191579 },
      { x: 2, y: 0.17209823939700752 },
    ],
  },
];
const optionsBoxPlot = {
  chart: {
    type: "boxPlot",
    height: 350,
  },
  colors: ["#008FFB", "#FEB019"],
  // title: {
  //   text: "BoxPlot - Scatter Chart",
  //   align: "left",
  // },
  xaxis: {
    // type: "datetime",
    type: "int",
    // tooltip: {
    //   formatter: function (val) {
    //     return new Date(val).getFullYear();
    //   },
    // },
  },
  tooltip: {
    shared: false,
    intersect: true,
  },
  yaxis: {
    tickAmount: 4, // Sets the number of ticks on the y-axis
    min: 0, // Sets the minimum value of the y-axis
    max: 1, // Sets the maximum value of the y-axis
    step: 0.25, // Sets the step size between ticks on the y-axis
    decimalsInFloat: 2,
  },
};

const data = [
  {
    districtPlan: "2010 District",
    geoVar: 0.1,
    popVar: 200,
    RdSplit: 0.3,
    party: "Republican",
  },
  {
    districtPlan: "2020 District",
    geoVar: 0.2,
    popVar: 400,
    RdSplit: 0.4,
    party: "Democratic",
  },
  {
    districtPlan: "District Plan 1",
    geoVar: 0.3,
    popVar: 600,
    RdSplit: 0.5,
    party: "Republican",
  },
  {
    districtPlan: "District Plan 2",
    geoVar: 0.4,
    popVar: 800,
    RdSplit: 0.6,
    party: "Democratic",
  },
  {
    districtPlan: "District Plan 3",
    geoVar: 0.5,
    popVar: 1000,
    RdSplit: 0.7,
    party: "Republican",
  },
];

const SideBar = () => {
  const { store } = useContext(GlobalStoreContext);

  var options = {
    chart: {
      id: "basic-bar",
    },
    xaxis: {
      categories: [
        "White",
        "Black/African American",
        "American Indian/Alaska Native",
        "Asian",
        "Native Hawaiian/Other Pacific Islander",
      ],
    },
  };

  return (
    // <aside class="sidebar">
    <Col xs={store && store.currentState ? 6 : 0}>
      <h2 style={{ textAlign: "center" }} className="mb-3">
        {store && store.currentState ? store.currentState.name : ""}
      </h2>
      {store && store.currentState ? (
        <Tabs>
          <Tab eventKey="first" title="Incumbent">
            {store && store.currentState ? (
              <div className="mt-2">
                <h4>Incumbent Table</h4>
                <IncumbentTable />
              </div>
            ) : (
              <div />
            )}
            {store && store.currentDistrict ? (
              <Tabs
                defaultActiveKey="contact"
                id="uncontrolled-tab-example"
                className="mb-3 mt-2"
              >
                <Tab eventKey="contact" title="Summary">
                  <h5>District #{store.currentDistrict}</h5>

                  <ul>
                    <li>
                      <strong>Incumbent: </strong>
                      {store.getCurrentIncumbent().name}
                    </li>
                    <li>
                      <strong>2020 Population: </strong>
                      {store.getCurrentIncumbent().popVar2020[0]}
                    </li>
                    <li>
                      <strong>2022 Population: </strong>
                      {store.getCurrentIncumbent().popVar2022[0]}
                    </li>
                  </ul>
                </Tab>
                <Tab eventKey="home" title="Geographic Variation">
                  <div>
                    <h4 className="mt-3">
                      Geographic Variation from 2020 to 2022 for{" "}
                      {store.getCurrentIncumbent().name}
                    </h4>
                    <Chart
                      options={options}
                      series={[
                        {
                          name: "2020",
                          data: store.getCurrentIncumbent().popVar2020,
                        },
                        {
                          name: "2022",
                          data: store.getCurrentIncumbent().popVar2022,
                        },
                      ]}
                      type="bar"
                      width={"100%"}
                    />
                  </div>
                </Tab>
                <Tab eventKey="profile" title="Population Variation">
                  <div>
                    <h4 className="mt-3">
                      Population Variation from 2020 to 2022 for{" "}
                      {store.getCurrentIncumbent().name}
                    </h4>
                    <Chart
                      options={options}
                      series={[
                        {
                          name: "2020",
                          data: store.getCurrentIncumbent().popVar2020,
                        },
                        {
                          name: "2022",
                          data: store.getCurrentIncumbent().popVar2022,
                        },
                      ]}
                      type="bar"
                      width={"100%"}
                    />
                  </div>
                </Tab>
              </Tabs>
            ) : store && store.currentState ? (
              <div>
                <h5 className="mt-3">Redistricting Policy</h5>
                <p>{store.currentState.summary}</p>
              </div>
            ) : (
              <div />
            )}
          </Tab>

          <Tab eventKey="second" title="Ensemble">
            <h4 className="mt-2">Ensemble Summary</h4>
            <ul>
              <li>
                <strong>Districts: </strong>
                {Math.floor(Math.random() * 9) + 1}
              </li>
              <li>
                <strong>Avg Population per district:</strong>{" "}
                {Math.floor(Math.random() * 10000)}
              </li>
              <li>
                <strong>Avg District Size:</strong>{" "}
                {Math.floor(Math.random() * 1000)} sq. mi.
              </li>
              <li>
                <strong>Population Variation: </strong>
                {Math.floor(Math.random() * 2000) - 1000}
              </li>
              <li>
                <strong>Geographic Variation: </strong>
                {Math.floor(Math.random() * 100)}%
              </li>
            </ul>
            <TableContainer component={Paper}>
              <Table aria-label="simple table">
                <TableHead>
                  <TableRow>
                    <TableCell align="center">
                      <Checkbox></Checkbox>
                    </TableCell>
                    <TableCell width={250} align="center">
                      <strong>District Plan</strong>
                    </TableCell>
                    <TableCell align="center" width={100}>
                      <strong>Geographic Variation</strong>
                    </TableCell>
                    <TableCell align="center" width={100}>
                      <strong>Population Variation</strong>
                    </TableCell>

                    <TableCell align="center" width={100}>
                      <strong>R/D Split</strong>
                    </TableCell>
                    <TableCell align="center" width={100}>
                      <strong>Redistricting Party</strong>
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {data.map((row, index) => (
                    <TableRow key={index}>
                      <TableCell align="center">
                        <Checkbox></Checkbox>
                      </TableCell>
                      <TableCell width={250}>{row.districtPlan}</TableCell>
                      <TableCell align="center" width={100}>
                        {row.geoVar}
                      </TableCell>
                      <TableCell align="center" width={100}>
                        {row.popVar}
                      </TableCell>

                      <TableCell align="center" width={100}>
                        {row.RdSplit}
                      </TableCell>
                      <TableCell align="center" width={100}>
                        {row.party}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            <h4 className="mt-2">Ensemble Analysis</h4>
            <ReactApexChart
              options={optionsBoxPlot}
              series={series}
              type="boxPlot"
              height={350}
            />
          </Tab>
        </Tabs>
      ) : (
        <div />
      )}
    </Col>
    // </aside>
  );
};

export default SideBar;

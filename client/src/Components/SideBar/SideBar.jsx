/* 
    Written By: Soroush Semerkant
    Last Updated By: Soroush Semerkant
    Last Update Date: 02/16/2023
*/

import "./SideBar.css";

import React, { useContext } from "react";
import { GlobalStoreContext } from "../../Context/store";
import IncumbentTable from "../IncumbentTable/IncumbentTable";
import Col from "react-bootstrap/Col";
import Chart from "react-apexcharts";
import Tabs from "react-bootstrap/Tabs";
import Tab from "react-bootstrap/Tab";
import ReactApexChart from "react-apexcharts";
import Dropdown from "react-bootstrap/Dropdown";

const conversions = {
  election: "Percentage of Republican Votes",
  popVar: "Population Variation (VAP)",
  whVar: "White Population Variation",
  hisVar: "Hispanic Population Variation",
  blcVar: "Black Population Variation",
  asncVar: "Asian Population Variation",
  natcVar: "Native American Population Variation",
  paccVar: "Pacific Islander Population Variation",
  areaVar: "Geographic Area Variation",
};

const SideBar = () => {
  const { store } = useContext(GlobalStoreContext);
  var options = {
    chart: {
      id: "basic-bar",
    },
    xaxis: {
      categories: [
        "Total VAP",
        "White",
        "Asian",
        "Black",
        "Native American",
        "Hispanic",
        "Other",
      ],
    },
  };
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
      title: {
        text: "Sorted Districts",
      },
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
      title: {
        text: conversions[store.currentEnsembleAnalysis],
      },
    },
  };
  var incumbent = store.getCurrentIncumbent();

  var totalGeo = 0;
  var totalPop = 0;
  var totalRep = 0;
  var num = 0;
  var avgGeo = 0;
  var avgPop = 0;
  var avgRep = 0;
  if (store && store.currentEnsemble) {
    for (const district of store.currentEnsemble.plots["popVar"][0].data) {
      totalPop += district.y[2];
      num += 1;
    }
    for (const district of store.currentEnsemble.plots["areaVar"][0].data) {
      totalGeo += district.y[2];
    }
    for (const district of store.currentEnsemble.plots["election"][0].data) {
      totalRep += district.y[2];
    }
    avgGeo = totalGeo / num;
    avgPop = totalPop / num;
    avgRep = totalRep / num;
  }
  var planInfo = null;
  if (store && store.currentState) {
    planInfo = store.getPlanInfo();
  }
  return (
    // <aside class="sidebar">
    <Col xs={store && store.currentState ? 7 : 0}>
      <div className="mx-3">
        {store && store.currentState ? (
          <Tabs
            onSelect={(key) =>
              key === "second" ? store.getCurrentEnsemble() : null
            }
          >
            <Tab eventKey="first" title="Incumbent">
              {store && store.currentState ? (
                <div className="mt-2">
                  <h4 className="text-center">Incumbent Table</h4>
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
                    <h5>{store.currentDistrict}</h5>

                    <ul>
                      <li>
                        <strong>District: </strong>
                        {incumbent.district}
                      </li>
                      <li>
                        <strong>Party: </strong>
                        {incumbent.party}
                      </li>

                      <li>
                        <strong>Total Voting Age Population: </strong>
                        {incumbent.Tot_2022_vap
                          ? parseInt(incumbent.Tot_2022_vap).toLocaleString()
                          : parseInt(incumbent.Tot_2020_vap).toLocaleString()}
                      </li>
                      <li>
                        <strong>White Population: </strong>
                        {incumbent.Wh_2022_vap
                          ? parseInt(incumbent.Wh_2022_vap).toLocaleString()
                          : parseInt(incumbent.Wh_2020_vap).toLocaleString()}
                      </li>
                      <li>
                        <strong>Hispanic Population: </strong>
                        {incumbent.His_2022_vap
                          ? parseInt(incumbent.His_2022_vap).toLocaleString()
                          : parseInt(incumbent.His_2020_vap).toLocaleString()}
                      </li>
                      <li>
                        <strong>Black Population: </strong>
                        {incumbent.BlC_2022_vap
                          ? parseInt(incumbent.BlC_2022_vap).toLocaleString()
                          : parseInt(incumbent.BlC_2020_vap).toLocaleString()}
                      </li>
                      <li>
                        <strong>Native American Population: </strong>
                        {incumbent.NatC_2022_vap
                          ? parseInt(incumbent.NatC_2022_vap).toLocaleString()
                          : parseInt(incumbent.NatC_2020_vap).toLocaleString()}
                      </li>
                      <li>
                        <strong>Asian Population: </strong>
                        {incumbent.AsnC_2022_vap
                          ? parseInt(incumbent.AsnC_2022_vap).toLocaleString()
                          : parseInt(incumbent.AsnC_2020_vap).toLocaleString()}
                      </li>
                      <li>
                        <strong>Pacific Islander Population: </strong>
                        {incumbent.PacC_2022_vap
                          ? parseInt(incumbent.PacC_2022_vap).toLocaleString()
                          : parseInt(incumbent.PacC_2020_vap).toLocaleString()}
                      </li>
                      <li>
                        <strong>Area: </strong>
                        {(
                          parseInt(incumbent.AREA) / 2.59e6
                        ).toLocaleString()}{" "}
                        sq. mi.
                      </li>
                      <li>
                        <strong>Votes Recieved: </strong>
                        {incumbent.PARTY === "REP"
                          ? parseInt(incumbent["REP Votes"]).toLocaleString()
                          : parseInt(incumbent["DEM Votes"]).toLocaleString()}
                      </li>
                    </ul>
                  </Tab>
                  {/* <Tab eventKey="home" title="Geographic Variation">
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
                        height={"350px"}
                      />
                    </div>
                  </Tab> */}
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
                        height={"350px"}
                      />
                    </div>
                  </Tab>
                </Tabs>
              ) : (
                <div>
                  <h4 className="mt-3 text-center">Seat Analysis</h4>
                  {store && planInfo ? (
                    <Chart
                      options={{
                        chart: {
                          id: "basic-bar",
                        },
                        bar: {
                          horizontal: true,
                        },
                        fill: {
                          colors: ["#0000FF", "#FF0000", "#00FF00"],
                        },
                        xaxis: {
                          categories: [
                            "Democratic Safe Seats vs. Republican Safe Seats vs. Non Safe Seats",
                            "Open Seats vs. Incumbent Seats",
                            "Democratic vs. Republican",
                          ],
                        },
                      }}
                      series={[
                        {
                          data: [
                            planInfo.demSafe,
                            planInfo.districts - planInfo.incumbents,
                            planInfo.dem,
                          ],
                        },
                        {
                          data: [
                            planInfo.repSafe,
                            planInfo.incumbents,
                            planInfo.rep,
                          ],
                        },
                        { data: [planInfo.nonSafe] },
                      ]}
                      type="bar"
                      width={"100%"}
                      height={"350px"}
                    />
                  ) : (
                    <div />
                  )}{" "}
                </div>
              )}
            </Tab>

            <Tab eventKey="second" title="Ensemble">
              <div style={{ height: "20vh" }}>
                <h4 className="mt-2 text-center">Ensemble Summary</h4>
                <ul>
                  <li>
                    <strong>Ensemble Size: </strong> 10,000 District Plans
                  </li>
                  <li>
                    <strong>Plan Resolution: </strong> 10,000 Steps
                  </li>
                  <li>
                    <strong>Average Geographic Variation: </strong>{" "}
                    {avgGeo.toFixed(3)}
                  </li>
                  <li>
                    <strong>Average Voting Age Population Variation: </strong>{" "}
                    {avgPop.toFixed(3)}
                  </li>
                  <li>
                    <strong>Average Percentage of Republican Votes: </strong>{" "}
                    {avgRep.toFixed(3) * 100} %
                  </li>
                </ul>
              </div>
              <hr />
              <div>
                <h4 className="mt-2 text-center">Ensemble Analysis</h4>
                <Dropdown>
                  <Dropdown.Toggle variant="primary" id="dropdown-basic">
                    {store.currentEnsembleAnalysis
                      ? conversions[store.currentEnsembleAnalysis]
                      : "Select Feature"}
                  </Dropdown.Toggle>

                  <Dropdown.Menu>
                    <Dropdown.Item
                      onClick={() => {
                        store.setCurrentEnsembleAnalysis("election");
                      }}
                    >
                      Percentage of Republican Votes
                    </Dropdown.Item>
                    <Dropdown.Item
                      onClick={() => {
                        store.setCurrentEnsembleAnalysis("popVar");
                      }}
                    >
                      Population Variation (VAP)
                    </Dropdown.Item>
                    <Dropdown.Item
                      onClick={() => {
                        store.setCurrentEnsembleAnalysis("whVar");
                      }}
                    >
                      White Population Variation
                    </Dropdown.Item>
                    <Dropdown.Item
                      onClick={() => {
                        store.setCurrentEnsembleAnalysis("hisVar");
                      }}
                    >
                      Hispanic Population Variation
                    </Dropdown.Item>
                    <Dropdown.Item
                      onClick={() => {
                        store.setCurrentEnsembleAnalysis("blcVar");
                      }}
                    >
                      Black Population Variation
                    </Dropdown.Item>
                    <Dropdown.Item
                      onClick={() => {
                        store.setCurrentEnsembleAnalysis("natcVar");
                      }}
                    >
                      Native American Population Variation
                    </Dropdown.Item>
                    <Dropdown.Item
                      onClick={() => {
                        store.setCurrentEnsembleAnalysis("asncVar");
                      }}
                    >
                      Asian Population Variation
                    </Dropdown.Item>
                    <Dropdown.Item
                      onClick={() => {
                        store.setCurrentEnsembleAnalysis("paccVar");
                      }}
                    >
                      Pacific Islander Population Variation
                    </Dropdown.Item>
                    <Dropdown.Item
                      onClick={() => {
                        store.setCurrentEnsembleAnalysis("areaVar");
                      }}
                    >
                      Geographic Variation
                    </Dropdown.Item>
                  </Dropdown.Menu>
                </Dropdown>
                {store.currentEnsemble ? (
                  <ReactApexChart
                    options={optionsBoxPlot}
                    series={
                      store.currentEnsemble.plots[store.currentEnsembleAnalysis]
                    }
                    type="boxPlot"
                    height={550}
                  />
                ) : (
                  <div />
                )}
              </div>
            </Tab>
          </Tabs>
        ) : (
          <div />
        )}
      </div>
    </Col>
    // </aside>
  );
};

export default SideBar;

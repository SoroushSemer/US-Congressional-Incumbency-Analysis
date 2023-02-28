/* 
    Written By: Soroush Semerkant
    Last Updated By: Soroush Semerkant
    Last Update Date: 02/16/2023
*/

import React, { useContext, useEffect } from "react";
import { GlobalStoreContext } from "../../Context/store";
import IncumbentTable from "../IncumbentTable/IncumbentTable";
import Col from "react-bootstrap/Col";
import Chart from "react-apexcharts";

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
    <Col xs={6}>
      {store && store.currentState ? (
        <div>
          <h4>Incumbent Table</h4>
          <IncumbentTable />
        </div>
      ) : (
        <div />
      )}
      {store && store.currentDistrict ? (
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
      ) : (
        <div />
      )}
    </Col>
    // </aside>
  );
};

export default SideBar;

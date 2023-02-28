// /*
//     Written By: Soroush Semerkant
//     Last Updated By: Soroush Semerkant
//     Last Update Date: 02/16/2023
// */

import "./IncumbentTable.css";

import { useContext, useEffect } from "react";
import { GlobalStoreContext } from "../../Context/store";

// const IncumbentTable = () => {
//   const { store } = useContext(GlobalStoreContext);

//   return (
//     <div>
//       <h4>Incumbent Table</h4>

//       <table>
//         <tr>
//           <th>Incumbent Name</th>
//           <th>Political Party</th>
//           <th>2022 Election Results</th>
//           <th>Geographic Variation</th>
//           <th>Population Variations</th>
//         </tr>
//         {store &&
//         store.currentState &&
//         store.currentState.incumbents.length > 0 ? (
//           store.currentState.incumbents.map((incumbent) => (
//             <tr>
//               <td>{incumbent.name}</td>
//               <td>{incumbent.party}</td>
//               <td>{incumbent.electionResult ? "Win" : "Lose"}</td>
//               <td>{incumbent.geoVar}</td>
//               <td>{incumbent.populationVar}</td>
//             </tr>
//           ))
//         ) : (
//           <div />
//         )}
//       </table>
//     </div>
//   );
// };

// export default IncumbentTable;

import React from "react";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Paper from "@mui/material/Paper";

function createData(number, item, qty, price) {
  return { number, item, qty, price };
}

const rows = [
  createData(1, "Apple", 5, 3),
  createData(2, "Orange", 2, 2),
  createData(3, "Grapes", 3, 1),
  createData(4, "Tomato", 2, 1.6),
  createData(5, "Mango", 1.5, 4),
];

export default function IncumbentTable() {
  const { store } = useContext(GlobalStoreContext);
  return (
    <TableContainer component={Paper}>
      <Table aria-label="simple table">
        <TableHead>
          <TableRow>
            <TableCell>District</TableCell>
            <TableCell width={200} align="center">
              Name
            </TableCell>
            <TableCell align="center">Party</TableCell>
            <TableCell align="center">2022</TableCell>
            <TableCell align="center" width={100}>
              Geographic Variation
            </TableCell>
            <TableCell align="center">Population Variation</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {store && store.currentState ? (
            store.currentState.incumbents.map((incumbent) => (
              <TableRow
                key={incumbent.district}
                onClick={() => {
                  if (store.currentDistrict != incumbent.district) {
                    store.setCurrentDistrict(incumbent.district);
                  } else {
                    store.setCurrentDistrict(null);
                  }
                }}
                style={
                  store.currentDistrict == incumbent.district
                    ? { backgroundColor: "pink" }
                    : {}
                }
              >
                <TableCell component="th" scope="row">
                  {incumbent.district}
                </TableCell>
                <TableCell align="left">{incumbent.name}</TableCell>
                <TableCell align="center">{incumbent.party}</TableCell>
                <TableCell align="center">
                  {incumbent.electionResult ? "Win" : "Loss"}
                </TableCell>
                <TableCell align="center">{incumbent.geoVar}</TableCell>
                <TableCell align="center">{incumbent.populationVar}</TableCell>
              </TableRow>
            ))
          ) : (
            <div />
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

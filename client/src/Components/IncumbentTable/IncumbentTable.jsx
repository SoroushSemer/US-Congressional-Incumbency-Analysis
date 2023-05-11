// /*
//     Written By: Soroush Semerkant
//     Last Updated By: Soroush Semerkant
//     Last Update Date: 02/16/2023
// */

import "./IncumbentTable.css";

import { useContext, useEffect } from "react";
import { GlobalStoreContext } from "../../Context/store";


import React from "react";
// DataGrid
import Box from '@mui/material/Box';
import { DataGrid } from '@mui/x-data-grid';
// import Table from "@mui/material/Table";
// import TableBody from "@mui/material/TableBody";
// import TableCell from "@mui/material/TableCell";
// import TableContainer from "@mui/material/TableContainer";
// import TableHead from "@mui/material/TableHead";
// import TableRow from "@mui/material/TableRow";
// import Paper from "@mui/material/Paper";


const rows = [
  { id: 1, lastName: 'Snow', firstName: 'Jon', age: 35 },
  { id: 2, lastName: 'Lannister', firstName: 'Cersei', age: 42 },
  { id: 3, lastName: 'Lannister', firstName: 'Jaime', age: 45 },
  { id: 4, lastName: 'Stark', firstName: 'Arya', age: 16 },
  { id: 5, lastName: 'Targaryen', firstName: 'Daenerys', age: null },
  { id: 6, lastName: 'Melisandre', firstName: null, age: 150 },
  { id: 7, lastName: 'Clifford', firstName: 'Ferrara', age: 44 },
  { id: 8, lastName: 'Frances', firstName: 'Rossini', age: 36 },
  { id: 9, lastName: 'Roxie', firstName: 'Harvey', age: 65 },
];

export default function IncumbentTable() {
  const { store } = useContext(GlobalStoreContext);
  return (
    <Box sx={{ height: 400, width: '100%' }}>
      <DataGrid
        rows={rows}
        columns={columns}
        initialState={{
          pagination: {
            paginationModel: {
              pageSize: 5,
            },
          },
        }}
        pageSizeOptions={[5]}
        checkboxSelection
        disableRowSelectionOnClick
      />
    </Box>
    // <TableContainer component={Paper}>
    //   <Table aria-label="simple table">
    //     <TableHead>
    //       <TableRow>
    //         <TableCell>District</TableCell>
    //         <TableCell width={200} align="center">
    //           Name
    //         </TableCell>
    //         <TableCell align="center">Party</TableCell>
    //         <TableCell align="center">2022</TableCell>
    //         <TableCell align="center" width={100}>
    //           Geographic Variation
    //         </TableCell>
    //         <TableCell align="center">Population Variation</TableCell>
    //       </TableRow>
    //     </TableHead>
    //     <TableBody>
    //       {store && store.currentState ? (
    //         store.currentState.incumbents.map((incumbent) => (
    //           <TableRow
    //             key={incumbent.district}
    //             onClick={() => {
    //               if (store.currentDistrict != incumbent.name) {
    //                 store.setCurrentDistrict(incumbent.name);
    //               } else {
    //                 store.setCurrentDistrict(null);
    //               }
    //             }}
    //             style={
    //               store.currentDistrict == incumbent.name
    //                 ? { backgroundColor: "pink" }
    //                 : {}
    //             }
    //           >
    //             <TableCell component="th" scope="row">
    //               {incumbent.district}
    //             </TableCell>
    //             <TableCell align="left">
    //               <strong>{incumbent.name}</strong>
    //             </TableCell>
    //             <TableCell align="center">{incumbent.party}</TableCell>
    //             <TableCell
    //               align="center"
    //               style={
    //                 incumbent.electionResult
    //                   ? { color: "green" }
    //                   : { color: "red" }
    //               }
    //             >
    //               <strong>{incumbent.electionResult ? "Win" : "Loss"}</strong>
    //             </TableCell>
    //             <TableCell align="center">{incumbent.geoVar}</TableCell>
    //             <TableCell align="center">{incumbent.populationVar}</TableCell>
    //           </TableRow>
    //         ))
    //       ) : (
    //         <div />
    //       )}
    //     </TableBody>
    //   </Table>
    // </TableContainer>
  );
}

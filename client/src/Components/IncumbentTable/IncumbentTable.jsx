// /*
//     Written By: Soroush Semerkant
//     Last Updated By: Soroush Semerkant
//     Last Update Date: 02/16/2023
// */

import "./IncumbentTable.css";

import { useContext } from "react";
import { GlobalStoreContext } from "../../Context/store";

import React from "react";
// DataGrid
import Box from "@mui/material/Box";
import { DataGrid } from "@mui/x-data-grid";

// import Table from "@mui/material/Table";
// import TableBody from "@mui/material/TableBody";
// import TableCell from "@mui/material/TableCell";
// import TableContainer from "@mui/material/TableContainer";
// import TableHead from "@mui/material/TableHead";
// import TableRow from "@mui/material/TableRow";
// import Paper from "@mui/material/Paper";

const columns = [
  { field: "id", headerName: "id", width: 0 },
  {
    field: "district",
    headerName: "District",
    headerClassName: "super-app-theme--header",
    width: 100,
  },
  {
    field: "name",
    headerName: "Incumbent Name",
    headerClassName: "super-app-theme--header",
    width: 250,
  },
  {
    field: "party",
    headerName: "Party",
    headerClassName: "super-app-theme--header",
    width: 150,
  },
  {
    field: "electionResult",
    headerName: "2022 Election Result",
    width: 110,
  },
  {
    field: "election",
    headerName: "2022 Election Result",
    headerClassName: "super-app-theme--header",
    width: 200,
    valueGetter: (params) => (params.row.electionResult ? "Win" : "Loss"),
  },
  {
    field: "geoVar",
    headerName: "Geographic Variation",
    headerClassName: "super-app-theme--header",
    description:
      "Variation in the geographic area of the district from 2020 to 2022 = [(New - Old)/ (New + Old)]",
    width: 200,
  },
  {
    field: "populationVar",
    headerName: "Population Variation (VAP)",
    headerClassName: "super-app-theme--header",
    description:
      "Variation in the Voting Age Population of the district from 2020 to 2022 = [(New - Old)/ (New + Old)]",
    width: 304,
  },
];

export default function IncumbentTable() {
  const { store } = useContext(GlobalStoreContext);

  return (
    <Box
      sx={{
        height: "36vh",
        width: "100%",
        "& .super-app-theme--header": {
          backgroundColor: "#AcBeD0",
          fontWeight: "bold",
        },
        "& .Mui-selected": {
          backgroundColor: "pink",
          fontWeight: "bold",
        },
        ".MuiDataGrid-columnHeaderTitle": {
          fontWeight: "bold",
        },
        ".Republican": {
          backgroundColor: "rgba(255,0,0,0.4)",
          borderRadius: "10px",
        },
        ".Democratic": {
          backgroundColor: "rgba(0,100,255,0.4)",
          borderRadius: "10px",
        },
      }}
    >
      {store && store.currentState ? (
        <DataGrid
          rowHeight={40}
          rows={store.currentState.incumbents}
          columns={columns}
          initialState={{
            pagination: {
              paginationModel: {
                pageSize: 8,
              },
              sorting: {
                sortModel: [{ field: "district", sort: "desc" }],
              },
            },
            columns: {
              columnVisibilityModel: {
                // Hide columns status and traderName, the other columns will remain visible
                id: false,
                electionResult: false,
              },
            },
          }}
          pageSizeOptions={[8]}
          disableRowSelectionOnClick
          getRowClassName={(params) =>
            params.row.name === store.currentDistrict ? "Mui-selected" : ""
          }
          getCellClassName={(params) =>
            params.value === "Republican" || params.value === "Democratic"
              ? params.value
              : ""
          }
          onRowClick={(params) => store.setCurrentDistrict(params.row.name)}
        />
      ) : (
        <div />
      )}
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

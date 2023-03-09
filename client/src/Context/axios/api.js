import axios from "axios";
// axios.defaults.withCredentials = true;
// const cors = require("cors");
const api = axios.create({
  baseURL: "http://localhost:8080/",
});
// api.use(cors());
export const getState = (state, map) => api.get(`/maps/${state}/${map}`);
export const getHello = () => api.get(`/hello-world`);
const apis = {
  getState,
  getHello,
};

export default apis;

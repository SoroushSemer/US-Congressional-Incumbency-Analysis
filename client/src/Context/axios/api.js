import axios from "axios";
// axios.defaults.withCredentials = true;
// const cors = require("cors");
const api = axios.create({
  baseURL: "http://localhost:8080/",
});
// api.use(cors());
export const getMap = (state, map) => api.get(`/map/${state}/${map}`);
export const getState = (state) => api.get(`/state/${state}`);
export const getEnsemble = (state) => api.get(`/ensemble/${state}`);
export const getHello = () => api.get(`/hello-world`);
const apis = {
  getMap,
  getState,
  getEnsemble,
  getHello,
};

export default apis;

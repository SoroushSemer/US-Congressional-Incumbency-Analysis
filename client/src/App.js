import "./App.css";
import 'bootstrap/dist/css/bootstrap.min.css';
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./Pages/Home/Home";
import { GlobalStoreContextProvider } from "./Context/store";

export default function App() {
  
  return (
    <BrowserRouter>
      <GlobalStoreContextProvider>
        <Routes>
          <Route path="/" element={<Home />}></Route>
        </Routes>
      </GlobalStoreContextProvider>
    </BrowserRouter>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);

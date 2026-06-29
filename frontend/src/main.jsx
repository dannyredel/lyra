import React from "react";
import { createRoot } from "react-dom/client";
import ChassisApp from "./ChassisApp.jsx";
import "katex/dist/katex.min.css";
import "./ocean.css";

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <ChassisApp />
  </React.StrictMode>
);

import React, { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import GetPaste from "./Pages/GetPaste"
import PostPaste from "./Pages/PostPaste";
import NavBar from "./Components/NavBar";

const App = () => {
  return (
    <div className="app-container">
      <NavBar />
      <div className="app">
        <div className="left-col"></div>

        <BrowserRouter>
          <Routes>
            <Route index element={<PostPaste />} />
            <Route path="/:hash" element={< GetPaste />} />
          </Routes>
        </BrowserRouter>

        <div className="right-col"></div>
      </div>
    </div>

  );
};

export default App;
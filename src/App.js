import React, { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import GetPaste from "./Pages/GetPaste"
import PostPaste from "./Pages/PostPaste";

const App = () => {
  return (
    <div>
      <BrowserRouter>
        <Routes>
          <Route index element={<PostPaste />} />
          <Route path="/home" element={< PostPaste />} />
          <Route path="/get/:hash" element={< GetPaste />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
};

export default App;
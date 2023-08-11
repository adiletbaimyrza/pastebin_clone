import React, { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import GetPaste from "./Pages/GetPaste"
import PostPaste from "./Pages/PostPaste";
import NavBar from "./Components/NavBar";
import LoginForm from "./Components/LoginForm";
import RegisterForm from "./Components/RegisterForm";

const App = () => { 
  const [currentForm, setCurrentForm] = useState("login")

  const toggeForm = (formName) => {
    setCurrentForm(formName)
  };

  return (
    <div className="app-container">
      <NavBar />
      <div className="app">
        <div className="left-col">
        </div>

        <BrowserRouter>
          <Routes>
            <Route index element={<PostPaste />} />
            <Route path="/:hash" element={<GetPaste />} />
          </Routes>
        </BrowserRouter>

        <div className="right-col">
          {
            currentForm === "login" ? <LoginForm onFormSwitch={toggeForm}/> : <RegisterForm onFormSwitch={toggeForm}/>
          }
        </div>

      </div>
    </div>

  );
};

export default App;
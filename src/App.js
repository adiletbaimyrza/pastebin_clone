import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import GetPaste from "./Pages/GetPaste";
import PostPaste from "./Pages/PostPaste";
import NavBar from "./Components/NavBar";
import LoginForm from "./Components/LoginForm";
import RegisterForm from "./Components/RegisterForm";

const App = () => {
  const [currentForm, setCurrentForm] = useState("login");
  const [pastes, setPastes] = useState([]);
  const token = localStorage.getItem('token');

  const toggleForm = (formName) => {
    setCurrentForm(formName);
  };

  const fetchPastes = async () => {
    try {
      const response = await fetch("/get_pastes", {
        headers: {
          Authorization: `Bearer ${token}` // Include the JWT token in the Authorization header
        }
      });
      const data = await response.json();
      const pastesArray = data.pastes;
      setPastes(pastesArray);
    } catch (error) {
      console.error("Error fetching pastes:", error);
    }
  };

  useEffect(() => {
    if (token && token !== "" && token !== undefined) {
      fetchPastes();
    }
  }, [token]);

  return (
    <BrowserRouter>
      <div className="app-container">
        <NavBar />
        <div className="app">
          <div className="left-col">
            {token && token !== "" && token !== undefined ? (
              <React.Fragment>

                <div className="pastes">
                  {pastes.length > 0 ? (  // Check if pastes array is not empty
                    pastes.map((paste, index) => (
                      <div key={index} className="paste-item">
                        <a className="link-no-text-d" href={`http://localhost:3000/${paste.url_hash}`}>
                        <p className="paste-item-content">{paste.content}</p>
                        <p className="comment-created_at">{paste.created_at}</p>
                        <p className="comment-created_at">{paste.expire_at}</p>
                      </a>

                      </div>
                    ))
                  ) : (
                    <p>No pastes available.</p>
                  )}
                </div>
              </React.Fragment>
            ) : (
              <></>
            )}
          </div>

          <Routes>
            <Route index element={<PostPaste />} />
            <Route path="/:hash" element={<GetPaste />} />
          </Routes>

          <div className="right-col">
            {currentForm === "login" ? (
              <LoginForm onFormSwitch={toggleForm} />
            ) : (
              <RegisterForm onFormSwitch={toggleForm} />
            )}
          </div>
        </div>
      </div>
    </BrowserRouter>
  );
};

export default App;

import React, { useState } from "react";

const LoginForm = (props) => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");

    const handleUsernameChange = (event) => {
        console.log("Handling username change");
        setUsername(event.target.value);
    };

    const handlePasswordChange = (event) => {
        console.log("Handling password change");
        setPassword(event.target.value);
    };

    const handleSubmit = (event) => {
        console.log("Handling form submission");
        event.preventDefault();

        const userData = {
            username: username,
            password: password
        };

        console.log("Sending fetch request with user data:", userData);
        fetch('/token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData),
        }).then((response) => {
            if (response.ok) {
                return response.json();
            } else {
                console.error('Failed to log in User:', response.statusText);
            }
        }).then((data) => {
            if (data) {
                console.log("Received data:", data);
                localStorage.setItem('token', data.access_token);
                window.location.href = "/";
            }
        }).catch((error) => {
            console.error('Error sending the request:', error);
        });
    };

    const handleLogout = () => {
        console.log("Handling logout");
        localStorage.removeItem("token");
        window.location.href = "/";
    };

    const token = localStorage.getItem('token');
    console.log("Token:", token);

    return (
        <React.Fragment>
            {token && token !== "" && token !== undefined ? (
                    <button onClick={handleLogout} className="logout-button button">
                        Log out
                    </button>
            ) : (
                <div className="auth-form-container">
                    <h2 className="auth-form-header">Log in</h2>
                    <form className="auth-form" onSubmit={handleSubmit}>
                        <label className="label username-label">
                            Username
                            <input
                                className="input username-input"
                                value={username}
                                onChange={handleUsernameChange}
                                type="text"
                                id="username"
                                name="username"
                                placeholder="username"
                                required
                            />
                        </label>

                        <label className="label password-label">
                            Password
                            <input
                                className="input password-input"
                                value={password}
                                onChange={handlePasswordChange}
                                type="password"
                                id="password"
                                name="password"
                                placeholder="********"
                                required
                            />
                        </label>

                        <button className="auth-button" type="submit">
                            Log in
                        </button>
                    </form>
                    <button
                        className="auth-toggle-form"
                        onClick={() => props.onFormSwitch("register")}
                    >
                        Don't have an account? Register
                    </button>
                </div>
            )}
        </React.Fragment>
    );
};

export default LoginForm;

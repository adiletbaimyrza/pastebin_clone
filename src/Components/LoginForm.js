import React, { useState } from "react";
const token = localStorage.getItem('token')
console.log('token:' + token)

const LoginForm = (props) => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [loggedIn, setLoggedIn] = useState("");

    const handleUsernameChange = (event) => {
        setUsername(event.target.value);
    };

    const handlePasswordChange = (event) => {
        setPassword(event.target.value);
    };

    const handleSubmit = (event) => {
        event.preventDefault(); // Prevent the default form submission behavior

        // Prepare the JSON data to be sent
        const userData = {
            username: username,
            password: password
        };

        // Send the JSON data to the '/login' endpoint
        fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData),
        })
            .then((response) => {
                if (response.ok) {
                    // User logged in successfully
                    console.log('User logged in successfully!');
                    setLoggedIn("User logged in successfully!");
                    return response.json(); // Parse the response data as JSON
                } else {
                    // Handle error cases, e.g., display an error message
                    console.error('Failed to log in User:', response.statusText);
                }
            })
            .then(data => {
                if (data) {
                    console.log('this came from backend', data);
                    localStorage.setItem('token', data.access_token);
                }
            })
            .catch((error) => {
                console.error('Error sending the request:', error);
            });
    };

    return (
        <React.Fragment>
            {(token && token !== "" && token !== undefined) ? (
                <p>You are logged in successfully with token: {token}</p>
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

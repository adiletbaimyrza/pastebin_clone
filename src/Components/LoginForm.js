import React, { useState } from "react";

const LoginForm = (props) => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [showNotification, setShowNotification] = useState(false);

    const handleUsernameChange = (event) => {
        setUsername(event.target.value);
    };

    const handlePasswordChange = (event) => {
        setPassword(event.target.value);
    };

    const handleSubmit = (event) => {
        event.preventDefault();

        const userData = {
            username: username,
            password: password
        };

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
                console.error('Failed to log in. RESPONSE:', response.statusText);
            }
        }).then((data) => {
            if (data) {
                localStorage.setItem('token', data.access_token);
                setShowNotification(true);
                setTimeout(() => {
                    setShowNotification(false);
                    window.location.href = "/";
                }, 2000);
            }
        }).catch((error) => {
            console.error('Error sending the request. ERROR:', error);
        });
    };

    const handleLogout = () => {
        localStorage.removeItem("token");
        window.location.href = "/";
    };

    const token = localStorage.getItem('token');

    return (
        <React.Fragment>
            {showNotification && (
                <div className="notification">Logged in successfully!</div>
            )}
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

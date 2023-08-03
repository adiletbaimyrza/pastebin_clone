import React, { useState } from "react";

const RegisterForm = (props) => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [email, setEmail] = useState("");
    const [registered, setRegistered] = useState("");

    const handleUsernameChange = (event) => {
        setUsername(event.target.value);
    };

    const handlePasswordChange = (event) => {
        setPassword(event.target.value);
    };

    const handleConfirmPasswordChange = (event) => {
        setConfirmPassword(event.target.value);
    };

    const handleEmailChange = (event) => {
        setEmail(event.target.value);
    };

    const handleSubmit = (event) => {
        event.preventDefault(); // Prevent the default form submission behavior

        // Prepare the JSON data to be sent
        const userData = {
            username: username,
            email: email,
            password: password
        };

        // Send the JSON data to the '/register' endpoint
        fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData),
        })
            .then((response) => {
                if (response.ok) {
                    // User registered successfully
                    console.log('User registered successfully!');
                    setRegistered("User registered successfully!");
                } else {
                    // Handle error cases, e.g., display an error message
                    console.error('Failed to create User:', response.statusText);
                }
            })
            .catch((error) => {
                console.error('Error sending the request:', error);
            });
    };

    return (
        <div className="auth-form-container">
            <h2 className="auth-form-header">Register</h2>
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

                <label className="label email-label">
                    Email
                    <input
                        className="input email-input"
                        value={email}
                        onChange={handleEmailChange}
                        type="email"
                        id="email"
                        name="email"
                        placeholder="your@mail.com"
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

                <label className="label confirm-password-label">
                    Confirm password
                    <input
                        className="input password-input"
                        value={confirmPassword}
                        onChange={handleConfirmPasswordChange}
                        type="password"
                        id="confirm-password"
                        name="confirm-password"
                        placeholder="********"
                        required
                    />
                </label>

                <button className="auth-button" type="submit">
                    Register
                </button>
            </form>
            <button className="auth-toggle-form" onClick={() => props.onFormSwitch("login")}>
                Already have an account? Log in
            </button>
        </div>
    );
};

export default RegisterForm;
import React, { useState, useEffect } from "react";
import axios from "axios";

const GetPaste = () => {
    const [pasteId, setPasteId] = useState("");
    const [pasteContent, setPasteContent] = useState("");

    const handleIdChange = (event) => {
        setPasteId(event.target.value);
    };

    const handleGetClick = () => {
        // Make the GET request to retrieve the paste content
        axios
            .get(`/get/${pasteId}`)
            .then((response) => {
                if (response.status === 200) {
                    // Paste found, set the content in state
                    setPasteContent(response.data.content);
                } else {
                    // Handle error cases, e.g., display an error message
                    console.error("Failed to get paste:", response.statusText);
                }
            })
            .catch((error) => {
                console.error("Error sending the request:", error);
            });
    };

    useEffect(() => {
        // Extract the UUID from the address
        const pathParts = window.location.pathname.split("/");
        const uuid = pathParts[pathParts.length - 1];

        // Make the GET request to retrieve the paste content
        axios
            .get(`/get/${uuid}`)
            .then((response) => {
                if (response.status === 200) {
                    // Paste found, set the content in state
                    setPasteContent(response.data.content);
                } else {
                    // Handle error cases, e.g., display an error message
                    console.error("Failed to get paste:", response.statusText);
                }
            })
            .catch((error) => {
                console.error("Error sending the request:", error);
            });
    }, []); // Empty dependency array ensures the effect runs only once on mount

    return (
        <div>
            {pasteContent ? (
                <div>
                    <h3>Paste Content:</h3>
                    <pre>{pasteContent}</pre>
                </div>
            ) : (
                <div>
                    <p>Loading paste...</p>
                </div>
            )}
        </div>
    );
};

export default GetPaste;

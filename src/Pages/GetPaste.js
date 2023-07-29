import React, { useState, useEffect } from "react";
import axios from "axios";

const GetPaste = () => {
    const [pasteContent, setPasteContent] = useState("");

    useEffect(() => {
        // Extract the HASH from the address
        const pathParts = window.location.pathname.split("/");
        const hash = pathParts[pathParts.length - 1];

        // Make the GET request to retrieve the paste content
        axios
            .get(`/get/${hash}`)
            .then((response) => {
                if (response.status === 200) {
                    console.log('request sent')
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
        <div class="main">
            {pasteContent ? (
                <div>
                    <pre>{pasteContent}</pre>
                </div>
            ) : (
                <div>
                    <p>Paste loading...</p>
                </div>
            )}
        </div>
    );
};

export default GetPaste;

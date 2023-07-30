import React, { useState, useEffect } from "react";
import axios from "axios";
import { CopyToClipboard } from "react-copy-to-clipboard"

const GetPaste = () => {
    const [pasteContent, setPasteContent] = useState("");
    const [copied, setCopied] = useState(false);

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
        <div className="main">
            <CopyToClipboard text={ pasteContent }>
                <button
                    className="copy-button"
                    onCopy={() => setCopied(true)}>
                    <svg className="plus" width="1.8rem" height="1.8rem" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M4 12H20M12 4V20" stroke="#ffffff" strokeWidth="2.3" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                </button>
            </CopyToClipboard>
            {pasteContent ? (
                
                <div class="content">
                    <pre>{ pasteContent }</pre>
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

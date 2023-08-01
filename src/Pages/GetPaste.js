    import React, { useState, useEffect } from "react";
    import axios from "axios";
    import { CopyToClipboard } from "react-copy-to-clipboard"
    import CopySVG from "../SVGs/CopySVG";

    const GetPaste = () => {
        const [pasteContent, setPasteContent] = useState("");
        const [copied, setCopied] = useState(false);

        useEffect(() => {
            // Extract the HASH from the address
            const pathParts = window.location.pathname.split("/");
            const hash = pathParts[pathParts.length - 1];

            // Make the GET request to retrieve the paste content
            axios
                .get(`/${hash}`)
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
                <div className="post-nav">
                    <CopyToClipboard text={ pasteContent }>
                        <button
                            className="copy-button"
                            onCopy={() => setCopied(true)}>
                            <CopySVG />
                        </button>
                    </CopyToClipboard>
                </div>
                
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
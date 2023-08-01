import React, { useState, useEffect } from "react";
import axios from "axios";
import { CopyToClipboard } from "react-copy-to-clipboard";
import CopySVG from "../SVGs/CopySVG";

const GetPaste = () => {
  const [pasteContent, setPasteContent] = useState("");
  const [pasteCreatedAt, setPasteCreatedAt] = useState("");
  const [pasteExpireAt, setPasteExpireAt] = useState("");
  const [pasteUserId, setPasteUserId] = useState("");
  const [pasteUsername, setPasteUsername] = useState("");
  const [pasteViewsCount, setPasteViewsCount] = useState("");
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
              console.log("request sent");
              // Paste found, set the content in state
              setPasteContent(response.data.content);
              setPasteCreatedAt(response.data.created_at);
              setPasteExpireAt(response.data.expire_at);
              setPasteUserId(response.data.user_id);
              setPasteUsername(response.data.username);
              setPasteViewsCount(response.data.views_count);
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
        <p className="post-nav-item">created at: {pasteCreatedAt}</p>
        <p className="post-nav-item">will expire at: {pasteExpireAt}</p>
        <p className="post-nav-item">username: {pasteUsername}</p>
        <p className="post-nav-item">views: {pasteViewsCount}</p>
        <CopyToClipboard text={pasteContent}>
          <button className="copy-button" onCopy={() => setCopied(true)}>
            <CopySVG />
          </button>
        </CopyToClipboard>
      </div>

      {pasteContent ? (
        <div className="content">
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

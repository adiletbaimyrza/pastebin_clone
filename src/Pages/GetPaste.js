import React, { useState, useEffect } from "react";
import axios from "axios";
import { CopyToClipboard } from "react-copy-to-clipboard";

import CopySVG from "../SVGs/CopySVG";
import TimeSVG from "../SVGs/TimeSVG";
import TimerSVG from "../SVGs/TimerSVG";
import UserSVG from "../SVGs/UserSVG";

import { format } from "date-fns"

const GetPaste = () => {
  const [pasteContent, setPasteContent] = useState("");
  const [pasteCreatedAt, setPasteCreatedAt] = useState("");
  const [pasteExpireAt, setPasteExpireAt] = useState("");
  const [pasteUserId, setPasteUserId] = useState("");
  const [pasteUsername, setPasteUsername] = useState("");
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
              setPasteContent(response.data.content);
              // Format the datetime strings using date-fns
              setPasteCreatedAt(format(new Date(response.data.created_at), "MMMM d, yyyy HH:mm"));
              setPasteExpireAt(format(new Date(response.data.expire_at), "MMMM d, yyyy HH:mm"));
              setPasteUserId(response.data.user_id);
              setPasteUsername(response.data.username);
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
        <div className="post-nav-item">
          <TimeSVG />
          {pasteCreatedAt}
        </div>
        <div className="post-nav-item">
          <TimerSVG />
          {pasteExpireAt}
        </div>
        <div className="post-nav-item">
          <UserSVG />
          {pasteUsername}
          </div>
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

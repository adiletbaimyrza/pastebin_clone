import React, { useState, useEffect } from "react";
import axios from "axios";
import { CopyToClipboard } from "react-copy-to-clipboard";
import { format } from "date-fns"

import CopySVG from "../SVGs/CopySVG";
import TimeSVG from "../SVGs/TimeSVG";
import TimerSVG from "../SVGs/TimerSVG";
import UserSVG from "../SVGs/UserSVG";

const GetPaste = () => {
  const [pasteContent, setPasteContent] = useState("");
  const [pasteCreatedAt, setPasteCreatedAt] = useState("");
  const [pasteExpireAt, setPasteExpireAt] = useState("");
  const [pasteUsername, setPasteUsername] = useState("");
  const [comments, setComments] = useState([]);
  const [comment, setComment] = useState("");

  const handleCommentChange = (event) => {
    setComment(event.target.value);
  };

  const handleSubmit = () => {
    const commentData = {
        text : text,
        author : author
    };

    fetch('/add_comment', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${jwt}`,
        },
        body: JSON.stringify(commentData),
    })
    .then((response) => {
        if (response.ok) {
            console.log("OK. Comment sent to the API");
        } else {
            console.error('Failed to create paste:', response.statusText);
        }
    })
    .catch((error) => {
        console.error('Error sending the request:', error);
    });
  };

  useEffect(() => {
    const pathParts = window.location.pathname.split("/");
    const hash = pathParts[pathParts.length - 1];

    axios
      .get(`/${hash}`)
      .then((response) => {
        if (response.status === 200) {
          setPasteContent(response.data.content);
          setPasteCreatedAt(format(new Date(response.data.created_at), "MMMM d, yyyy HH:mm"));
          setPasteExpireAt(format(new Date(response.data.expire_at), "MMMM d, yyyy HH:mm"));
          setPasteUserId(response.data.user_id);
          setPasteUsername(response.data.username);
          setComments(response.data.comments);
        } else {
          console.error("Failed to get paste:", response.statusText);
        }
      })
      .catch((error) => {
        console.error("Error sending the request:", error);
      });
    }, 
    
  []);

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
        <>
          <div className="content">
            <pre>{pasteContent}</pre>
          </div>
          
          <div className="comments">
            {comments.length > 0 ? (
              comments.map((comment, index) => (
                <div key={index} className="comment">
                  <p>{comment.text}</p>
                  <p>By: {comment.author}</p>
                </div>
              ))
            ) : (
              <p>No comments available.</p>
            )}
          </div>

          <div className="add-comment">
            <form onSubmit={handleSubmit}>
              <label className="add-comment-label">
                  Comment
                  <input
                      className="input comment-input"
                      value={comment}
                      onChange={handleCommentChange}
                      type="text"
                      id="comment"
                      name="comment"
                      placeholder="comment"
                      required
                  />
              </label>
              <button className="add-comment-button button" type="submit">
                    Add comment
              </button>
            </form>
          </div>
        </>
      ) : (
        <div>
          <p>Paste loading...</p>
        </div>
      )}
    </div>
  );
};

export default GetPaste;

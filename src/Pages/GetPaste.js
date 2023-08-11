import React, { useState, useEffect } from "react";
import axios from "axios";
import { CopyToClipboard } from "react-copy-to-clipboard";
import { format } from "date-fns";

import CopySVG from "../SVGs/CopySVG";
import TimeSVG from "../SVGs/TimeSVG";
import TimerSVG from "../SVGs/TimerSVG";
import UserSVG from "../SVGs/UserSVG";

const GetPaste = () => {
  const [pasteContent, setPasteContent] = useState("");
  const [pasteCreatedAt, setPasteCreatedAt] = useState("");
  const [pasteExpireAt, setPasteExpireAt] = useState("");
  const [pasteUsername, setPasteUsername] = useState("");
  const [pasteId, setPasteId] = useState("");

  const [comment, setComment] = useState("");
  const [copied, setCopied] = useState("");
  const [comments, setComments] = useState([]);

  const jwt = localStorage.getItem('token');

  const handleCommentChange = (event) => {
    setComment(event.target.value);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    
    if (!pasteId) {
      console.error('Failed to create comment: Missing paste id');
      return;
    }
  
    const commentData = {
      comment: comment,
      paste_id: pasteId
    };

    fetch('/create_comment', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${jwt}`,
      },
      body: JSON.stringify(commentData),
    })
    .then((response) => {
        if (response.ok) {
            console.log("OK. Comment sent to Backend")
        } else {
            console.error('Failed to create comment:', response.statusText);
        }
    })
    .catch((error) => {
        console.error('Error sending the request:', error);
    });

    
  }

  useEffect(() => {
    const pathParts = window.location.pathname.split("/");
    const hash = pathParts[pathParts.length - 1];

    axios
      .get(`/${hash}`)
      .then((response) => {
        if (response.status === 200) {
          const responseData = response.data;
          setPasteId(responseData.id);
          setPasteContent(responseData.content);
          setPasteCreatedAt(format(new Date(responseData.created_at), "MMMM d, yyyy HH:mm"));
          setPasteExpireAt(format(new Date(responseData.expire_at), "MMMM d, yyyy HH:mm"));
          setPasteUsername(responseData.username);
          setComments(responseData.comments);
        } else {
          console.error("Failed to get paste:", response.statusText);
        }
      })
      .catch((error) => {
        console.error("Error sending the request:", error);
      });
  }, []);

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
          <button className="copy-button">
            <CopySVG /> Copy
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
          
          {jwt ? (
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
          ) : <p>unauthorized to comment</p>
          }
          
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

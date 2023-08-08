import React, { useState } from 'react';
import PlusSVG from '../SVGs/PlusSVG';

const PostPaste = () => {
    const [content, setContent] = useState('');
    const [minutes, setMinutes] = useState(60); // Default to 60 minutes
    const [pasteId, setPasteId] = useState(null);

    const handleContentChange = (event) => {
        setContent(event.target.value); 
    };

    const handleMinutesChange = (event) => {
        // Ensure the minutes value is between 1 and 60
        const newMinutes = Math.max(1, Math.min(60, event.target.value));
        setMinutes(newMinutes);
    };

    const jwt = localStorage.getItem('token');

    const handlePostClick = () => {
        // Prepare the JSON data to be sent
        const pasteData = {
            content: content,
            minutes_to_live: minutes,
        };

        // Send the JSON data to the '/post' endpoint
        if (jwt) {
            fetch('/create_paste', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${jwt}`,
                },
                body: JSON.stringify(pasteData),
            })
                .then((response) => {
                    if (response.ok) {
                        response.json().then((data) => {setPasteId(data.hash)});
                    } else {
                        console.error('Failed to create paste:', response.statusText);
                    }
                })
                .catch((error) => {
                    console.error('Error sending the request:', error);
                });
        }
        else {
            fetch('/create_paste', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(pasteData),
            })
                .then((response) => {
                    if (response.ok) {
                        response.json().then((data) => {setPasteId(data.hash)});
                    } else {
                        console.error('Failed to create paste:', response.statusText);
                    }
                })
                .catch((error) => {
                    console.error('Error sending the request:', error);
                });
        }
        
    };

    return (
        <div className="main">
            {/* Display the HASH if it exists */}
            {pasteId && <a href={`http://localhost:3000/${pasteId}`} target='_blank'>localhost:3000/{pasteId}</a>}
            <div className="paste-nav">
                <label className="timer-label">
                    Timer <small className="small">(minutes)</small>:
                    <input className="timer-input"
                        type="number"
                        min="1"
                        max="60"
                        value={minutes}
                        onChange={handleMinutesChange}
                    />
                </label>

                <button
                    className="paste"
                    onClick={handlePostClick}>
                    <PlusSVG />
                    <div className="paste-button-text">New Paste</div> 
                </button>
            </div>
            <textarea className="textarea"
                rows="10"
                cols="50"
                value={content}
                onChange={handleContentChange}
                placeholder="Paste your text here..."
            />
        </div>
    );
};

export default PostPaste;

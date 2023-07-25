import React, { useState } from 'react';

const PostPaste = () => {
    const [content, setContent] = useState('');
    const [pasteId, setPasteId] = useState(null);

    const handleContentChange = (event) => {
        setContent(event.target.value);
    };

    const handlePostClick = () => {
        // Prepare the JSON data to be sent
        const pasteData = {
            content: content,
            minutes_to_live: 60, // Change this value to set the expiration time in minutes
        };

        // Send the JSON data to the '/post' endpoint
        fetch('/post', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(pasteData),
        })
            .then((response) => {
                if (response.ok) {
                    // Paste successfully created
                    console.log('Paste created successfully!');
                    // Extract and set the pasteId from the response data
                    response.json().then((data) => {
                        setPasteId(data.item.id); // Access the "id" from the "item" object
                    });
                } else {
                    // Handle error cases, e.g., display an error message
                    console.error('Failed to create paste:', response.statusText);
                }
            })
            .catch((error) => {
                console.error('Error sending the request:', error);
            });
    };

    return (
        <div>
            <textarea
                rows="10"
                cols="50"
                value={content}
                onChange={handleContentChange}
                placeholder="Enter your text here..."
            />
            <br />
            <button onClick={handlePostClick}>Post Paste</button>

            {/* Display the pasteId if it exists */}
            {pasteId && <p>Paste ID: {pasteId}</p>}
        </div>
    );
};

export default PostPaste;

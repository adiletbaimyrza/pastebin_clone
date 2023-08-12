import React, { useState } from 'react';

import PlusSVG from '../SVGs/PlusSVG';

const PostPaste = () => {
    const [content, setContent] = useState(null);                    // default null
    const [pasteUrlHash, setPasteUrlHash] = useState(null);          // default null
    const [timeUnit, setTimeUnit] = useState('minutes');             // default 'Minutes'
    const [hideTimer, setHideTimer] = useState(false);               // default false
    const [timeValue, setTimeValue] = useState(10);                  // default 10
    const [deleteUponSeen, setDeleteUponSeen] = useState(false);     // default false
    const [neverDelete, setNeverDelete] = useState(false);           // default false
    const [max, setMax] = useState(60);

    const jwt = localStorage.getItem('token');

    const handleContentChange = (event) => {
        setContent(event.target.value); 
    };

    const handleTimeValueChange = (event) => {
        setTimeValue(event.target.value);
    };

    const handleTimeUnitChange = (event) => {
        if (event.target.value === 'never') {
            setHideTimer(true);
            setNeverDelete(true);
            setTimeUnit(null);
        }
        else if (event.target.value === 'delete-upon-seen') {
            setHideTimer(true);
            setDeleteUponSeen(true);
            setTimeUnit(null);
        }
        else {
            setTimeUnit(event.target.value);
            setHideTimer(false);
            setNeverDelete(false);
            setDeleteUponSeen(false);
            if (event.target.value === 'Minutes') {
                setMax(60);
            }
            else if (event.target.value === 'Hours') {
                setMax(24);
            }
            else {
                setMax(365);
            }
        }
    };

    const handlePostClick = () => {
        const pasteData = {
            content: content,
            time_unit: timeUnit,
            time_value: timeValue,
            delete_upon_seen: deleteUponSeen,
            never_delete: neverDelete
        };

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
                        response.json().then((data) => {setPasteUrlHash(data.url_hash)});
                    } else {
                        console.error('Failed to create paste. RESPONSE:', response.statusText);
                    }
                })
                .catch((error) => {
                    console.error('Error sending the request. ERROR:', error);
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
                        response.json().then((data) => {setPasteUrlHash(data.url_hash)});
                    } else {
                        console.error('Failed to create paste. RESPONSE:', response.statusText);
                    }
                })
                .catch((error) => {
                    console.error('Error sending the request. ERROR:', error);
                });
        }
        
    };

    return (
        <div className="main">
            {pasteUrlHash && <a href={`http://localhost:3000/${pasteUrlHash}`} target='_blank'>localhost:3000/{pasteUrlHash}</a>}
            <div className="paste-nav">
                {jwt && jwt !== "" && jwt !== undefined ? (
                    <>
                        <select className='time-unit-select' value={timeUnit} onChange={handleTimeUnitChange}>
                            <option className="time-unit-item" value="delete-upon-seen">Delete upon seen</option>
                            <option className="time-unit-item" value="minutes">Minutes</option>
                            <option className="time-unit-item" value="hours">Hours</option>
                            <option className="time-unit-item" value="days">Days</option>
                            <option className="time-unit-item" value="never">Never</option>
                        </select>

                        {hideTimer === false ? (
                            <label className="timer-label">
                                Timer
                                <small className="small">
                                    ({timeUnit})
                                </small>
                                :
                                <input className="timer-input"
                                    type="number"
                                    min="1"
                                    max={max}
                                    value={timeValue}
                                    onChange={handleTimeValueChange}
                                />
                            </label>
                        ) : (
                            <></>
                        )}
                    </>
                ) : (
                    <label className="timer-label">
                    Timer
                    <small className="small">
                        ({timeUnit})
                    </small>
                    :
                    <input className="timer-input"
                        type="number"
                        min="1"
                        max="60"
                        value={timeValue}
                        onChange={handleTimeValueChange}
                    />
                </label>
                )}
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

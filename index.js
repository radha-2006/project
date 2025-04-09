// frontend/pages/index.js
import React, { useState } from 'react';
import styles from '../styles/Home.module.css';

export default function Home() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const sendMessage = async () => {
    if (!input.trim()) return;

    setMessages([...messages, { text: input, isUser: true }]);
    setInput('');

    try {
      const response = await fetch('/api/chat', { //change here
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: input }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setMessages([...messages, { text: data.response, isUser: false }]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages([...messages, { text: "Error.", isUser: false }]);
    }
  };

  return (
    <div className={styles.container}>
      {/* ... (UI code from previous example) ... */}
    </div>
  );
}

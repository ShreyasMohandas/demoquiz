import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './Chatbot.css';

function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const sendMessage = async () => {
    if (input.trim() === '') return;
    
    setIsTyping(true);
    const userMessage = { text: input, isUser: true, timestamp: new Date() };
    setMessages(prevMessages => [...prevMessages, userMessage]);
    setInput('');

    try {
      const response = await axios.post('http://localhost:8001/chat/', {
        text: input,
      });
      const botMessage = { text: response.data.response, isUser: false, timestamp: new Date() };
      setMessages(prevMessages => [...prevMessages, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = { text: 'Sorry, there was an error processing your request.', isUser: false, timestamp: new Date() };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    }

    setIsTyping(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const formatMessage = (message) => {
    const lines = message.split('\n');
  
    let inCodeBlock = false;
    let codeContent = '';
  
    return lines.reduce((formattedLines, line, index) => {
      const trimmedLine = line.trim();
  
      if (trimmedLine.startsWith('```')) {
        if (inCodeBlock) {
          formattedLines.push(
            <pre key={`code-${index}`}>
              <code>{codeContent}</code>
            </pre>
          );
          inCodeBlock = false;
          codeContent = '';
        } else {
          inCodeBlock = true;
        }
        return formattedLines;
      }
  
      if (inCodeBlock) {
        codeContent += line + '\n';
        return formattedLines;
      }
  
      if (trimmedLine.startsWith('* **')) {
        const parts = trimmedLine.split(':');
        const boldTextMatch = parts[0].match(/\*\*(.*?)\*\*/);
        if (boldTextMatch) {
          const boldText = boldTextMatch[1];
          formattedLines.push(
            <li key={index} className="bold-bullet">
              <strong>{boldText}:</strong> {parts.slice(1).join(':').trim()}
            </li>
          );
        } else {
          formattedLines.push(
            <li key={index} className="bold-bullet">
              {trimmedLine}
            </li>
          );
        }
      } else if (trimmedLine.startsWith('* ')) {
        formattedLines.push(
          <li key={index} className="regular-bullet">
            {trimmedLine.substring(2)}
          </li>
        );
      } else if (trimmedLine.startsWith('#')) {
        const level = trimmedLine.match(/^#+/)[0].length;
        const HeaderTag = `h${level}`;
        formattedLines.push(
          <HeaderTag key={index} className="llm-header">
            {trimmedLine.substring(level + 1).trim()}
          </HeaderTag>
        );
      } else if (trimmedLine.match(/^(-{3,}|\*{3,})$/)) {
        formattedLines.push(<hr key={index} className="llm-hr" />);
      } else if (trimmedLine.includes('`')) {
        const parts = trimmedLine.split('`');
        const formattedParts = parts.map((part, i) =>
          i % 2 === 0 ? part : <code key={`inline-${i}`}>{part}</code>
        );
        formattedLines.push(<p key={index}>{formattedParts}</p>);
      } else {
        formattedLines.push(<p key={index} className="llm-text">{trimmedLine}</p>);
      }
  
      return formattedLines;
    }, []);
  };

  

  useEffect(scrollToBottom, [messages]);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  return (
    <div className="container">
      <div className="body_block">
        <div className="chatbot-container">
          <div className="chatbot-header">
            <h2>AI Assistant</h2>
            <span>{new Date().toLocaleDateString()}</span>
          </div>
          <div className="messages-container">
            {messages.map((message, index) => (
              <div key={index} className={`message ${message.isUser ? 'user-message' : 'bot-message'}`}>
                <div className="message-content">
                  <span className="message-text">{formatMessage(message.text)}</span>
                  <span className="message-timestamp">{message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                </div>
              </div>
            ))}
            {isTyping && <div className="typing-indicator">AI is typing...</div>}
            <div ref={messagesEndRef} />
          </div>
          <div className="input-container">
            <input 
              ref={inputRef}
              value={input} 
              onChange={e => setInput(e.target.value)} 
              onKeyPress={handleKeyPress}
              placeholder="Type your message here..."
              className="input-field" 
            />
            <button onClick={sendMessage} className="send-button">Send</button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Chatbot;
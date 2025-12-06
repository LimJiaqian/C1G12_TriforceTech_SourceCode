/**
 * Frontend Integration Guide for Voice-to-RAG
 * 
 * This file provides example code for integrating the Voice-to-RAG backend
 * with your React frontend.
 */

// ============================================
// 1. TEXT QUERY EXAMPLE
// ============================================

export async function sendTextQuery(queryText) {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/chat-enquiry', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text: queryText })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Text query error:', error);
    throw error;
  }
}

// Usage:
// const result = await sendTextQuery("How much energy can I donate?");
// console.log(result.response);


// ============================================
// 2. AUDIO QUERY EXAMPLE (Pre-recorded File)
// ============================================

export async function sendAudioFile(audioFile) {
  try {
    const formData = new FormData();
    formData.append('audio', audioFile);

    const response = await fetch('http://127.0.0.1:5000/api/chat-enquiry', {
      method: 'POST',
      body: formData
      // Note: Don't set Content-Type header - browser will set it automatically with boundary
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Audio query error:', error);
    throw error;
  }
}

// Usage:
// <input type="file" accept="audio/*" onChange={(e) => {
//   const file = e.target.files[0];
//   sendAudioFile(file).then(result => console.log(result.response));
// }} />


// ============================================
// 3. REACT COMPONENT EXAMPLE - Audio Recording
// ============================================

import React, { useState, useRef } from 'react';
import { Mic, Square, Send } from 'lucide-react';

export function VoiceChat() {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [response, setResponse] = useState('');
  const [transcript, setTranscript] = useState('');
  
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        await sendAudioToBackend(audioBlob);
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
      alert('Failed to access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const sendAudioToBackend = async (audioBlob) => {
    setIsProcessing(true);
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');

      const response = await fetch('http://127.0.0.1:5000/api/chat-enquiry', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setTranscript(data.query);
      setResponse(data.response);
    } catch (error) {
      console.error('Error sending audio:', error);
      alert('Failed to process audio. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="p-6 bg-white rounded-xl shadow-lg">
      <h3 className="text-xl font-bold mb-4">Voice Chat</h3>
      
      {/* Recording Controls */}
      <div className="flex gap-3 mb-4">
        {!isRecording ? (
          <button
            onClick={startRecording}
            disabled={isProcessing}
            className="flex items-center gap-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:opacity-50"
          >
            <Mic size={20} />
            Start Recording
          </button>
        ) : (
          <button
            onClick={stopRecording}
            className="flex items-center gap-2 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-800"
          >
            <Square size={20} />
            Stop Recording
          </button>
        )}
      </div>

      {/* Processing Indicator */}
      {isProcessing && (
        <div className="mb-4 p-3 bg-blue-50 rounded-lg">
          <p className="text-blue-700">Processing audio...</p>
        </div>
      )}

      {/* Transcript Display */}
      {transcript && (
        <div className="mb-4 p-4 bg-gray-50 rounded-lg">
          <p className="text-sm text-gray-600 mb-1">Your question:</p>
          <p className="text-gray-900">{transcript}</p>
        </div>
      )}

      {/* Response Display */}
      {response && (
        <div className="p-4 bg-purple-50 rounded-lg">
          <p className="text-sm text-purple-600 mb-1">AI Response:</p>
          <p className="text-gray-900">{response}</p>
        </div>
      )}
    </div>
  );
}


// ============================================
// 4. INTEGRATED WITH EXISTING CHATPANEL
// ============================================

import React, { useState } from 'react';
import { Mic, Send } from 'lucide-react';

export function EnhancedChatPanel({ onClose }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  // Text message handler
  const sendTextMessage = async () => {
    if (!input.trim() || isProcessing) return;

    const userMessage = input;
    setMessages(prev => [...prev, { sender: 'user', text: userMessage }]);
    setInput('');
    setIsProcessing(true);

    try {
      const response = await fetch('http://127.0.0.1:5000/api/chat-enquiry', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: userMessage })
      });

      const data = await response.json();
      setMessages(prev => [...prev, { sender: 'ai', text: data.response }]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, { 
        sender: 'ai', 
        text: 'Sorry, I encountered an error. Please try again.' 
      }]);
    } finally {
      setIsProcessing(false);
    }
  };

  // Voice message handler
  const handleVoiceMessage = async (audioBlob) => {
    setMessages(prev => [...prev, { sender: 'user', text: '🎤 Voice message...' }]);
    setIsProcessing(true);

    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'voice.webm');

      const response = await fetch('http://127.0.0.1:5000/api/chat-enquiry', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      
      // Update user message with transcript
      setMessages(prev => {
        const updated = [...prev];
        updated[updated.length - 1] = { sender: 'user', text: data.query };
        return updated;
      });
      
      // Add AI response
      setMessages(prev => [...prev, { sender: 'ai', text: data.response }]);
    } catch (error) {
      console.error('Voice error:', error);
      setMessages(prev => [...prev, { 
        sender: 'ai', 
        text: 'Sorry, I couldn\'t process your voice message.' 
      }]);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="chat-panel">
      {/* Chat messages */}
      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.sender}`}>
            {msg.text}
          </div>
        ))}
      </div>

      {/* Input area */}
      <div className="input-area flex gap-2">
        <button
          onClick={() => {/* Implement voice recording */}}
          disabled={isProcessing}
          className="p-2 rounded-full bg-red-500 text-white hover:bg-red-600"
        >
          <Mic size={20} />
        </button>
        
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendTextMessage()}
          placeholder="Type or use voice..."
          className="flex-1 px-4 py-2 border rounded-lg"
        />
        
        <button
          onClick={sendTextMessage}
          disabled={isProcessing}
          className="p-2 rounded-full bg-purple-500 text-white hover:bg-purple-600"
        >
          <Send size={20} />
        </button>
      </div>
    </div>
  );
}


// ============================================
// 5. SUPPORTED AUDIO FORMATS
// ============================================

const SUPPORTED_FORMATS = [
  'audio/mp3',
  'audio/wav',
  'audio/flac',
  'audio/ogg',
  'audio/m4a',
  'audio/webm'
];

export function validateAudioFile(file) {
  const maxSize = 50 * 1024 * 1024; // 50MB
  
  if (file.size > maxSize) {
    throw new Error('File size exceeds 50MB limit');
  }
  
  if (!SUPPORTED_FORMATS.some(format => file.type.includes(format.split('/')[1]))) {
    throw new Error('Unsupported audio format. Use mp3, wav, flac, ogg, m4a, or webm');
  }
  
  return true;
}


// ============================================
// 6. ERROR HANDLING UTILITIES
// ============================================

export function handleAPIError(error, response) {
  if (response?.status === 400) {
    return 'Invalid request. Please check your input.';
  } else if (response?.status === 500) {
    return 'Server error. Please try again later.';
  } else if (error.message.includes('network')) {
    return 'Network error. Please check your connection.';
  } else {
    return 'An unexpected error occurred. Please try again.';
  }
}
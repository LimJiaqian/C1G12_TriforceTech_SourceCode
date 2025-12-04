/**
 * JAM AI API SERVICE
 * 
 * This service handles all communication with the Jam AI backend.
 * It includes retry logic, error handling, and response parsing.
 */

import { JAM_AI_CONFIG } from '../config/jamAI.config';

// Define the Base URL once (Easy to change later)
const API_BASE_URL = "http://127.0.0.1:5000";

/**
 * Sends a message to the Jam AI backend and retrieves the processed response
 * 
 * @param {string} userText - The user's input text
 * @returns {Promise<string>} - The AI's response from the Final_response column
 * @throws {Error} - If the API call fails after retries
 */
export async function sendMessageToJamAI(userText) {
  let lastError = null;

  // Debug: Log configuration
  console.log("=== JamAI API Call Debug ===");
  console.log("Endpoint:", JAM_AI_CONFIG.ENDPOINT);
  console.log("Project ID:", JAM_AI_CONFIG.PROJECT_ID);
  console.log("Table ID:", JAM_AI_CONFIG.TABLE_ID);
  console.log("API Key exists:", !!JAM_AI_CONFIG.API_KEY);
  console.log("Input Column:", JAM_AI_CONFIG.COLUMNS.INPUT);
  console.log("User Text:", userText);

  // Retry logic
  for (let attempt = 0; attempt <= JAM_AI_CONFIG.RETRY_ATTEMPTS; attempt++) {
    try {
      // Add delay between retries (but not on first attempt)
      if (attempt > 0) {
        await new Promise(resolve => setTimeout(resolve, JAM_AI_CONFIG.RETRY_DELAY));
        console.log(`Retry attempt ${attempt}/${JAM_AI_CONFIG.RETRY_ATTEMPTS}`);
      }

      const requestBody = {
        table_id: JAM_AI_CONFIG.TABLE_ID,
        data: [
          {
            [JAM_AI_CONFIG.COLUMNS.INPUT]: userText
          }
        ],
        stream: false
      };

      console.log("Request Body:", JSON.stringify(requestBody, null, 2));

      const response = await fetchWithTimeout(
        JAM_AI_CONFIG.ENDPOINT,
        {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${JAM_AI_CONFIG.API_KEY}`,
            "Content-Type": "application/json",
            "X-PROJECT-ID": JAM_AI_CONFIG.PROJECT_ID
          },
          body: JSON.stringify(requestBody)
        },
        JAM_AI_CONFIG.TIMEOUT
      );

      console.log("Response status:", response.status);
      console.log("Response OK:", response.ok);

      if (!response.ok) {
        const errorText = await response.text();
        console.error("API Error Response:", errorText);
        throw new Error(`API Error: ${response.status} ${response.statusText} - ${errorText}`);
      }

      const result = await response.json();
      console.log("API Response:", JSON.stringify(result, null, 2));
      
      // Parse the response - adjust based on your actual API response structure
      const finalResponse = extractFinalResponse(result);
      
      if (!finalResponse) {
        console.warn("Could not extract Final_response from result");
        throw new Error("No valid response received from AI");
      }

      console.log("Extracted response:", finalResponse);
      return finalResponse;

    } catch (error) {
      lastError = error;
      console.error(`Attempt ${attempt + 1} failed:`, error.message);
      
      // Don't retry on certain errors
      if (error.message.includes('401') || error.message.includes('403')) {
        throw new Error("Authentication failed. Please check your API credentials.");
      }
    }
  }

  // All retries failed
  throw lastError || new Error("Failed to connect to Jam AI");
}

/**
 * Extracts the Final_response from the JamAI Base API result
 * Final Clean Parser - handles OpenAI-style response structure
 */
function extractFinalResponse(data) {
  console.log("=== Extracting Final_response ===");
  console.log("Raw API Response:", JSON.stringify(data, null, 2));
  
  try {
    // --- FINAL CLEAN PARSER ---
    // 1. Find the column (Case Insensitive)
    const columns = data.rows[0].columns;
    const targetKey = Object.keys(columns).find(key => 
      key.toLowerCase().includes("final_response")
    );

    let botText = "";

    if (targetKey) {
      const cellData = columns[targetKey];

      // 2. Extract text based on the structure seen in logs
      if (typeof cellData === 'object' && cellData !== null) {
        if (cellData.choices && cellData.choices[0] && cellData.choices[0].message) {
          // Structure: { choices: [ { message: { content: "..." } } ] }
          botText = cellData.choices[0].message.content;
        } else if (cellData.text) {
          // Fallback: Standard JamAI text field
          botText = cellData.text;
        } else if (cellData.value) {
          // Fallback: Value field
          botText = cellData.value;
        } else {
          // Fallback: If it's just a raw object, try to stringify it cleanly
          botText = JSON.stringify(cellData);
        }
      } else {
        // It's already a string
        botText = String(cellData);
      }
    }

    // 3. Final cleanup (remove quotes if they got stuck)
    if (botText) {
      botText = botText.replace(/^"|"$/g, '').trim();
    } else {
      botText = "Sorry, I couldn't generate a response.";
    }

    return botText;
    
  } catch (error) {
    console.error("Error extracting response:", error);
    return "Error parsing the AI response.";
  }
}

/**
 * Fetch with timeout support
 */
function fetchWithTimeout(url, options, timeout) {
  return Promise.race([
    fetch(url, options),
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error('Request timeout')), timeout)
    )
  ]);
}

/**
 * Sends audio to backend for transcription and RAG processing
 * 
 * @param {Blob} audioBlob - The recorded audio blob
 * @returns {Promise<string>} - The AI's response text
 * @throws {Error} - If the upload or processing fails
 */
export async function sendAudioToBackend(audioBlob) {
  const formData = new FormData();
  formData.append("audio", audioBlob, "recording.webm");

  console.log("📤 Sending audio to backend:");
  console.log("- Blob size:", audioBlob.size, "bytes");
  console.log("- Blob type:", audioBlob.type);

  try {
    const response = await fetch(`${API_BASE_URL}/api/chat-enquiry`, {
      method: "POST",
      body: formData,
    });

    console.log("📥 Backend response status:", response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error("❌ Backend error response:", errorText);
      throw new Error(`Server error: ${response.status}`);
    }

    const data = await response.json();
    console.log("✅ Backend response data:", data);

    // Return just the AI text response
    return data.response || "I processed your voice message successfully! 🎉";
  } catch (error) {
    console.error("❌ Audio Upload Error:", error);
    throw error;
  }
}

/**
 * Test the Jam AI connection
 * Useful for debugging
 */
export async function testJamAIConnection() {
  try {
    console.log("Testing Jam AI connection...");
    console.log("Endpoint:", JAM_AI_CONFIG.ENDPOINT);
    
    const response = await sendMessageToJamAI("Hello, this is a test message.");
    
    console.log("Connection successful!");
    console.log("Response:", response);
    
    return { success: true, response };
  } catch (error) {
    console.error("Connection failed:", error.message);
    return { success: false, error: error.message };
  }
}

/**
 * JAM AI CONFIGURATION
 * 
 * This file contains the configuration for connecting to your Jam AI backend.
 * Update these values with your actual Jam AI credentials and endpoint.
 */

export const JAM_AI_CONFIG = {
  // JamAI Base API endpoint URL
  ENDPOINT: import.meta.env.VITE_JAM_API_ENDPOINT || "https://api.jamaibase.com/v1/gen_tables/action/rows/add",
  
  // Your API key
  API_KEY: import.meta.env.VITE_JAM_API_KEY || "",
  
  // Project ID (required by JamAI Base)
  PROJECT_ID: import.meta.env.VITE_JAM_PROJECT_ID || "",
  
  // Table ID (CASE-SENSITIVE! Must be exactly "Chatbox")
  TABLE_ID: import.meta.env.VITE_JAM_TABLE_ID || "Chatbox",
  
  // Column names in your Jam AI table
  COLUMNS: {
    INPUT: "Input_text",
    OUTPUT: "Final_response"
  },
  
  // Request timeout in milliseconds (30 seconds default for AI processing)
  TIMEOUT: 30000,
  
  // Retry configuration
  RETRY_ATTEMPTS: 2,
  RETRY_DELAY: 1000, // milliseconds
};

/**
 * INSTRUCTIONS FOR SETUP:
 * 
 * 1. Create a .env file in the root of your SolarAid_App directory
 * 2. Add these variables (note: Vite requires VITE_ prefix):
 *    VITE_JAM_AI_ENDPOINT=https://your-jam-ai-endpoint.com/api/v1/...
 *    VITE_JAM_AI_API_KEY=your-api-key-here
 *    VITE_JAM_AI_ORG_ID=your-org-id-here
 * 
 * 3. Restart your dev server after creating/updating .env
 * 
 * For Jam AI Base specifically:
 * - Get your endpoint from the Jam AI dashboard
 * - Format: https://api.jamaibase.com/api/v1/gen_tables/{PROJECT_ID}/{TABLE_ID}/chat
 * - Or use the row add endpoint if applicable
 */

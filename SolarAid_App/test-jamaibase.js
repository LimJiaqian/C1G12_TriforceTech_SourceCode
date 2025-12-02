/**
 * TEST FILE - JamAI Base Connection Test
 * 
 * Run this in your browser console to test the JamAI Base API connection
 */

const testJamAIConnection = async () => {
  const config = {
    endpoint: "/jam-api/api/v1/gen_tables/action/rows/add",
    projectId: "proj_7ae3e9429c658e092cf88c26",
    tableId: "Chatbox",
    apiKey: "jamai_pat_020559435940aa3d98e4bc8c1d40f85a45a9925c21e748c5"
  };

  console.log("Testing JamAI Base connection...");
  console.log("Config:", config);

  try {
    const response = await fetch(config.endpoint, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${config.apiKey}`,
        "Content-Type": "application/json",
        "X-PROJECT-ID": config.projectId
      },
      body: JSON.stringify({
        table_id: config.tableId,
        data: [{
          "Input_text": "Test message"
        }],
        stream: false
      })
    });

    console.log("Response status:", response.status);
    console.log("Response OK:", response.ok);

    const text = await response.text();
    console.log("Response text:", text);

    if (response.ok) {
      const json = JSON.parse(text);
      console.log("✅ SUCCESS! Response:", json);
    } else {
      console.log("❌ FAILED:", text);
    }
  } catch (error) {
    console.error("❌ ERROR:", error);
  }
};

// Run the test
testJamAIConnection();

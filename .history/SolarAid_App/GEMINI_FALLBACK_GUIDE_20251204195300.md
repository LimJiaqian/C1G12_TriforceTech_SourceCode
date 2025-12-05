# Fallback Logic Implementation Guide

## 🎯 What This Does

When your JamAI Action Table returns the exact string `"FALLBACK_MODE"`, the system automatically switches to Google Gemini to generate the response.

---

## 📦 Installation Commands

Run these commands in your terminal (inside the `SolarAid_App` directory):

```powershell
# Install Google Generative AI library
pip install google-generativeai

# Or add to requirements.txt and install all
pip install -r requirements.txt
```

### Update `requirements.txt`

Add this line to your `requirements.txt`:

```txt
google-generativeai>=0.3.0
```

---

## 🔑 Environment Variables

Add your Gemini API key to the `.env` file:

```env
# Google Gemini Configuration (for fallback)
GEMINI_API_KEY=your_gemini_api_key_here
```

**Get your API key:** https://makersuite.google.com/app/apikey

---

## 🔄 How It Works

### **Flow Diagram:**

```
User Query
    ↓
[Query JamAI Action Table]
    ↓
Check Response
    ├─→ IF Response == "FALLBACK_MODE"
    │       ↓
    │   [Call Google Gemini API]
    │       ↓
    │   Return Gemini Response
    │
    └─→ ELSE
            ↓
        Return JamAI Response
```

### **Code Logic:**

```python
# Step 1: Query JamAI Action Table
response_text = query_jamai_action_table(user_query)

# Step 2: Check for FALLBACK_MODE
if response_text.strip() == "FALLBACK_MODE":
    # Step 3a: Use Gemini fallback
    gemini_response = handle_fallback(user_query)
    return gemini_response
else:
    # Step 3b: Return JamAI response normally
    return response_text
```

---

## 📝 Implementation Details

### **Function: `handle_fallback(user_query)`**

```python
def handle_fallback(user_query: str) -> str:
    """
    Fallback handler using Google Gemini when JamAI returns FALLBACK_MODE
    
    Args:
        user_query (str): The user's original query
        
    Returns:
        str: Response from Google Gemini
    """
    # Initialize Gemini 1.5 Flash model
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        system_instruction="You are a helpful, friendly assistant. Answer the user naturally."
    )
    
    # Generate response
    response = model.generate_content(user_query)
    return response.text
```

### **Main Logic Block:**

```python
def query_jamai_chat(query_text: str, table_id: str = "Chatbox") -> dict:
    # Query JamAI Action Table
    response_text = jamai.table.add_table_rows(...)
    
    # Check for FALLBACK_MODE trigger
    if response_text.strip() == "FALLBACK_MODE":
        print("🔄 FALLBACK_MODE detected - switching to Google Gemini")
        
        # Use Gemini as fallback
        gemini_response = handle_fallback(query_text)
        
        return {
            "success": True,
            "response": gemini_response,
            "fallback_used": True,
            "fallback_provider": "Google Gemini"
        }
    
    # Return JamAI response normally
    return {
        "success": True,
        "response": response_text,
        "fallback_used": False
    }
```

---

## 🧪 Testing

### **Test Case 1: Normal JamAI Response**

```bash
# JamAI returns: "Solar energy is renewable..."
# Result: Frontend displays JamAI response
```

### **Test Case 2: Fallback Mode Triggered**

```bash
# JamAI returns: "FALLBACK_MODE"
# Result: System calls Gemini and displays Gemini response
```

### **How to Trigger Fallback in JamAI:**

In your JamAI Action Table, configure a column to return `"FALLBACK_MODE"` when certain conditions are met:

```
IF knowledge_base_empty OR confidence_low:
    OUTPUT = "FALLBACK_MODE"
ELSE:
    OUTPUT = rag_response
```

---

## 📊 Response Structure

### **Normal Response (JamAI):**

```json
{
  "success": true,
  "response": "Solar energy is a renewable energy source...",
  "table_id": "Chatbox",
  "fallback_used": false
}
```

### **Fallback Response (Gemini):**

```json
{
  "success": true,
  "response": "Solar energy is generated from the sun...",
  "table_id": "Chatbox",
  "fallback_used": true,
  "fallback_provider": "Google Gemini"
}
```

---

## 🔍 Debugging

### **Check Logs:**

```
✅ Received response from JamAI: FALLBACK_MODE
🔄 FALLBACK_MODE detected - switching to Google Gemini
✅ Gemini response generated: 245 characters
```

### **Common Issues:**

1. **"GEMINI_API_KEY not found"**
   - Solution: Add `GEMINI_API_KEY` to `.env` file

2. **Gemini fallback fails**
   - Check API key validity
   - Verify internet connection
   - Check Gemini API quotas

3. **FALLBACK_MODE not triggering**
   - Ensure JamAI returns exactly `"FALLBACK_MODE"` (case-sensitive, no extra spaces)
   - Check JamAI Action Table configuration

---

## 🚀 Benefits

✅ **Graceful degradation:** System never fails completely  
✅ **Flexible routing:** JamAI controls when to use fallback  
✅ **Cost optimization:** Use JamAI for RAG, Gemini for general queries  
✅ **Better UX:** Users always get a response  

---

## 💡 Use Cases

1. **Knowledge Base Empty:** When RAG has no relevant documents
2. **Low Confidence:** When JamAI confidence score is below threshold
3. **Out of Domain:** When user asks questions outside your knowledge base
4. **Testing:** Easy A/B testing between JamAI and Gemini responses

---

## 🎛️ Configuration Options

### **Customize System Instruction:**

```python
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction="""
    You are a SolarAid assistant specializing in renewable energy.
    Provide accurate, friendly responses about solar energy donations.
    If you don't know something, admit it honestly.
    """
)
```

### **Use Different Gemini Model:**

```python
# For more complex queries
model = genai.GenerativeModel(model_name='gemini-1.5-pro')

# For faster responses
model = genai.GenerativeModel(model_name='gemini-1.5-flash')
```

---

## ✅ Installation Checklist

- [ ] Install `google-generativeai` library
- [ ] Add `GEMINI_API_KEY` to `.env` file
- [ ] Configure JamAI Action Table to return `"FALLBACK_MODE"` when needed
- [ ] Test fallback with a sample query
- [ ] Monitor logs to ensure fallback triggers correctly

---

## 📚 Additional Resources

- **Gemini API Docs:** https://ai.google.dev/docs
- **Get API Key:** https://makersuite.google.com/app/apikey
- **Gemini Pricing:** https://ai.google.dev/pricing

---

## 🎉 Done!

Your system now has intelligent fallback logic. When JamAI can't handle a query, Gemini steps in automatically! 🚀

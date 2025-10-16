# RAG Prompt Engineering Guide

## Current Prompt Strategy

### Problem Solved
**Before:** AI was adding extra information not requested by the user
- User asks: "Where is the college?"
- AI responds: Address + phone + WhatsApp + email (too much!)

**After:** AI answers ONLY what was asked
- User asks: "Where is the college?"
- AI responds: Just the address ✅

### Prompt Instructions

Located in `server/rag_pipeline.py` (lines ~210-230):

```python
Instructions:
- Answer ONLY what the student asked - no extra information
- If they ask for location, give ONLY the address
- If they ask for contact, give ONLY contact details
- If they ask for a specific detail, provide ONLY that detail
- Use ONLY information from the context above
- Be direct and concise (1-2 sentences)
- Don't add unrequested details like phone numbers, addresses, etc.
```

## Example Behavior

### Query: "Where is Sunway College?"
**Expected Response:**
```
Sunway College is located Behind Maitidevi Temple, Maitidevi, Kathmandu, Nepal.
```

**NOT:**
```
Sunway College is located Behind Maitidevi Temple, Maitidevi, Kathmandu, Nepal. 
You can also reach out by phone at [PHONE] or SMS/Whatsapp at 9823047066.
```

### Query: "How do I contact Sunway College?"
**Expected Response:**
```
You can reach Sunway College by phone at [PHONE] or SMS/WhatsApp at 9823047066. 
Email: info@sunwaycollege.edu.np
```

### Query: "What courses are offered?"
**Expected Response:**
```
Sunway College offers BBA, BIM, BBM, BSc.CSIT, and BCA programs.
```

## Testing the Prompt

### Restart Server
```bash
# Apply changes
python run_server.py
```

### Test Queries (Text Mode)
```bash
python client.py
# Choose: t (text mode)

# Test specific queries:
"Where is the college?"
"What's the phone number?"
"Tell me about courses"
"What are the fees?"
```

### Test Queries (Voice Mode)
```bash
python client.py
# Choose: v (voice mode)

# Speak clearly:
"Where is Sunway College located?"
```

## Tuning the Prompt

If responses are still too verbose or too brief, edit `server/rag_pipeline.py`:

### Make More Concise
```python
- Be direct and concise (1 sentence maximum)
- Give only the essential fact requested
```

### Make More Detailed
```python
- Be helpful and informative (2-3 sentences)
- Provide context when useful
```

### Add Personality
```python
- Use a friendly, helpful tone
- Add "Let me know if you need anything else!"
```

## Current Settings

- **Model:** gemini-2.0-flash-exp
- **Context:** Top 5 retrieved documents
- **Max Response:** 1-2 sentences
- **Behavior:** Answer ONLY what's asked

---

**After updating the prompt, always restart the server!**
```bash
python run_server.py
```

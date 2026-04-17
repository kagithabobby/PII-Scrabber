🔐 Privacy-Preserving LLM Middleware

A production-ready backend system that enables secure interaction with Large Language Models (LLMs) by anonymizing sensitive user data before processing and restoring it after response generation.

🚀 Live Demo

👉 https://pii-scrabber.onrender.com/docs

🧠 Problem Statement

Organizations cannot directly send user data (emails, phone numbers, personal details) to AI models due to privacy and compliance risks.

This project solves that problem by acting as a middleware security layer between users and AI systems.

💡 Solution

This system:

Detects sensitive data (PII)
Replaces it with placeholders
Sends safe input to LLM
Restores original data in the response
⚙️ Architecture
User Input
   ↓
PII Detection (Regex)
   ↓
Mask + Mapping
   ↓
Send to LLM (OpenRouter)
   ↓
Receive Response
   ↓
Rehydrate (Restore Data)
   ↓
Final Output
🛠️ Tech Stack
Backend: FastAPI
Language: Python
AI API: OpenRouter
Model: Nemotron / LLaMA-based models
Deployment: Render
Version Control: Git & GitHub
✨ Features
🔒 PII Detection (Email, Phone)
🔄 Unique Placeholder Mapping
🤖 Real-time LLM Integration
♻️ Response Rehydration
🌐 Live API Deployment
⚙️ Modular Backend Structure
📦 API Usage
Endpoint: /chat
Request
{
  "text": "My email is abc@gmail.com. Explain AI simply."
}
Response
{
  "original": "...",
  "masked": "...",
  "llm_response": "...",
  "final_response": "..."
}
🔑 Environment Variables

Set this in your deployment environment:

OPENROUTER_API_KEY=your_api_key_here
🚀 Run Locally
git clone <your-repo-url>
cd pii-scrubber
pip install -r requirements.txt
uvicorn main:app --reload
🧪 Example Use Cases
Secure AI chat applications
Enterprise AI compliance layers
Privacy-first AI assistants
Data anonymization pipelines
⚠️ Challenges Faced
Handling API authentication errors
Managing environment variables in production
Preventing backend crashes (500 errors)
Ensuring reversible data transformation
📈 Future Improvements
Add support for more PII types (Aadhaar, Names, Addresses)
Integrate frontend (React UI)
Add authentication & rate limiting
Implement logging & monitoring
Use ML-based PII detection instead of regex
👨‍💻 Author

Kagitha Bobby

⭐ If you like this project

Give it a ⭐ on GitHub!
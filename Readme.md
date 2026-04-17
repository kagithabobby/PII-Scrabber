# 🔐 Privacy-Preserving LLM Middleware

A production-ready backend system that enables **secure interaction with Large Language Models (LLMs)** by anonymizing sensitive user data before processing and restoring it after response generation.

---

## 🚀 Live Demo

👉 https://pii-scrabber.onrender.com/docs

---

## 🧠 Problem Statement

Organizations cannot directly send sensitive user data (emails, phone numbers, personal information) to AI models due to **privacy, security, and compliance risks**.

This project solves that problem by acting as a **middleware security layer** between users and AI systems.

---

## 💡 Solution

This system:

* Detects sensitive data (PII)
* Replaces it with unique placeholders
* Sends anonymized input to the LLM
* Restores original data in the final response

---

## ⚙️ Architecture

```
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
```

---

## 🛠️ Tech Stack

* **Backend:** FastAPI
* **Language:** Python
* **AI API:** OpenRouter
* **Model:** Nemotron / LLaMA-based models
* **Deployment:** Render
* **Version Control:** Git & GitHub

---

## ✨ Features

* 🔒 PII Detection (Email, Phone)
* 🔄 Unique Placeholder Mapping System
* 🤖 Real-time LLM Integration
* ♻️ Response Rehydration
* 🌐 Live API Deployment
* ⚙️ Modular Backend Architecture

---

## 📦 API Usage

### Endpoint: `/chat`

### 🔹 Request

```json
{
  "text": "My email is abc@gmail.com. Explain AI simply."
}
```

### 🔹 Response

```json
{
  "original": "...",
  "masked": "...",
  "llm_response": "...",
  "final_response": "..."
}
```

---

## 🔑 Environment Variables

Set this in your deployment environment:

```
OPENROUTER_API_KEY=your_api_key_here
```

---

## 🚀 Run Locally

```bash
git clone <your-repo-url>
cd pii-scrubber
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## 🧪 Example Use Cases

* Secure AI chat applications
* Enterprise AI compliance systems
* Privacy-first AI assistants
* Data anonymization pipelines

---

## ⚠️ Challenges Faced

* Handling API authentication failures (401 errors)
* Managing environment variables in production
* Debugging deployment issues on cloud platforms
* Preventing backend crashes (500 errors)
* Ensuring reversible data transformation

---

## 📈 Future Improvements

* Support for more PII types (Aadhaar, Names, Addresses)
* Frontend integration (React UI)
* Authentication & rate limiting
* Logging and monitoring system
* ML-based PII detection (NER models)

---

## 👨‍💻 Author

**Kagitha Bobby**

---

## ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub!

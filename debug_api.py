import requests
import json

MODEL_NAME = "ai-optum"  # Make sure to create this model using 'ollama create ai-optum -f Modelfile'
API_URL = "http://localhost:11434/api/chat"
SYSTEM_PROMPT = "You are AI Optum, a professional AI Optometrist. Conduct preliminary eye exams with clinical precision."

payload = {
    "model": MODEL_NAME,
    "messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "I am ready to start my eye examination."}
    ],
    "stream": False
}

print("Sending request to local AI Optum engine...")
try:
    response = requests.post(API_URL, json=payload, timeout=30)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"AI Optum: {result['message']['content']}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Connection failed: {str(e)}")
    print("Ensure Ollama is running and the 'ai-optum' model has been created.")

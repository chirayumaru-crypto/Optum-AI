# How to Test "AI Optum - AI Optometrist"

Since this model runs locally on your machine, you need to use **Ollama**.

## Prerequisite: Install Ollama
If you haven't already:
1.  Download Ollama from [ollama.com](https://ollama.com/download/windows).
2.  Install it.
3.  Open a new terminal/command prompt to ensure it's in your PATH.

---

## Method 1: The Quick Terminal Test (Recommended)

This is the fastest way to chat with the model.

1.  **Open PowerShell** in the folder `c:\Users\chirayu.maru\Downloads\AI Optum`.
2.  **Create the custom model** from the Modelfile:
    ```powershell
    ollama create ai-optum -f Modelfile
    ```
    *(This might take a minute as it processes the system prompt and base model)*

3.  **Run the model**:
    ```powershell
    ollama run ai-optum
    ```
4.  **Chat!**
    *   Type: `Hello!`
    *   Type: `I am ready for my eye exam.`
    *   Type: `What is your role?`
    *   *Result:* The model should respond professionally as AI Optum, guiding you through an eye exam.

---

## Method 2: Using the Python Script

If you want to test it via code (like an API):

1.  **Ensure the model is created** (Step 2 in Method 1).
2.  **Run the provided script**:
    ```powershell
    python test_agent.py
    ```
3.  This script runs a comprehensive test suite including:
    *   Response Parsing
    *   Phoropter Control Logic
    *   LLM Engine Steering
    *   Safety Guardrails
    *   Full Exam Flow Simulation

## Method 3: Debug API Test

For a quick API connectivity test:

1.  **Run the debug script**:
    ```powershell
    python debug_api.py
    ```
2.  This verifies that the Ollama server is reachable and the `ai-optum` model is responding correctly.

## Troubleshooting

*   **"ollama: The term 'ollama' is not recognized..."**
    *   Restart your terminal or computer after installing Ollama.
*   **"Error: model 'ai-optum' not found"**
    *   You forgot to run `ollama create ai-optum -f Modelfile`.
*   **Model gives non-clinical or casual answers**
    *   Ensure you are running the `ai-optum` model and not the base `llama3` model.
    *   Check `Modelfile` to ensure the `SYSTEM` block is correctly formatted.
    *   If steering is enabled, ensure `steering_vectors.pt` is present in the directory.

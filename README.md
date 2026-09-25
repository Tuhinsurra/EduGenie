# EduGenie: Google Gemini Powered Learning Assistant 💡

EduGenie is a lightweight AI-powered educational assistant that simplifies learning through generative AI. Designed for students of all academic levels, EduGenie enables users to ask questions, understand complex topics, generate interactive quizzes, summarize passages, and receive structured learning roadmaps.

---

## 🏗️ Project Architecture

```text
EduGenie/
├── main.py                     # Root FastAPI entrypoint (uvicorn main:app --reload)
├── qna.py                      # Question answering module (Milestone 1)
├── explanation_module.py       # Concept explanation module (Milestone 1)
├── quiz_module.py              # Quiz generation module (Milestone 1)
├── summary_module.py           # Summarization module (Milestone 1)
├── learning_path.py            # Adaptive learning recommendations (Milestone 1)
├── app/
│   ├── main.py                 # FastAPI application core & route endpoints
│   ├── config.py               # Pydantic configuration & environment variables
│   ├── schemas.py              # Pydantic data models & request/response schemas
│   ├── services/
│   │   ├── gemini_service.py   # Google Gemini API client integration
│   │   ├── explanation_module.py # Explanation logic (with Gemini fallback)
│   │   ├── local_explainer.py  # Local LaMini-Flan-T5 model loader (optional)
│   │   ├── quiz_module.py      # MCQ generator & structured validator
│   │   ├── summary_module.py   # Paragraph summarizer
│   │   └── learning_path.py    # Structured learning roadmap generator
│   ├── templates/
│   │   └── index.html          # Interactive Web UI (All Modules & Single Mode)
│   └── static/
│       ├── style.css           # Modern responsive card-based styling
│       └── app.js              # Interactive client script with live quiz checker
├── templates/
│   └── index.html              # Root templates copy for direct mounting
├── static/
│   ├── style.css               # Root static copy
│   └── app.js                  # Root script copy
├── tests/
│   └── test_api.py             # Automated unit & endpoint validation tests
├── .env.example                # Example environment variables
├── .env                        # Local configuration file (add your API key here)
├── requirements.txt            # Python dependencies
└── README.md                   # Complete setup, running, and testing guide
```

---

## 🚀 Quick Start Guide (VS Code Setup)

### Step 1: Open the Project in VS Code
1. Launch **Visual Studio Code**.
2. Click **File** &rarr; **Open Folder...** (or press `Ctrl + K, Ctrl + O`).
3. Select the `EduGenie` folder located on your Desktop:
   ```text
   C:\Users\tuhin\OneDrive\Desktop\EduGenie
   ```
4. Open the integrated terminal in VS Code:
   * Press `Ctrl + ~` (tilde) or go to menu **Terminal** &rarr; **New Terminal**.

---

### Step 2: Create & Activate Virtual Environment

In the VS Code terminal (PowerShell), run:

```powershell
# 1. Create a Python virtual environment named .venv
python -m venv .venv

# 2. Activate the virtual environment
.\.venv\Scripts\Activate.ps1
```

> **Note**: If you receive an execution policy warning in PowerShell, run:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> .\.venv\Scripts\Activate.ps1
> ```

You will see `(.venv)` in your terminal prompt when activated.

---

### Step 3: Install Dependencies

```powershell
# Upgrade pip to latest version
python -m pip install --upgrade pip

# Install all required dependencies
pip install -r requirements.txt
```

---

### Step 4: Configure Your Google Gemini API Key

1. Get a free API key from [Google AI Studio](https://aistudio.google.com/).
2. In VS Code, open the `.env` file in the project root.
3. Replace the placeholder with your actual Gemini API key:
   ```env
   GEMINI_API_KEY=AIzaSy...YourActualGeminiKeyHere...
   ```
4. Save the file (`Ctrl + S`).

---

### Step 5: Run the EduGenie Application

Run the server with Uvicorn:

```powershell
uvicorn main:app --reload
```

You should see output similar to:
```text
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Now open your web browser and navigate to:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

Interactive API Documentation (Swagger UI):
👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

---

## 🧪 Testing the 5 EduGenie Features

Open `http://127.0.0.1:8000` in your browser to test each feature:

### 1. Q&A Module (`/qa`)
* **Input**: `"Which is the largest ocean?"` or `"Why is the sky blue?"`
* **Action**: Click **Get Answer**.
* **Result**: EduGenie returns a direct, accurate, and concise answer.

### 2. Concept Explanation Module (`/explain`)
* **Input**: `"Photosynthesis"` or `"The Pythagoras Theorem"`
* **Action**: Click **Explain**.
* **Result**: Returns a beginner-friendly explanation with definition, analogy, and key points.

### 3. Summarization Module (`/summarize`)
* **Input**: Paste any long educational passage or article paragraph.
* **Action**: Click **Summarize**.
* **Result**: Generates a concise summary preserving key definitions and core takeaways.

### 4. Interactive Quiz Generator (`/quiz`)
* **Input**: `"Solar System"` or `"Pythagoras theorem"`
* **Action**: Click **Generate Quiz**.
* **Interactive Test**:
  * EduGenie renders 3 Multiple-Choice Questions (MCQs) with 4 options each.
  * Select an option for each question and click **Check Answer**.
  * The interface immediately verifies your selection:
    * ✅ **Correct!** (with explanation)
    * ❌ **Incorrect. Correct answer: ...**

### 5. Learning Path Recommendations (`/learn/recommendations`)
* **Input**: `"SQL"` or `"Linear Regression"`
* **Action**: Click **Get Recommendations**.
* **Result**: EduGenie builds a structured curriculum organized into Beginner, Intermediate, and Advanced stages with estimated timeframes, key concepts, curated resources, and adaptive study tips.

---

## 🔍 Automated Verification Tests

To verify that all routes and error validations work properly:

```powershell
pytest -q
```

---

## ⚙️ Advanced Configuration (`.env`)

* **Switch Models**: The default model is `gemini-1.5-flash` for high speed and generous quotas. To use Gemini 1.5 Pro, change:
  ```env
  GEMINI_MODEL=gemini-1.5-pro
  ```
* **Optional Local Model (LaMini-Flan-T5)**: To run the local HuggingFace model offline without API calls:
  1. Install PyTorch & Transformers:
     ```powershell
     pip install torch transformers sentencepiece
     ```
  2. Set `USE_LOCAL_EXPLAINER=true` in `.env`.
  3. On the first run, it will automatically download `MBZUAI/LaMini-Flan-T5-783M` (~3GB).

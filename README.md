# ⚖️ AI-Court Case Analyzer & Judicial Intelligence Platform

An AI-powered legal analytics web application designed to analyze Indian court case records, predict trial outcomes, assess bail/custody risk, and explore Indian Penal Code (IPC) statutory references.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![HuggingFace](https://img.shields.io/badge/Transformers-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)

---

## 🌟 Key Features

- 🧠 **InLegalBERT Outcome Predictor**: Deep neural classification (`Accepted`, `Other`, `Rejected`) based on fine-tuned InLegalBERT transformers with automatic target leakage stripping.
- 🔍 **Interactive Legal Search Engine**: Filter judicial records by State Jurisdiction, Police Station, Act Number / IPC Section, and Case CINO ID.
- ⚖️ **AI Outcome & Risk Predictor**: Evaluates case parameters to estimate disposition likelihood (Withdrawal / Compromise vs Full Trial), custody/bail risk levels, and predicted disposal timeframes.
- 📊 **Judicial Data Analytics**: Visualizes historical disposition trends, top registered IPC sections, and state-wise court caseload distributions.
- 📜 **IPC Statutory Reference Dictionary**: Instant access to IPC legal section definitions, statutory offenses, and maximum prescribed sentences.

---

## 🛠️ Technology Stack

- **Frontend / Framework**: Streamlit (with modern glassmorphic CSS styling)
- **Deep Learning / NLP**: Fine-tuned InLegalBERT (`transformers`, `torch`)
- **API Service**: FastAPI, Uvicorn, Pydantic
- **Data Engineering**: Pandas, NumPy, Scikit-Learn
- **Deployment Targets**: Streamlit Community Cloud, Render, HuggingFace Spaces

---

## 🤖 InLegalBERT Model Integration (`best_model/`)

The fine-tuned **InLegalBERT** model classifies legal case facts or judgment text into 3 outcomes:
1. `Accepted`
2. `Other`
3. `Rejected`

### ⚙️ Environment Variables

- `LEXICOURT_MODEL_DIR` or `MODEL_DIR`: Specifies the filesystem path to the unzipped HuggingFace model directory containing `config.json`, `model.safetensors`, `tokenizer.json`, and `label_mapping.json`.
- **Default**: `./best_model`

### 💻 Running Locally

#### 1. Streamlit Web App (Direct Integration)
```bash
streamlit run ui.py
```
Open `http://localhost:8501` and navigate to **Tab 2: ⚖️ AI Outcome & Risk Intelligence**.

#### 2. FastAPI Microservice
```bash
python lexicourt_api.py
```
Or with uvicorn:
```bash
uvicorn lexicourt_api:app --host 0.0.0.0 --port 8000
```
Interactive API docs will be available at `http://localhost:8000/docs`.

### 📡 API Example Request & Response

#### POST `/predict`
```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{
           "text": "The petitioner filed a writ petition under Article 226 challenging the detention order. The respondent state filed counter affidavit.",
           "apply_leakage_strip": true
         }'
```

#### Response
```json
{
  "predicted_label": "Other",
  "confidence": 0.7839,
  "probabilities": {
    "Accepted": 0.0963,
    "Other": 0.7839,
    "Rejected": 0.1197
  },
  "disclaimer": "AI-assisted estimate based on fine-tuned InLegalBERT (Test Macro F1 ~0.61). This output is a statistical prediction and does NOT constitute a legal guarantee or verdict."
}
```

#### GET `/health`
```bash
curl "http://localhost:8000/health"
```
```json
{
  "status": "healthy",
  "model_dir": "/absolute/path/to/AI-Court/best_model",
  "model_loaded": true
}
```

---

## ⚡ Resource & Deployment Guidelines

> [!IMPORTANT]
> **RAM Requirements**: The ~110M parameter InLegalBERT transformer model requires approximately **1.5 GB to 2.0 GB of RAM** in memory during PyTorch inference. When deploying to container environments (e.g. Render, AWS ECS, HuggingFace Spaces, or Streamlit Cloud), ensure your tier provides at least **2 GB RAM**.

> [!NOTE]
> **Version Control & Model Binary Artifacts**: The `best_model/` weights directory (~438MB safetensors) is excluded in `.gitignore` to prevent committing heavy binaries to git history. When cloning into a fresh environment or CI/CD pipeline, place the `best_model/` folder in the project root or set `LEXICOURT_MODEL_DIR` to point to your storage bucket or model path.

---

## 🧪 Running Automated Tests

Run the unit test suite to verify model loading, input validation, leakage stripping, and response formatting:
```bash
python test_lexicourt_inference.py
```

---

## 📁 Repository Structure

```text
├── ui.py                                                # Main Streamlit application
├── lexicourt_inference.py                               # Standalone InLegalBERT inference module
├── lexicourt_api.py                                     # FastAPI microservice for /predict & /health
├── test_lexicourt_inference.py                         # Automated test suite for outcome prediction
├── best_model/                                          # Fine-tuned InLegalBERT model directory
│   ├── config.json                                      # HF Model configuration & label mapping
│   ├── model.safetensors                                # PyTorch model weights (~438 MB)
│   ├── tokenizer.json & tokenizer_config.json           # Fast Tokenizer files
│   └── label_mapping.json                               # Label index mapping (0: Accepted, 1: Other, 2: Rejected)
├── requirements.txt                                     # Python dependencies
├── Procfile                                             # Web server entrypoint for Render / Railway
├── .gitignore                                           # Git exclusion rules (includes best_model/ & binaries)
└── README.md                                            # Technical documentation
```

---

## 👩‍💻 Author

**Anushka Das**  
Computer Science Undergraduate | Applied ML & NLP Researcher  
GitHub: [@Anushka8178](https://github.com/Anushka8178)
# ⚖️ AI-Court Case Analyzer & Judicial Intelligence Platform

An AI-powered legal analytics web application designed to analyze Indian court case records, predict trial outcomes, assess bail/custody risk, and explore Indian Penal Code (IPC) statutory references.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-F7931E?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)

---

## 🌟 Key Features

- 🔍 **Interactive Legal Search Engine**: Filter judicial records by State Jurisdiction, Police Station, Act Number / IPC Section, and Case CINO ID.
- ⚖️ **AI Outcome & Risk Predictor**: Evaluates case parameters to estimate disposition likelihood (Withdrawal / Compromise vs Full Trial), custody/bail risk levels, and predicted disposal timeframes.
- 📊 **Judicial Data Analytics**: Visualizes historical disposition trends, top registered IPC sections, and state-wise court caseload distributions.
- 📜 **IPC Statutory Reference Dictionary**: Instant access to IPC legal section definitions, statutory offenses, and maximum prescribed sentences.
- ⚡ **Preset Demonstration Shortcuts**: Single-click preset buttons for rapid testing during demos and code reviews.

---

## 🛠️ Technology Stack

- **Frontend / Framework**: Streamlit (with modern glassmorphic CSS styling)
- **Data Engineering**: Pandas, NumPy
- **Machine Learning & NLP**: Scikit-Learn, Joblib
- **Deployment Targets**: Streamlit Community Cloud, Render, HuggingFace Spaces

---

## 🚀 Quick Local Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Anushka8178/AI-Court.git
   cd AI-Court
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the application**:
   ```bash
   streamlit run ui.py
   ```

The application will open automatically in your web browser at `http://localhost:8501`.

---

## 🌐 Deploying to Streamlit Community Cloud (Recommended - Free 1-Click)

1. Push your changes to GitHub (`git push origin main` or `master`).
2. Visit **[share.streamlit.io](https://share.streamlit.io/)** and log in with GitHub.
3. Click **New app** and select:
   - **Repository**: `Anushka8178/AI-Court`
   - **Branch**: `master` (or `main`)
   - **Main file path**: `ui.py`
4. Click **Deploy!** Your app will be live with an SSL HTTPS link in under 2 minutes.

---

## 📁 Repository Structure

```text
├── ui.py                                                # Main Streamlit application
├── requirements.txt                                     # Python dependencies
├── Procfile                                             # Web server entrypoint for Render / Railway
├── .streamlit/
│   └── config.toml                                      # Theme & server configuration
├── final_cases_with_detailed_section_explanations.csv   # Indian judicial dataset
├── model.pkl                                            # ML model artifact
├── preprocessor.pkl                                     # Feature preprocessor
├── label_encoder.pkl                                    # Class encoder
├── .gitignore                                           # Excludes 2.5GB binary files & caches
└── README.md                                            # Documentation
```

---

## 👩‍💻 Author

**Anushka Das**  
Computer Science Undergraduate | Applied ML & NLP Researcher  
GitHub: [@Anushka8178](https://github.com/Anushka8178)
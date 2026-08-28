from contextlib import asynccontextmanager
import os
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, ConfigDict
from lexicourt_inference import load_model, predict_outcome, DEFAULT_MODEL_DIR

class PredictionRequest(BaseModel):
    text: str = Field(..., description="Legal case text or facts to classify", min_length=1)
    apply_leakage_strip: bool = Field(True, description="Whether to strip disposition leakage phrases")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text": "The petitioner filed a petition challenging the detention order under section 3 of the IPC. The High Court analyzed the evidence.",
                "apply_leakage_strip": True
            }
        }
    )

class PredictionResponse(BaseModel):
    predicted_label: str
    confidence: float
    probabilities: Dict[str, float]
    disclaimer: str
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    model_dir: str
    model_loaded: bool

    model_config = ConfigDict(protected_namespaces=())

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load model once into memory
    print("Initializing LexiCourt API service & loading InLegalBERT model...")
    try:
        load_model()
        print("InLegalBERT model pre-loaded successfully for FastAPI service.")
    except Exception as e:
        print(f"Warning: Failed to pre-load InLegalBERT model at startup: {e}")
    yield
    # Shutdown logic if any
    print("Shutting down LexiCourt API service.")

app = FastAPI(
    title="LexiCourt Legal Outcome Prediction API",
    description="FastAPI service serving fine-tuned InLegalBERT legal outcome classifier (Accepted / Other / Rejected)",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health", response_model=HealthResponse)
def health_check():
    target_dir = os.path.abspath(DEFAULT_MODEL_DIR)
    is_loaded = False
    try:
        load_model()
        is_loaded = True
    except Exception:
        is_loaded = False

    return {
        "status": "healthy" if is_loaded else "degraded",
        "model_dir": target_dir,
        "model_loaded": is_loaded
    }

@app.post("/predict", response_model=PredictionResponse)
def predict_endpoint(payload: PredictionRequest):
    if not payload.text or not payload.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Field 'text' cannot be empty or blank."
        )

    result = predict_outcome(payload.text, apply_leakage_strip=payload.apply_leakage_strip)
    
    if "error" in result and result.get("predicted_label") == "Unknown":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"]
        )

    return result

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting LexiCourt FastAPI server on http://0.0.0.0:{port}")
    uvicorn.run("lexicourt_api:app", host="0.0.0.0", port=port, reload=False)

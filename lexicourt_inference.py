import os
import re
import json
import gc
from typing import Dict, Any, Tuple, Optional
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Environment variable for model directory
DEFAULT_MODEL_DIR = os.environ.get("LEXICOURT_MODEL_DIR", os.environ.get("MODEL_DIR", "./best_model"))

# Global singleton storage for cached model and tokenizer
_LOADED_MODEL = None
_LOADED_TOKENIZER = None
_LOADED_LABEL_MAPPING = None
_CURRENT_MODEL_DIR = None

# Procedural decision leakage regex patterns targeting formal disposition clauses.
# Specifically designed NOT to naively strip standalone words like "accepted" or "rejected" when used in factual context.
DECISION_LEAK_PATTERNS = [
    r"(?i)\b(appeal|petition|application|writ|special\s+leave\s+petition|slp)\s+(is|are)\s+(hereby\s+)?(allowed|dismissed|rejected|accepted|disposed\s+of)\b.*",
    r"(?i)\bimpugned\s+(order|judgment|decree)\s+is\s+(hereby\s+)?(set\s+aside|quashed|upheld|confirmed|modified|vacated)\b.*",
    r"(?i)\bjudgment\s+(is|stands)\s+(affirmed|reversed|modified)\b.*",
    r"(?i)\b(allowed|dismissed|rejected|accepted)\s+with\s+no\s+order\s+as\s+to\s+costs\b.*",
    r"(?i)\b(stand[s]?\s+)(dismissed|allowed|rejected|accepted)\b",
]

def strip_leakage(text: str) -> str:
    """
    Removes explicit legal disposition statements from judgment/case text
    using the exact DECISION_LEAK_PATTERNS regex list to prevent target leakage
    without naively stripping occurrences of 'accepted'/'rejected' in factual context.
    """
    if not text:
        return ""
    
    cleaned_text = text
    for pattern in DECISION_LEAK_PATTERNS:
        cleaned_text = re.sub(pattern, " ", cleaned_text)
        
    # Collapse multiple whitespaces
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
    return cleaned_text if cleaned_text else text

def load_model(model_dir: Optional[str] = None) -> Tuple[Any, Any, Dict[int, str]]:
    """
    Loads the HuggingFace tokenizer and InLegalBERT classification model ONCE into memory.
    Subsequent calls return the cached singleton instances. Optimized for memory-constrained environments (<1GB RAM).
    """
    global _LOADED_MODEL, _LOADED_TOKENIZER, _LOADED_LABEL_MAPPING, _CURRENT_MODEL_DIR
    
    target_dir = os.path.abspath(model_dir or DEFAULT_MODEL_DIR)
    
    if _LOADED_MODEL is not None and _LOADED_TOKENIZER is not None and _CURRENT_MODEL_DIR == target_dir:
        return _LOADED_MODEL, _LOADED_TOKENIZER, _LOADED_LABEL_MAPPING

    if not os.path.exists(target_dir):
        raise FileNotFoundError(
            f"Model directory not found at '{target_dir}'. "
            "Please ensure 'best_model' directory exists or set LEXICOURT_MODEL_DIR / MODEL_DIR environment variable."
        )

    config_path = os.path.join(target_dir, "config.json")
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Model configuration file 'config.json' missing in '{target_dir}'.")

    label_mapping_path = os.path.join(target_dir, "label_mapping.json")
    id2label = {0: "Accepted", 1: "Other", 2: "Rejected"}
    
    if os.path.exists(label_mapping_path):
        try:
            with open(label_mapping_path, "r", encoding="utf-8") as f:
                mapping = json.load(f)
                if "id2label" in mapping:
                    id2label = {int(k): str(v) for k, v in mapping["id2label"].items()}
        except Exception as e:
            print(f"Warning: Could not parse label_mapping.json: {e}. Falling back to default id2label.")

    try:
        # Restrict single-thread CPU allocations to reduce RAM overhead in low-memory environments (Streamlit Cloud 1GB limit)
        torch.set_num_threads(1)
        
        tokenizer = AutoTokenizer.from_pretrained(target_dir)
        
        # Try loading with low_cpu_mem_usage if accelerate is installed, fallback cleanly if not
        try:
            model = AutoModelForSequenceClassification.from_pretrained(
                target_dir,
                low_cpu_mem_usage=True
            )
        except Exception:
            model = AutoModelForSequenceClassification.from_pretrained(target_dir)

        model.eval()
        gc.collect()
        
        _LOADED_TOKENIZER = tokenizer
        _LOADED_MODEL = model
        _LOADED_LABEL_MAPPING = id2label
        _CURRENT_MODEL_DIR = target_dir
        
        return _LOADED_MODEL, _LOADED_TOKENIZER, _LOADED_LABEL_MAPPING
    except Exception as e:
        raise RuntimeError(f"Failed to load InLegalBERT model from '{target_dir}': {str(e)}")

def predict_outcome(text: str, apply_leakage_strip: bool = True) -> Dict[str, Any]:
    """
    Predicts legal case outcome (Accepted / Other / Rejected) for input text.
    
    Returns:
        dict: {
            "predicted_label": str,
            "confidence": float (0-1),
            "probabilities": Dict[str, float],
            "disclaimer": str
        }
    """
    if not text or not isinstance(text, str) or not text.strip():
        return {
            "error": "Empty or missing text input. Please provide legal case facts or document text.",
            "predicted_label": "Unknown",
            "confidence": 0.0,
            "probabilities": {"Accepted": 0.0, "Other": 0.0, "Rejected": 0.0}
        }

    try:
        model, tokenizer, id2label = load_model()
    except Exception as e:
        return {
            "error": f"Model loading error: {str(e)}",
            "predicted_label": "Unknown",
            "confidence": 0.0,
            "probabilities": {"Accepted": 0.0, "Other": 0.0, "Rejected": 0.0}
        }

    processed_text = text.strip()
    if apply_leakage_strip:
        processed_text = strip_leakage(processed_text)

    try:
        inputs = tokenizer(
            processed_text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        )

        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probs = F.softmax(logits, dim=-1).squeeze(0).tolist()

        label_names = [id2label.get(i, f"Class_{i}") for i in range(len(probs))]
        probabilities_dict = {
            label: round(float(prob), 4) for label, prob in zip(label_names, probs)
        }

        top_idx = int(torch.argmax(logits, dim=-1).item())
        predicted_label = id2label.get(top_idx, "Unknown")
        confidence = round(float(probs[top_idx]), 4)

        return {
            "predicted_label": predicted_label,
            "confidence": confidence,
            "probabilities": probabilities_dict,
            "disclaimer": (
                "AI-assisted estimate based on fine-tuned InLegalBERT (Test Macro F1 ~0.61). "
                "This output is a statistical prediction and does NOT constitute a legal guarantee or verdict."
            )
        }
    except Exception as e:
        return {
            "error": f"Inference execution error: {str(e)}",
            "predicted_label": "Unknown",
            "confidence": 0.0,
            "probabilities": {"Accepted": 0.0, "Other": 0.0, "Rejected": 0.0}
        }

if __name__ == "__main__":
    print("Pre-loading model...")
    _, _, mapping = load_model()
    print(f"Loaded successfully with label mapping: {mapping}")
    sample_text = "The defendant accepted the contract terms, but the appeal is hereby allowed."
    print("Original text:", sample_text)
    print("Stripped text:", strip_leakage(sample_text))
    res = predict_outcome(sample_text)
    print("Sample prediction result:")
    print(json.dumps(res, indent=2))

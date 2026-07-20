import os
import joblib
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'ml_assets', 'crop_model.pkl')
SCALER_PATH = os.path.join(BASE_DIR, 'ml_assets', 'scaler.pkl')

_model = None
_scaler = None

def get_ml_assets():
    global _model, _scaler
    if _model is None or _scaler is None:
        if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
            _model = joblib.load(MODEL_PATH)
            _scaler = joblib.load(SCALER_PATH)
        else:
            raise FileNotFoundError("ML Model or Scaler file not found. Please train model first.")
    return _model, _scaler

def predict_crop_recommendation(n, p, k, temperature, humidity, ph, rainfall):
    """
    Predicts the primary crop recommendation along with confidence score
    and top alternative crop probabilities.
    """
    model, scaler = get_ml_assets()
    
    # Create DataFrame with matching feature names to avoid sklearn warnings
    feature_names = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    input_df = pd.DataFrame([[n, p, k, temperature, humidity, ph, rainfall]], columns=feature_names)
    
    scaled_input = scaler.transform(input_df)
    
    # Predict probabilities across all classes
    probabilities = model.predict_proba(scaled_input)[0]
    classes = model.classes_
    
    # Sort probabilities descending
    sorted_indices = np.argsort(probabilities)[::-1]
    
    top_class = classes[sorted_indices[0]]
    top_confidence = round(float(probabilities[sorted_indices[0]]) * 100, 2)
    
    alternatives = []
    for idx in sorted_indices[1:4]: # Top 3 runner-ups
        conf = round(float(probabilities[idx]) * 100, 2)
        if conf > 0.01:
            alternatives.append({
                'crop': str(classes[idx]),
                'confidence': conf
            })
            
    return top_class, top_confidence, alternatives

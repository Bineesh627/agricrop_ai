import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Create ml_assets directory if it doesn't exist
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.makedirs(BASE_DIR, exist_ok=True)

# Define crop optimal parameter profiles based on agricultural science standard dataset
# Format: crop: [N_mean, N_std, P_mean, P_std, K_mean, K_std, temp_mean, temp_std, hum_mean, hum_std, ph_mean, ph_std, rain_mean, rain_std]
crop_profiles = {
    'rice':        [90, 10, 42, 5, 43, 5, 23.6, 2.0, 82.2, 4.0, 6.4, 0.4, 236.0, 25.0],
    'maize':       [77, 8, 48, 5, 20, 3, 22.3, 2.0, 65.0, 5.0, 6.2, 0.4, 84.0, 10.0],
    'chickpea':    [40, 5, 68, 6, 80, 5, 18.9, 1.8, 16.8, 2.0, 7.3, 0.3, 80.0, 8.0],
    'kidneybeans': [20, 4, 67, 5, 20, 3, 20.1, 1.5, 21.6, 2.5, 5.7, 0.3, 106.0, 10.0],
    'pigeonpeas':  [20, 4, 67, 5, 20, 3, 27.7, 2.0, 48.1, 5.0, 5.8, 0.4, 149.0, 15.0],
    'mothbeans':   [21, 4, 48, 5, 20, 3, 28.2, 2.0, 53.2, 4.0, 6.8, 0.4, 51.0, 6.0],
    'mungbean':    [20, 4, 48, 5, 20, 3, 28.5, 2.0, 85.5, 3.0, 6.7, 0.3, 48.0, 5.0],
    'blackgram':   [40, 5, 67, 5, 19, 3, 29.9, 2.0, 65.1, 4.0, 7.1, 0.4, 67.0, 7.0],
    'lentil':      [18, 3, 68, 5, 19, 3, 24.5, 1.8, 64.8, 4.0, 6.9, 0.3, 45.0, 5.0],
    'pomegranate': [20, 4, 18, 3, 40, 4, 21.8, 2.0, 90.1, 3.0, 6.4, 0.4, 107.0, 10.0],
    'banana':      [100, 10, 82, 6, 50, 5, 27.3, 2.0, 80.4, 4.0, 6.0, 0.4, 105.0, 10.0],
    'mango':       [20, 4, 27, 4, 30, 4, 31.2, 2.0, 50.2, 4.0, 5.8, 0.3, 95.0, 9.0],
    'grapes':      [23, 4, 134, 8, 200, 10, 23.8, 2.0, 81.9, 3.0, 6.0, 0.3, 70.0, 7.0],
    'watermelon':  [99, 8, 17, 3, 50, 4, 25.5, 1.8, 85.2, 3.0, 6.5, 0.3, 50.0, 5.0],
    'muskmelon':   [100, 8, 17, 3, 50, 4, 28.6, 1.8, 92.3, 2.5, 6.4, 0.3, 24.0, 3.0],
    'apple':       [20, 4, 134, 8, 199, 10, 22.6, 1.8, 92.3, 2.5, 5.9, 0.3, 112.0, 10.0],
    'orange':      [19, 4, 16, 3, 10, 2, 22.8, 1.8, 92.2, 2.5, 7.0, 0.3, 110.0, 10.0],
    'papaya':      [49, 5, 59, 5, 50, 4, 33.7, 2.0, 92.4, 2.5, 6.7, 0.3, 142.0, 12.0],
    'coconut':     [21, 4, 17, 3, 31, 4, 27.4, 1.8, 94.8, 2.0, 5.9, 0.3, 175.0, 15.0],
    'cotton':      [117, 10, 46, 5, 19, 3, 24.0, 2.0, 79.8, 4.0, 6.9, 0.4, 80.0, 8.0],
    'jute':        [78, 8, 46, 5, 40, 4, 24.9, 1.8, 79.6, 4.0, 6.7, 0.3, 174.0, 15.0],
    'coffee':      [101, 9, 28, 4, 30, 4, 25.5, 1.8, 57.7, 4.0, 6.8, 0.3, 158.0, 14.0]
}

def generate_dataset(samples_per_crop=100):
    np.random.seed(42)
    data = []
    
    for crop, prof in crop_profiles.items():
        n = np.clip(np.random.normal(prof[0], prof[1], samples_per_crop), 0, 140)
        p = np.clip(np.random.normal(prof[2], prof[3], samples_per_crop), 5, 145)
        k = np.clip(np.random.normal(prof[4], prof[5], samples_per_crop), 5, 205)
        temp = np.clip(np.random.normal(prof[6], prof[7], samples_per_crop), 8, 45)
        hum = np.clip(np.random.normal(prof[8], prof[9], samples_per_crop), 14, 100)
        ph = np.clip(np.random.normal(prof[10], prof[11], samples_per_crop), 3.5, 10.0)
        rain = np.clip(np.random.normal(prof[12], prof[13], samples_per_crop), 20, 300)
        
        for i in range(samples_per_crop):
            data.append({
                'N': round(float(n[i]), 2),
                'P': round(float(p[i]), 2),
                'K': round(float(k[i]), 2),
                'temperature': round(float(temp[i]), 2),
                'humidity': round(float(hum[i]), 2),
                'ph': round(float(ph[i]), 2),
                'rainfall': round(float(rain[i]), 2),
                'label': crop
            })
            
    df = pd.DataFrame(data)
    csv_path = os.path.join(BASE_DIR, 'crop_recommendation.csv')
    df.to_csv(csv_path, index=False)
    print(f"Dataset generated with {len(df)} samples saved to {csv_path}")
    return df

def train():
    df = generate_dataset(samples_per_crop=100)
    
    X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
    y = df['label']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    y_pred = model.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {acc * 100:.2f}%")
    
    # Save model and scaler
    model_path = os.path.join(BASE_DIR, 'crop_model.pkl')
    scaler_path = os.path.join(BASE_DIR, 'scaler.pkl')
    
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    print(f"Saved model to {model_path} and scaler to {scaler_path}")

if __name__ == '__main__':
    train()

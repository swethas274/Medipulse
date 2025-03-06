import torch
import numpy as np
import joblib
import model_fnn as ml
from model_fnn import AdvancedCortisolPredictor

model = AdvancedCortisolPredictor(input_dim=6) 
model.load_state_dict(torch.load("best_cortisol_model.pth"))
model.eval()

scaler = joblib.load("scaler.pkl")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

def predict_cortisol(new_sample):
    """
    Predict cortisol levels for a new sample.

    Parameters:
    new_sample (list or array): A single new sample with sensor readings.

    Returns:
    float: Predicted cortisol level.
    """
    new_sample = np.array(new_sample).reshape(1, -1)  
    new_sample_scaled = scaler.transform(new_sample)  
    sample_tensor = torch.tensor(new_sample_scaled, dtype=torch.float32).to(device)
    with torch.no_grad():
        prediction = model(sample_tensor).item()
    
    return prediction

def check_cortisol(new_sample):
    cortisol=predict_cortisol(new_sample)
    if (cortisol >= 20):
        return 2
    elif (cortisol >= 15):
        return 1
    return 0

print(check_cortisol([46991.0,41819.0,83.0,308.0,96.0,32.0]))
import joblib
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel

# ------------------ LOAD MODEL ------------------
model = joblib.load("model.pkl")

app = FastAPI()

# ------------------ INPUT SCHEMA ------------------
class WineFeatures(BaseModel):
    fixed_acidity: float
    volatile_acidity: float
    citric_acid: float
    residual_sugar: float
    chlorides: float
    free_sulfur_dioxide: float
    total_sulfur_dioxide: float
    density: float
    pH: float
    sulphates: float
    alcohol: float

# ------------------ PREDICTION ENDPOINT ------------------
@app.post("/predict")
def predict(features: WineFeatures):
    X = np.array([[
        features.fixed_acidity,
        features.volatile_acidity,
        features.citric_acid,
        features.residual_sugar,
        features.chlorides,
        features.free_sulfur_dioxide,
        features.total_sulfur_dioxide,
        features.density,
        features.pH,
        features.sulphates,
        features.alcohol
    ]])

    prediction = model.predict(X)[0]

    wine_quality = int(round(prediction))

    return {
        "name": "Amogh",
        "roll_no": "2022BCS0022",
        "wine_quality": wine_quality
    }

from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
app = FastAPI()

model = joblib.load("model.pkl")
scaler = joblib.load("scaler.pkl")
features = joblib.load("features.pkl")


class HeartInput(BaseModel):
    age: float
    sex: int
    resting_blood_pressure: float
    cholestoral: float
    fasting_blood_sugar: int
    Max_heart_rate: float
    exercise_induced_angina: int
    oldpeak: float

    chest_pain_type_Atypical_angina: int
    chest_pain_type_Non_anginal_pain: int
    chest_pain_type_Typical_angina: int

    rest_ecg_Normal: int
    rest_ecg_ST_T_wave_abnormality: int

    slope_Flat: int
    slope_Upsloping: int

    vessels_colored_by_flourosopy_One: int
    vessels_colored_by_flourosopy_Three: int
    vessels_colored_by_flourosopy_Two: int
    vessels_colored_by_flourosopy_Zero: int

    thalassemia_No: int
    thalassemia_Normal: int
    thalassemia_Reversable_Defect: int


@app.post("/predict")
def predict(data: HeartInput):

    input_data = np.array([[
        data.age,
        data.sex,
        data.resting_blood_pressure,
        data.cholestoral,
        data.fasting_blood_sugar,
        data.Max_heart_rate,
        data.exercise_induced_angina,
        data.oldpeak,

        data.chest_pain_type_Atypical_angina,
        data.chest_pain_type_Non_anginal_pain,
        data.chest_pain_type_Typical_angina,

        data.rest_ecg_Normal,
        data.rest_ecg_ST_T_wave_abnormality,

        data.slope_Flat,
        data.slope_Upsloping,

        data.vessels_colored_by_flourosopy_One,
        data.vessels_colored_by_flourosopy_Three,
        data.vessels_colored_by_flourosopy_Two,
        data.vessels_colored_by_flourosopy_Zero,

        data.thalassemia_No,
        data.thalassemia_Normal,
        data.thalassemia_Reversable_Defect
    ]])

    # scale
    input_scaled = scaler.transform(input_data)

    # predict
    prediction = model.predict(input_scaled)

    return {
        "prediction": int(prediction[0])
    }
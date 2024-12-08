from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ml.utils.prediction import StrokePredictor
from pydantic import BaseModel
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="StrokeGuard API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize predictor
try:
    predictor = StrokePredictor()
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load model: {str(e)}")
    raise

class PredictionInput(BaseModel):
    age: float
    gender: int
    hypertension: int
    heart_disease: int
    ever_married: int
    Residence_type: int
    avg_glucose_level: float
    bmi: float
    work_type_Govt_job: int
    work_type_Never_worked: int
    work_type_Private: int
    work_type_Self_employed: int  # Perbaiki nama field ini
    work_type_children: int
    smoking_status_Unknown: int
    smoking_status_formerly_smoked: int
    smoking_status_never_smoked: int
    smoking_status_smokes: int

    class Config:
        # Izinkan konversi dari snake_case ke camelCase
        allow_population_by_field_name = True

@app.get("/")
def read_root():
    return {"message": "Welcome to StrokeGuard API", "status": "healthy"}

@app.post("/predict")
async def predict(data: PredictionInput):
    try:
        logger.info("Received prediction request")
        input_data = data.dict()
        result = predictor.make_prediction(input_data)
        logger.info("Prediction completed successfully")
        return result
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
import os
import sys

# Import dengan absolute path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ml.utils.preprocessing import prepare_input_data, validate_input

class StrokePredictor:
    def __init__(self):
        self.model = None
        self.metadata = None
        self.expected_columns = None
        self.optimal_threshold = None
        self._load_model()

    def _load_model(self):
        """Load model dan metadata"""
        try:
            # Mendapatkan path absolut ke root project
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent

            # Define paths
            model_path = project_root / "ml" / "models" / "optimized_stroke_model.joblib"
            metadata_path = project_root / "ml" / "models" / "model_metadata.joblib"
            data_path = project_root / "ml" / "data" / "processed" / "stroke_data_final.csv"

            print(f"Loading model from: {model_path}")
            print(f"Loading metadata from: {metadata_path}")
            print(f"Loading data from: {data_path}")

            # Verifikasi file exists
            if not model_path.exists():
                raise FileNotFoundError(f"Model file not found at: {model_path}")
            if not metadata_path.exists():
                raise FileNotFoundError(f"Metadata file not found at: {metadata_path}")
            if not data_path.exists():
                raise FileNotFoundError(f"Data file not found at: {data_path}")

            # Load files
            self.model = joblib.load(str(model_path))
            self.metadata = joblib.load(str(metadata_path))
            original_data = pd.read_csv(str(data_path))
            
            # Set variables
            self.expected_columns = original_data.drop('stroke', axis=1).columns.tolist()
            self.optimal_threshold = self.metadata['optimized_performance']['optimal_threshold']

            print("Model and data loaded successfully")

        except Exception as e:
            raise Exception(f"Error loading model and data: {str(e)}")

    def make_prediction(self, data_dict):
        """
        Melakukan prediksi stroke
        
        Parameters:
        data_dict (dict): Dictionary berisi data input user
        
        Returns:
        dict: Hasil prediksi dengan probability dan risk factors
        """
        try:
            # Validasi input
            is_valid, error_message = validate_input(data_dict)
            if not is_valid:
                raise ValueError(error_message)

            # Prepare input data
            df = prepare_input_data(data_dict, self.expected_columns)
            
            # Prediksi
            probability = self.model.predict_proba(df)[0, 1]
            prediction = 1 if probability >= self.optimal_threshold else 0
            
            # Hitung risk factors
            risk_factors = []
            if int(data_dict['hypertension']) == 1:
                risk_factors.append("Hypertension")
            if int(data_dict['heart_disease']) == 1:
                risk_factors.append("Heart Disease")
            if float(data_dict['bmi']) >= 25:
                risk_factors.append("High BMI")
            if float(data_dict['avg_glucose_level']) >= 200:
                risk_factors.append("High Glucose Level")
            if float(data_dict['age']) >= 65:
                risk_factors.append("Advanced Age")
            
            # Determine confidence level
            confidence_margin = abs(probability - 0.5)
            if confidence_margin > 0.3:
                confidence = "High"
            elif confidence_margin > 0.15:
                confidence = "Medium"
            else:
                confidence = "Low"

            return {
                "prediction": prediction,
                "probability": float(probability),
                "risk_factors": risk_factors,
                "confidence": confidence,
                "threshold": self.optimal_threshold
            }

        except Exception as e:
            raise Exception(f"Error during prediction: {str(e)}")

# Test code
if __name__ == "__main__":
    try:
        predictor = StrokePredictor()
        print("Predictor initialized successfully")
        
        # Test prediction with sample data
        sample_data = {
            'age': 50,
            'gender': 1,
            'hypertension': 0,
            'heart_disease': 0,
            'ever_married': 1,
            'Residence_type': 1,
            'avg_glucose_level': 100,
            'bmi': 25,
            'work_type_Govt_job': 0,
            'work_type_Never_worked': 0,
            'work_type_Private': 1,
            'work_type_Self-employed': 0,
            'work_type_children': 0,
            'smoking_status_Unknown': 0,
            'smoking_status_formerly smoked': 0,
            'smoking_status_never smoked': 1,
            'smoking_status_smokes': 0
        }
        
        result = predictor.make_prediction(sample_data)
        print("\nPrediction Result:")
        print(f"Prediction: {'High Risk' if result['prediction'] == 1 else 'Low Risk'}")
        print(f"Probability: {result['probability']:.2%}")
        print(f"Confidence: {result['confidence']}")
        print("Risk Factors:", result['risk_factors'])
        
    except Exception as e:
        print(f"Error: {str(e)}")
import pandas as pd
import numpy as np

def create_features(data_dict):
    """
    Membuat fitur tambahan dari input data
    
    Parameters:
    data_dict (dict): Dictionary berisi data input user
    
    Returns:
    dict: Dictionary dengan fitur tambahan
    """
    # Konversi ke float untuk perhitungan
    numeric_features = ['age', 'bmi', 'avg_glucose_level', 'hypertension', 'heart_disease']
    for key in numeric_features:
        data_dict[key] = float(data_dict[key])
    
    # Buat fitur interaksi
    data_dict['age_health_interaction'] = data_dict['age'] * (
        data_dict['hypertension'] + data_dict['heart_disease']
    )
    data_dict['bmi_glucose_risk'] = data_dict['bmi'] * data_dict['avg_glucose_level']
    
    # Hitung risk factors
    high_bmi = 1 if data_dict['bmi'] >= 25 else 0
    high_glucose = 1 if data_dict['avg_glucose_level'] >= 200 else 0
    data_dict['risk_factors'] = (
        data_dict['hypertension'] + 
        data_dict['heart_disease'] + 
        high_bmi + 
        high_glucose
    )
    
    data_dict['age_lifestyle_risk'] = data_dict['age'] * data_dict['risk_factors']
    
    return data_dict

def prepare_input_data(data_dict, expected_columns):
    """
    Menyiapkan data input sesuai format yang diharapkan model
    
    Parameters:
    data_dict (dict): Dictionary berisi data input user
    expected_columns (list): List kolom yang diharapkan oleh model
    
    Returns:
    pd.DataFrame: DataFrame yang siap untuk prediksi
    """
    # Buat fitur tambahan
    data_dict = create_features(data_dict)
    
    # Buat DataFrame
    df = pd.DataFrame([data_dict])
    
    # Pastikan semua kolom yang diharapkan ada
    for col in expected_columns:
        if col not in df.columns:
            df[col] = 0
    
    # Urutkan kolom sesuai dengan urutan training
    df = df[expected_columns]
    
    return df

def validate_input(data_dict):
    """
    Memvalidasi input dari user
    
    Parameters:
    data_dict (dict): Dictionary berisi data input user
    
    Returns:
    tuple: (is_valid, error_message)
    """
    try:
        # Validasi age
        if not 0 <= float(data_dict['age']) <= 120:
            return False, "Age must be between 0 and 120"
        
        # Validasi BMI
        if not 10 <= float(data_dict['bmi']) <= 60:
            return False, "BMI must be between 10 and 60"
        
        # Validasi glucose level
        if not 0 <= float(data_dict['avg_glucose_level']) <= 500:
            return False, "Glucose level must be between 0 and 500"
        
        return True, ""
        
    except ValueError:
        return False, "Invalid numeric values provided"
    except KeyError as e:
        return False, f"Missing required field: {str(e)}"
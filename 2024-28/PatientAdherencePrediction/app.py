import streamlit as st
import pandas as pd
import joblib
import numpy as np
model = joblib.load("best_model.pkl")

st.title("💊 Patient Medication Adherence Prediction App")
st.write("This app predicts whether a patient will adhere to their medication regimen based on given details.")

col1, col2 = st.columns(2)

with col1:
    age = st.slider("Age", 18, 90, 45)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    med_type = st.selectbox("Medication Type", ["TypeA", "TypeB", "TypeC"])
    dosage = st.number_input("Dosage (mg)", 0, 500, 150)
    prev_adherence = st.selectbox("Previous Adherence", ["No", "Yes"])
    education = st.selectbox("Education Level", ["High School", "Graduate", "Postgraduate"])

with col2:
    income = st.number_input("Income", 100000, 1500000, 500000)
    social_support = st.selectbox("Social Support", ["Low", "Medium", "High"])
    condition_severity = st.selectbox("Condition Severity", ["Mild", "Moderate", "Severe"])
    comorbidities = st.slider("Comorbidities Count", 0, 10, 2)
    healthcare_access = st.selectbox("Healthcare Access", ["Poor", "Average", "Good"])
    mental_health = st.selectbox("Mental Health", ["Poor", "Moderate", "Good"])
    insurance = st.selectbox("Insurance Coverage", ["No", "Yes"])

# Encode categorical variables (if preprocessing not in model)
input_data = {
    'Age': age,
    'Gender': gender,
    'Medication_Type': med_type,
    'Dosage_mg': dosage,
    'Previous_Adherence': 1 if prev_adherence == "Yes" else 0,
    'Education_Level': education,
    'Income': income,
    'Social_Support_Level': social_support,
    'Condition_Severity': condition_severity,
    'Comorbidities_Count': comorbidities,
    'Healthcare_Access': healthcare_access,
    'Mental_Health_Status': mental_health,
    'Insurance_Coverage': 1 if insurance == "Yes" else 0
}

input_df = pd.DataFrame([input_data])

if st.button("Predict"):
    try:
        with st.spinner("Predicting..."):
            y_pred = model.predict(input_df)[0]
            proba_fn = getattr(model, "predict_proba", None)
            if callable(proba_fn):
                _probs = proba_fn(input_df)
                probs = np.asarray(_probs)[0]
            else:
                probs = None

        adhered = (y_pred == 1)
        if adhered:
            conf = f" ({probs[1]*100:.1f}% confidence)" if probs is not None else ""
            st.success(f"Patient is likely to ADHERE{conf}")
        else:
            conf = f" ({probs[0]*100:.1f}% confidence)" if probs is not None else ""
            st.error(f"Patient is likely to NOT ADHERE{conf}")

        if probs is not None:
            st.write("### Confidence")
            c1, c2 = st.columns(2)
            c1.metric("Adherence", f"{probs[1]*100:.1f}%")
            c2.metric("Non-adherence", f"{probs[0]*100:.1f}%")

    except Exception as e:
        st.error(f"Prediction failed: {e}")

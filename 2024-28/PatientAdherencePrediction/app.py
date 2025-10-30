import streamlit as st
import pandas as pd
import joblib

# Load model (ensure preprocessing is included inside the model pipeline)
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
        prediction = model.predict(input_df)[0]
        probability = model.predict_proba(input_df)[0]

        if prediction == 1:
            st.success(f"✅ Patient is likely to ADHERE ({probability[1]*100:.1f}% probability)")
        else:
            st.error(f"❌ Patient is likely to NOT ADHERE ({probability[0]*100:.1f}% probability)")

        st.write("### Confidence Scores")
        st.write(f"- Adherence: {probability[1]*100:.1f}%")
        st.write(f"- Non-Adherence: {probability[0]*100:.1f}%")

    except Exception as e:
        st.error(f"Prediction failed: {e}")

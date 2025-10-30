import streamlit as st
import pandas as pd
import joblib
import numpy as np
import pandas as _pd
import pandas as _pd
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
if hasattr(model, "feature_names_in_"):
    input_df = input_df.reindex(columns=model.feature_names_in_, fill_value=0)

if st.button("Predict"):
    try:
        with st.spinner("Running prediction..."):
            # Make prediction
            prediction = model.predict(input_df)[0]

            # Get probability scores (with sensible fallbacks)
            probability = None
            if hasattr(model, "predict_proba"):
                probability = model.predict_proba(input_df)[0]
            elif hasattr(model, "decision_function"):
                scores = model.decision_function(input_df)
                # helper transforms #type: ignore
                def _sigmoid(x):
                    return 1.0 / (1.0 + np.exp(-x)) #type: ignore
                def _softmax(x):
                    e = np.exp(x - np.max(x))
                    return e / e.sum() #type: ignore
                if np.ndim(scores) == 1: #type: ignore 
                    p_pos = float(_sigmoid(scores[0]))
                    probability = [1.0 - p_pos, p_pos]
                else:
                    probability = _softmax(scores[0])
            else:
                # no probability info available
                probability = [None, None]

        # small formatting helper
        def _fmt(p):
            return f"{p * 100:.1f}%" if p is not None else "N/A"

        # Display main result
        if prediction == 1:
            st.success(f" Patient is likely to ADHERE ({_fmt(probability[1])} confidence)")
        else:
            st.error(f" Patient is likely to NOT ADHERE ({_fmt(probability[0])} confidence)")

        # Confidence breakdown
        st.write("### Confidence Scores")
        st.write(f"- Adherence: {_fmt(probability[1])}")
        st.write(f"- Non-adherence: {_fmt(probability[0])}")

        # Visual progress bars (if probabilities available)
        if probability[0] is not None and probability[1] is not None:
            cols = st.columns(2)
            cols[0].write("Non-adherence")
            cols[0].progress(min(max(int(probability[0] * 100), 0), 100)) #type: ignore
            cols[1].write("Adherence")
            cols[1].progress(min(max(int(probability[1] * 100), 0), 100)) #type: ignore

        # Show input summary for transparency
        st.write("### Input Summary")
        st.table(input_df.T.rename(columns={0: "Value"}))

        # Try to show feature importances / coefficients if available
        try:
            if hasattr(model, "feature_importances_"):
                imp = _pd.Series(model.feature_importances_, index=input_df.columns)
                imp = imp.sort_values(ascending=False).head(10)
                st.write("### Top features (feature_importances_)")
                st.bar_chart(imp)
            elif hasattr(model, "coef_"):
                coef = model.coef_
                if np.ndim(coef) > 1:
                    coef_vals = np.abs(coef[0])
                else:
                    coef_vals = np.abs(coef)
                imp = _pd.Series(coef_vals, index=input_df.columns).sort_values(ascending=False).head(10)
                st.write("### Top features (absolute coefficients)")
                st.bar_chart(imp)
        except Exception:
            # non-fatal if feature importance cannot be displayed
            pass

        # Prepare downloadable result
        result = input_df.copy()
        result["prediction"] = int(prediction)
        result["prob_non_adherence"] = float(probability[0]) if probability[0] is not None else None #type: ignore
        result["prob_adherence"] = float(probability[1]) if probability[1] is not None else None #type: ignore
        csv = result.to_csv(index=False).encode("utf-8")
        st.download_button("Download prediction (CSV)", csv, file_name="prediction_result.csv", mime="text/csv")

    except Exception as e:
        st.error(" Prediction failed")
        st.exception(e)

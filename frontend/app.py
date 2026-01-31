import streamlit as st
import requests

st.title("CVMatch")

cv_text = st.text_area("Paste CV text here")
job_text = st.text_area("Paste Job Description here")

if st.button("Match"):
    response = requests.post(
        "http://localhost:8000/match",
        json={
            "cv_text": cv_text,
            "job_text": job_text
        }
    )
    result = response.json()
    st.success(f"Match Score: {result['match_percentage']}%")

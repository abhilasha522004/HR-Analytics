# Integrated HR Tool with ATS and Course Recommendation
# This is a merged and cleaned version of both projects
# It includes: Login, Turnover Prediction, Clustering, Sentiment Analysis, ATS Resume Matcher, and Course Recommendation

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import pickle
import re
from io import StringIO
import PyPDF2
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob
from wordcloud import WordCloud
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

# Import custom ML classes
from custom_ml_classes import DynamicOutlierHandler, SentimentAnalyzer, TextCleaner

# -------------------------------
# Load Models and Data
# -------------------------------
hr_model = joblib.load("hr_model.pkl")
sentiment_model = joblib.load("sentiment_model.pkl")

@st.cache_resource
def load_course_data():
    df = pd.read_csv("cleaned_courses.csv")
    with open("course_pipeline.pkl", "rb") as f:
        pipeline = pickle.load(f)
    return df, pipeline

course_df, course_pipeline = load_course_data()

# -------------------------------
# Utility Functions
# -------------------------------
def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    return "".join(page.extract_text() for page in pdf_reader.pages)

def calculate_ats_score(resume_text, job_desc):
    resume_words = set(re.findall(r'\w+', resume_text.lower()))
    job_words = set(re.findall(r'\w+', job_desc.lower()))
    if not job_words: return 0
    matched_words = resume_words & job_words
    return round(len(matched_words) / len(job_words) * 100, 2)

def recommend_courses(query, top_n=10, difficulty=None, min_rating=0.0):
    cleaned_query = course_pipeline.named_steps["cleaner"].transform(pd.Series(query))
    query_vector = course_pipeline.named_steps["tfidf"].transform(cleaned_query)

    course_texts = course_pipeline.named_steps["cleaner"].transform(course_df["course_title"])
    course_vectors = course_pipeline.named_steps["tfidf"].transform(course_texts)

    sim_scores = cosine_similarity(query_vector, course_vectors).flatten()
    course_df["similarity"] = sim_scores
    filtered_df = course_df.copy()

    if difficulty != "All":
        filtered_df = filtered_df[filtered_df["course_difficulty"] == difficulty]

    filtered_df = filtered_df[filtered_df["course_rating"] >= min_rating]
    return filtered_df.sort_values(by="similarity", ascending=False).head(top_n)

# -------------------------------
# Login
# -------------------------------
users = {
    "employee": {"username": "employee", "password": "employee123"},
    "hr": {"username": "hr", "password": "hr123"},
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None

def login(username, password, role):
    if username == users[role]["username"] and password == users[role]["password"]:
        st.session_state.logged_in = True
        st.session_state.user_role = role
        return True
    return False

def logout():
    st.session_state.logged_in = False
    st.session_state.user_role = None

# -------------------------------
# App UI
# -------------------------------
if not st.session_state.logged_in:
    st.title("Login")
    role = st.radio("Select Role", options=["Employee", "HR"])
    username = st.text_input(f"{role} Username")
    password = st.text_input(f"{role} Password", type="password")

    if st.button(f"Login as {role}"):
        if login(username, password, role.lower()):
            st.success(f"Welcome, {role}!")
        else:
            st.error("Invalid credentials.")
else:
    st.sidebar.title(f"Logged in as: {st.session_state.user_role.title()}")
    st.sidebar.button("Logout", on_click=logout)

    uploaded_file = st.file_uploader("Upload Employee Data (CSV)", type=["csv"])
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        st.write(data.head())

        st.sidebar.title("Options")
        selected_option = st.sidebar.radio("Choose a feature:", (
            "Predict Turnover Probability", "Clustering", "Sentiment Analysis", "Course Recommendation", "ATS Resume Matcher"
        ))

        if selected_option == "Predict Turnover Probability":
            if st.button("Predict"):
                predictions = hr_model.predict(data)
                data['Turnover_Probability'] = predictions
                st.write(data)

        elif selected_option == "Clustering":
            features = st.sidebar.multiselect("Select Features", options=data.columns)
            if features:
                preprocessor = ColumnTransformer([
                    ('num', StandardScaler(), data[features].select_dtypes(include=[np.number]).columns.tolist()),
                    ('cat', OneHotEncoder(handle_unknown='ignore'), data[features].select_dtypes(include=[object]).columns.tolist())
                ])
                scaled_data = preprocessor.fit_transform(data[features])
                k = st.sidebar.slider("Number of Clusters", 2, 10, 3)
                kmeans = KMeans(n_clusters=k, random_state=42).fit(scaled_data)
                data['Cluster'] = kmeans.labels_
                st.write(data['Cluster'].value_counts())

        elif selected_option == "Sentiment Analysis":
            if 'ExitStatement' in data.columns:
                sentiments = SentimentAnalyzer().transform(data)
                st.write(sentiments[['ExitStatement', 'Polarity', 'Subjectivity']])

        elif selected_option == "Course Recommendation":
            query = st.text_input("Enter skills or interests")
            diff = st.selectbox("Difficulty", ["All", "Beginner", "Intermediate", "Advanced"])
            rating = st.slider("Min Rating", 0.0, 5.0, 3.5)
            if st.button("Recommend"):
                recs = recommend_courses(query, difficulty=diff, min_rating=rating)
                st.write(recs)

        elif selected_option == "ATS Resume Matcher":
            resume_file = st.file_uploader("Upload Resume", type=["pdf", "txt"])
            job_desc = st.text_area("Job Description")
            if resume_file and job_desc:
                if resume_file.name.endswith(".pdf"):
                    resume_text = extract_text_from_pdf(resume_file)
                else:
                    resume_text = StringIO(resume_file.getvalue().decode("utf-8")).read()
                score = calculate_ats_score(resume_text, job_desc)
                st.metric("ATS Score", f"{score}%")
                st.progress(int(score))

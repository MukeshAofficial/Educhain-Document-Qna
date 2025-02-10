import streamlit as st
from educhain import Educhain, LLMConfig
from educhain.engines import qna_engine
from langchain_google_genai import ChatGoogleGenerativeAI
import os

# Set page configuration at the very top of the script
st.set_page_config(page_title="Educhain Document Q&A", page_icon="📄", layout="wide")

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Google API Key", type="password")
    model_options = {
        "gemini-2.0-flash": "gemini-2.0-flash",
        "gemini-2.0-flash-lite-preview-02-05": "gemini-2.0-flash-lite-preview-02-05",
        "gemini-2.0-pro-exp-02-05": "gemini-2.0-pro-exp-02-05",
    }
    model_name = st.selectbox("Select Model", options=list(model_options.keys()), format_func=lambda x: model_options[x])

    st.markdown("**Powered by** [Educhain](https://github.com/satvik314/educhain)")
    st.write("❤️ Built by [Build Fast with AI](https://buildfastwithai.com/genai-course)")

# --- Initialize Educhain with Gemini Model ---
@st.cache_resource
def initialize_educhain(api_key, model_name):
    if not api_key:
        return None  # Return None if API key is missing

    gemini_model = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key
    )
    llm_config = LLMConfig(custom_model=gemini_model)
    return Educhain(llm_config)


# --- Utility Function to Display Questions ---
def display_questions(questions):
    if questions and hasattr(questions, "questions"):
        for i, question in enumerate(questions.questions):
            st.subheader(f"Question {i + 1}:")
            if hasattr(question, 'options'):
                st.write(f"**Question:** {question.question}")
                st.write("Options:")
                for j, option in enumerate(question.options):
                    st.write(f"   {chr(65 + j)}. {option}")
                if hasattr(question, 'answer'):
                    st.write(f"**Correct Answer:** {question.answer}")
                if hasattr(question, 'explanation') and question.explanation:
                    st.write(f"**Explanation:** {question.explanation}")
            elif hasattr(question, 'keywords'):
                st.write(f"**Question:** {question.question}")
                st.write(f"**Answer:** {question.answer}")
                if question.keywords:
                    st.write(f"**Keywords:** {', '.join(question.keywords)}")
            elif hasattr(question,'answer'):
                st.write(f"**Question:** {question.question}")
                st.write(f"**Answer:** {question.answer}")
                if hasattr(question, 'explanation') and question.explanation:
                    st.write(f"**Explanation:** {question.explanation}")
            else:
                st.write(f"**Question:** {question.question}")
                if hasattr(question, 'explanation') and question.explanation:
                    st.write(f"**Explanation:** {question.explanation}")
            st.markdown("---")

# --- Streamlit App Layout ---
st.title("📄 Educhain Document Q&A")

# --- Main Content: Document Q&A ---
if not api_key:
    st.warning("Please enter your Google API Key in the sidebar to continue.")
else:
    # Initialize Educhain client with Gemini model
    educhain_client = initialize_educhain(api_key, model_name)
    if educhain_client:
        qna_engine = educhain_client.qna_engine
        st.header("Generate Questions from Document")
        source_type = st.selectbox("Select Source Type", ["pdf", "url", "text"])
        if source_type == "pdf":
            uploaded_doc = st.file_uploader("Upload your PDF file", type="pdf")
            source = None
            if uploaded_doc:
                source = uploaded_doc
        elif source_type == "url":
            source = st.text_input("Enter URL:")
        elif source_type == "text":
            source = st.text_area("Enter Text Content:")

        num_questions_doc = st.slider("Number of Questions", 1, 5, 3, key="doc_q")
        learning_objective = st.text_input("Learning Objective (optional):", placeholder="e.g. 'Key events'")
        difficulty_level = st.selectbox("Select Difficulty Level (optional)", ["", "Easy", "Intermediate", "Hard"])

        if source and st.button("Generate Questions from Document", key='doc_button'):
            with st.spinner("Generating..."):
                if source_type == 'pdf' and uploaded_doc:
                    with open("temp_doc.pdf", "wb") as f:
                        f.write(uploaded_doc.read())
                    source = "temp_doc.pdf"

                questions = qna_engine.generate_questions_from_data(
                    source=source,
                    source_type=source_type,
                    num=num_questions_doc,
                    learning_objective=learning_objective,
                    difficulty_level=difficulty_level
                )

                if source_type == 'pdf':
                    os.remove("temp_doc.pdf")  # Clean up pdf file
                display_questions(questions)
    else:
        st.error("Failed to initialize Educhain. Please check your API key and model selection.")

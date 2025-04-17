import streamlit as st
from groq import Groq
import json
import re

# Initialize the Groq client with your API key
client = Groq(api_key="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")

# Function to extract the JSON-like content from the API response
def extract_json_from_response(response_text):
    # Regular expression to find JSON-like content in the response
    json_match = re.search(r'(\[.*\])', response_text, re.DOTALL)
    
    if json_match:
        return json_match.group(1)
    else:
        return None

# Function to generate quiz questions using Groq's llama model
def generate_quiz(content):
    system_prompt = """You are given a Python programming topic. Your task is to generate a set of five coding quiz questions related to the topic.
    Each question should include a Python code segment that the user needs to debug or analyze. Provide four multiple-choice options for users to identify the correct answer or bug in the code.
    Return the response in JSON format without any extra information."""
    
    format_spec = json.dumps([
        {
            'question': 'Question text',
            'code_segment': 'Python code block here',
            'type': 'multiple_choice',
            'options': ['Option A', 'Option B', 'Option C', 'Option D'],
            'correct_answer': 'Option A'
        }
    ])

    user_prompt = f"This is Topic: {content}. Return the response in JSON format like this: {format_spec}, with code segments and multiple-choice options only, no unnecessary information."

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
        )
        response_content = completion.choices[0].message.content
        
        json_data = extract_json_from_response(response_content)
        
        if json_data:
            try:
                return json.loads(json_data)
            except json.JSONDecodeError as e:
                st.error(f"Error parsing the quiz response: {e}")
                st.write("Response received from the API:", response_content)
                return []
        else:
            st.error("Failed to extract JSON from the quiz response.")
            st.write("Response received from the API:", response_content)
            return []
    except Exception as e:
        st.error(f"Error generating quiz: {e}")
        return []

# Main app function
def app():
    # Initialize session state variables if they don't exist
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0
    if 'correct_answers' not in st.session_state:
        st.session_state.correct_answers = 0
    if 'quiz_completed' not in st.session_state:
        st.session_state.quiz_completed = False
    if 'selected_option' not in st.session_state:
        st.session_state.selected_option = None
    if 'answered' not in st.session_state:
        st.session_state.answered = False

    st.sidebar.header("Content Input")
    content = st.sidebar.text_area("Paste the content to generate the quiz", "")
    
    if st.sidebar.button("Generate Quiz"):
        if content:
            # Generate quiz questions and reset session state
            st.session_state.questions = generate_quiz(content)
            st.session_state.current_question_index = 0
            st.session_state.correct_answers = 0
            st.session_state.quiz_completed = False
            st.session_state.answered = False
            st.session_state.selected_option = None

    if st.session_state.questions and not st.session_state.quiz_completed:
        current_question = st.session_state.questions[st.session_state.current_question_index]
        
        # Display current question
        st.write(f"**Question {st.session_state.current_question_index + 1}:** {current_question['question']}")
        
        # Display the code segment
        st.code(current_question['code_segment'], language='python')
        
        # Display options as radio buttons
        selected_option = st.radio("Options", current_question['options'], key=f"q{st.session_state.current_question_index}")
        
        if st.button("Submit"):
            if selected_option:
                # Check if the selected answer is correct
                correct_option = current_question['correct_answer']
                if selected_option == correct_option:
                    st.write("Correct!")
                    st.session_state.correct_answers += 1
                else:
                    st.write(f"Wrong! The correct answer is: {correct_option}")
                # Mark this question as answered
                st.session_state.answered = True
        
        if st.session_state.answered:
            if st.button("Next"):
                # Move to the next question
                if st.session_state.current_question_index < len(st.session_state.questions) - 1:
                    st.session_state.current_question_index += 1
                    st.session_state.answered = False  # Reset for next question
                else:
                    st.session_state.quiz_completed = True

    if st.session_state.quiz_completed:
        st.write(f"Quiz completed! You got {st.session_state.correct_answers} out of {len(st.session_state.questions)} correct.")

if __name__ == "__main__":
    app()

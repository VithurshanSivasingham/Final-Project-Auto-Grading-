import streamlit as st
from Statistics.Statistics import *
from Grammar.grammar2 import *
from Spellings.Spellings import *
from Coherence.Coherence import *
import os

# Function to authenticate user
def authenticate(username, password, user_database):
    # Check if the username exists in the user database and if the password matches
    return username in user_database and user_database[username] == password

# Function to register new user
def register(username, password, user_database):
    # Add the new user to the user database
    user_database[username] = password
    st.sidebar.success("Registration successful. Please log in.")

# Function to log out
def logout():
    st.session_state.logged_in = False
    st.sidebar.success("Logged out successfully.")

# Function to get logical sentences
def get_logical_sentences(essay):
    sentences = [sent.text for sent in nlp(essay).sents]
    logical_sentences = []

    for sentence in sentences:
        if has_logical_connectors(sentence):
            logic_consistency_score = 1  # You can modify this based on your needs
            logical_sentences.append({'sentence': sentence, 'score': logic_consistency_score})

    return logical_sentences

def main():
    st.title('Auto grading system')

    # Check if 'user_database' and 'logged_in' exist in the session state
    if 'user_database' not in st.session_state:
        st.session_state.user_database = {"admin": "admin123"}
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # Sidebar for login, registration, and logout
    if not st.session_state.logged_in:
        action = st.sidebar.radio("Action", ["Login", "Register"])
        if action == "Login":
            login()
        elif action == "Register":
            register_user()
    else:
        file_upload()
        st.sidebar.button("Logout", on_click=logout)

def login():
    # Login section
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if authenticate(username, password, st.session_state.user_database):
            st.session_state.logged_in = True
            st.sidebar.success("Logged in as {}".format(username))
            file_upload()  # Display file upload section after login
        else:
            st.sidebar.error("Invalid credentials")

def register_user():
    # Registration section
    new_username = st.text_input("Enter a new username")
    new_password = st.text_input("Enter a new password", type="password")
    if st.button("Register"):
        if new_username and new_password:
            register(new_username, new_password, st.session_state.user_database)
        else:
            st.warning("Please enter a username and password.")

def file_upload():
    # File upload section
    uploaded_file = st.file_uploader("Upload your essay", type=["txt"])
    if uploaded_file is not None:
        essay = uploaded_file.read().decode('utf-8')

        # Perform grading
        wordCount = getWordCount(essay)
        sentCount = getSentenceCount(essay)
        paraCount = getParaCount(essay)
        avgSentLen = getAvgSentenceLength(essay)
        stdDevSentLen = getStdDevSentenceLength(essay)
        numMisspelt, misspeltWordSug = spellCheck(essay)
        grammarCumScore, grammarSentScore = getGrammarScore(essay)
        coherenceScore = check_coherence(essay)
        
        # Calculate individual scores (scaled to 100)
        spelling_score = min(((wordCount - numMisspelt) / wordCount) * 100, 100) * 0.3  # Scaled to 30
        grammar_score = min(grammarCumScore * 100, 100) * 0.5  # Scaled to 50
        coherence_score = min(coherenceScore * 100, 100) * 0.2  # Scaled to 20

        # Calculate overall score out of 100
        overall_score = min(spelling_score + grammar_score + coherence_score, 100)

        # Get logical sentences
        logical_sentences = get_logical_sentences(essay)

        # Display results
        st.write("Overall Score: ", f"{overall_score:.2f}/100")
        st.write("Word Count: ", wordCount)
        st.write("Sentence Count: ", sentCount)
        st.write("Paragraph Count: ", paraCount)
        st.write("Average Sentence Length: ", avgSentLen)
        st.write("Standard Deviation from the Average Sentence Length: ", stdDevSentLen)
        st.write("Number of Misspelt Words: ", numMisspelt)

        # Display logical sentences
        st.subheader("Logical Sentences:")
        for logical_sentence in logical_sentences:
            st.write(logical_sentence['sentence'], " - Score:", logical_sentence['score'])

if __name__ == '__main__':
    main()

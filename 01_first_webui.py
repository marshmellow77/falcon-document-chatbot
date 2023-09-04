import streamlit as st

# Setting the title of the app
st.title("Hello Streamlit App")

# Creating a text input box
text_input = st.text_input("Please enter your name:")

# Creating a submit button
if st.button("Submit"):
    # Display the hello message
    st.write(f"Hello {text_input}!")


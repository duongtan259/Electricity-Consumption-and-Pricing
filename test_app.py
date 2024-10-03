import streamlit as st
from datetime import datetime

# Function to validate and parse the date input
def validate_date(date_input):
    try:
        # Try to convert the input string to a date object
        parsed_date = datetime.strptime(date_input, "%Y-%m-%d").date()
        return parsed_date, None
    except ValueError:
        # Return None and an error message if the input is invalid
        return None, "Invalid date format. Please use YYYY-MM-DD."

# Create two text inputs for user to type the start and end date
start_date_input = st.text_input("Enter Start Date (YYYY-MM-DD):", "")
end_date_input = st.text_input("Enter End Date (YYYY-MM-DD):", "")

# Initialize session state for dates
if 'start_date' not in st.session_state:
    st.session_state.start_date = None
if 'end_date' not in st.session_state:
    st.session_state.end_date = None

# Validate and store the start date
start_date, start_error = validate_date(start_date_input)
if start_date:
    st.session_state.start_date = start_date

# Validate and store the end date
end_date, end_error = validate_date(end_date_input)
if end_date:
    st.session_state.end_date = end_date

# Display the validated dates or errors
if st.session_state.start_date and st.session_state.end_date:
    st.write(f"Validated Start Date: {st.session_state.start_date}")
    st.write(f"Validated End Date: {st.session_state.end_date}")
    
    # Check if start date is before end date
    if st.session_state.start_date <= st.session_state.end_date:
        st.success("Start date is before or the same as end date.")
    else:
        st.error("Start date cannot be after the end date.")
else:
    if start_error:
        st.error(start_error)
    if end_error:
        st.error(end_error)

# Run the app using `streamlit run <filename.py>`

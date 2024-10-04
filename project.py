import pandas as pd
import streamlit as st
from datetime import datetime
import warnings
import plotly.graph_objects as go

warnings.filterwarnings("ignore")

# Load the data using the raw GitHub links
df1 = pd.read_csv('https://raw.githubusercontent.com/duongtan259/Electricity-Consumption-and-Pricing/main/Electricity_20-09-2024.csv', delimiter=';')
df2 = pd.read_csv('https://raw.githubusercontent.com/duongtan259/Electricity-Consumption-and-Pricing/main/sahkon-hinta-010121-240924.csv')

# Step 1: Trim whitespace and convert time columns to datetime
df1['Time'] = df1['Time'].str.strip()
df1['Time'] = pd.to_datetime(df1['Time'], format='%d.%m.%Y %H:%M', errors='coerce')
df1['Date'] = df1['Time'].dt.date
df1['Date'] = pd.to_datetime(df1['Date'], format='%Y-%m-%d', errors='coerce')

# Define the columns to convert and clean the data
columns_to_convert = ['Energy (kWh)', 'Energy night(kWh)', 'Energy day (kWh)', 'Temperature']
for column in columns_to_convert:
    df1[column] = df1[column].str.replace(',', '.', regex=False)
    df1[column] = df1[column].astype(float)

# Fill null values in the Temperature column with 0
df1['Temperature'] = df1['Temperature'].fillna(0)

# Step 1: Trim whitespace and convert time columns to datetime for df2
df2['Time'] = df2['Time'].str.strip()
df2['Time'] = pd.to_datetime(df2['Time'], format='%d-%m-%Y %H:%M:%S', errors='coerce')
df2['Date'] = df2['Time'].dt.date
df2['Date'] = pd.to_datetime(df2['Date'], format='%Y-%m-%d', errors='coerce')

# Step 1: Join the DataFrames on 'Time'
merged_df = pd.merge(df1, df2, on='Time', how='inner')
merged_df = merged_df.drop(columns=['Date_y'])  # Drop 'Date_y', keeping 'Date_x'
merged_df.rename(columns={'Date_x': 'Date'}, inplace=True)

# Step 3: Calculate hourly bill paid
merged_df['Hourly Bill'] = merged_df['Energy (kWh)'] * (merged_df['Price (cent/kWh)'] / 100)

# Convert 'Date' column to datetime type
merged_df['Date'] = pd.to_datetime(merged_df['Date'])

# Function to validate and parse the date input
def validate_date(date_input):
    try:
        parsed_date = datetime.strptime(date_input, "%Y-%m-%d")
        return parsed_date, None
    except ValueError:
        return None, "Invalid date format. Please use YYYY-MM-DD."

# Streamlit app
st.title("Electricity Consumption and Pricing Dashboard")

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

# Filter the DataFrame based on the selected dates when both dates are valid
if st.session_state.start_date and st.session_state.end_date:
    start_datetime = pd.to_datetime(st.session_state.start_date)
    end_datetime = pd.to_datetime(st.session_state.end_date)

    filtered_df = merged_df[
        (merged_df['Date'] >= start_datetime) & 
        (merged_df['Date'] <= end_datetime)
    ]

    # Calculate metrics based on filtered DataFrame
    total_consumption = filtered_df['Energy (kWh)'].sum()
    total_bill = filtered_df['Hourly Bill'].sum()
    average_hourly_price = filtered_df['Price (cent/kWh)'].mean()

    # Avoid division by zero
    average_paid_price = (total_bill / total_consumption * 100) if total_consumption > 0 else 0

    # Display the results
    st.write(f"\nShowing range: {st.session_state.start_date.date()} ---> {st.session_state.end_date.date()}\n")
    st.write(f"Total consumption over the period: {total_consumption:.1f} kWh")
    st.write(f"Total bill over the period: {total_bill:.1f} €")
    st.write(f"Average hourly price: {average_hourly_price:.2f} cents")
    st.write(f"Average paid price: {average_paid_price:.2f} cents")

# Show errors if there are any issues with the dates
if start_error:
    st.error(start_error)
if end_error:
    st.error(end_error)

# Ensure 'Date' is in datetime format for resampling
filtered_df['Date'] = pd.to_datetime(filtered_df['Date'])

# Step 1: Create a selection box for grouping interval
grouping_interval = st.selectbox("Select grouping interval", ("Daily", "Weekly", "Monthly"))

# Step 2: Calculate metrics based on the selected interval
if grouping_interval == 'Daily':
    # Group by date
    summary = filtered_df.groupby('Date').agg(
        Daily_Consumption=('Energy (kWh)', 'sum'),
        Daily_Bill=('Hourly Bill', 'sum'),
        Average_Price=('Price (cent/kWh)', 'mean'),
        Average_Temperature=('Temperature', 'mean')
    ).reset_index()

elif grouping_interval == 'Weekly':
    # Group by week
    summary = filtered_df.resample('W', on='Date').agg(
        Weekly_Consumption=('Energy (kWh)', 'sum'),
        Weekly_Bill=('Hourly Bill', 'sum'),
        Average_Price=('Price (cent/kWh)', 'mean'),
        Average_Temperature=('Temperature', 'mean')
    ).reset_index()

elif grouping_interval == 'Monthly':
    # Group by month
    summary = filtered_df.resample('M', on='Date').agg(
        Monthly_Consumption=('Energy (kWh)', 'sum'),
        Monthly_Bill=('Hourly Bill', 'sum'),
        Average_Price=('Price (cent/kWh)', 'mean'),
        Average_Temperature=('Temperature', 'mean')
    ).reset_index()

else:
    st.warning("Invalid grouping interval selected.")
    summary = pd.DataFrame()  # Empty DataFrame if invalid input

# Step 3: Calculate total metrics
if not summary.empty:
    total_consumption = summary['Daily_Consumption'].sum() if grouping_interval == 'Daily' else \
                        summary['Weekly_Consumption'].sum() if grouping_interval == 'Weekly' else \
                        summary['Monthly_Consumption'].sum()

    total_bill = summary['Daily_Bill'].sum() if grouping_interval == 'Daily' else \
                 summary['Weekly_Bill'].sum() if grouping_interval == 'Weekly' else \
                 summary['Monthly_Bill'].sum()

    average_price = summary['Average_Price'].mean() if grouping_interval == 'Daily' else \
                    summary['Average_Price'].mean() if grouping_interval == 'Weekly' else \
                    summary['Average_Price'].mean()

    average_temperature = summary['Average_Temperature'].mean() if grouping_interval == 'Daily' else \
                         summary['Average_Temperature'].mean() if grouping_interval == 'Weekly' else \
                         summary['Average_Temperature'].mean()

    # Step 4: Visualization of individual metrics using Plotly

    # Set figure size
    chart_width = 800
    chart_height = 600

    # Consumption plot
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=summary['Date'], 
                               y=summary['Daily_Consumption'] if grouping_interval == 'Daily' else 
                                 summary['Weekly_Consumption'] if grouping_interval == 'Weekly' else 
                                 summary['Monthly_Consumption'],
                               mode='lines+markers',
                               name='Consumption (kWh)'))
    fig1.update_layout(title='Total Consumption Over Time',
                       xaxis_title='Date',
                       yaxis_title='Consumption (kWh)',
                       xaxis_tickangle=-45,
                       width=chart_width,
                       height=chart_height)
    st.plotly_chart(fig1)

    # Bill plot
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=summary['Date'], 
                               y=summary['Daily_Bill'] if grouping_interval == 'Daily' else 
                                 summary['Weekly_Bill'] if grouping_interval == 'Weekly' else 
                                 summary['Monthly_Bill'],
                               mode='lines+markers',
                               name='Bill (€)', line=dict(color='orange')))
    fig2.update_layout(title='Total Bill Over Time',
                       xaxis_title='Date',
                       yaxis_title='Bill (€)',
                       xaxis_tickangle=-45,
                       width=chart_width,
                       height=chart_height)
    st.plotly_chart(fig2)

    # Average Price plot
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=summary['Date'], 
                               y=summary['Average_Price'],
                               mode='lines+markers',
                               name='Average Price (cent/kWh)', line=dict(color='green')))
    fig3.update_layout(title='Average Price Over Time',
                       xaxis_title='Date',
                       yaxis_title='Average Price (cent/kWh)',
                       xaxis_tickangle=-45,
                       width=chart_width,
                       height=chart_height)
    st.plotly_chart(fig3)

    # Average Temperature plot
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=summary['Date'], 
                               y=summary['Average_Temperature'],
                               mode='lines+markers',
                               name='Average Temperature (°C)', line=dict(color='red')))
    fig4.update_layout(title='Average Temperature Over Time',
                       xaxis_title='Date',
                       yaxis_title='Average Temperature (°C)',
                       xaxis_tickangle=-45,
                       width=chart_width,
                       height=chart_height)
    st.plotly_chart(fig4)


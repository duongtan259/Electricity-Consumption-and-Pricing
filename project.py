import pandas as pd
import streamlit as st
from datetime import datetime
import warnings
import plotly.graph_objects as go

# Suppress warnings to clean up the output
warnings.filterwarnings("ignore")

# Load the data from GitHub using raw links
df1 = pd.read_csv('https://raw.githubusercontent.com/duongtan259/Electricity-Consumption-and-Pricing/main/Electricity_20-09-2024.csv', delimiter=';')
df2 = pd.read_csv('https://raw.githubusercontent.com/duongtan259/Electricity-Consumption-and-Pricing/main/sahkon-hinta-010121-240924.csv')

# Step 1: Clean 'Time' columns, strip whitespace, and convert to datetime format
df1['Time'] = df1['Time'].str.strip()  # Remove leading/trailing spaces
df1['Time'] = pd.to_datetime(df1['Time'], format='%d.%m.%Y %H:%M', errors='coerce')  # Convert to datetime
df1['Date'] = df1['Time'].dt.date  # Extract the date portion
df1['Date'] = pd.to_datetime(df1['Date'], format='%Y-%m-%d', errors='coerce')  # Ensure correct datetime format

# Step 2: Convert relevant columns to numeric after replacing commas with periods for decimals
columns_to_convert = ['Energy (kWh)', 'Energy night(kWh)', 'Energy day (kWh)', 'Temperature']
for column in columns_to_convert:
    df1[column] = df1[column].str.replace(',', '.', regex=False)  # Replace commas with periods
    df1[column] = df1[column].astype(float)  # Convert the string to float for numerical analysis

# Fill any missing values in the 'Temperature' column with 0
df1['Temperature'] = df1['Temperature'].fillna(0)

# Step 3: Repeat the cleaning process for df2 (Electricity pricing data)
df2['Time'] = df2['Time'].str.strip()  # Remove leading/trailing spaces
df2['Time'] = pd.to_datetime(df2['Time'], format='%d-%m-%Y %H:%M:%S', errors='coerce')  # Convert to datetime
df2['Date'] = df2['Time'].dt.date  # Extract the date portion
df2['Date'] = pd.to_datetime(df2['Date'], format='%Y-%m-%d', errors='coerce')  # Ensure correct datetime format

# Step 4: Merge the two dataframes on the 'Time' column to align consumption and pricing data
merged_df = pd.merge(df1, df2, on='Time', how='inner')

# Drop duplicate 'Date_y' column (because 'Date_x' is sufficient) and rename 'Date_x' to 'Date'
merged_df = merged_df.drop(columns=['Date_y'])
merged_df.rename(columns={'Date_x': 'Date'}, inplace=True)

# Step 5: Calculate the hourly bill based on energy consumption and electricity price
merged_df['Hourly Bill'] = merged_df['Energy (kWh)'] * (merged_df['Price (cent/kWh)'] / 100)

# Streamlit app interface
st.title("Electricity Consumption and Pricing Dashboard")

# Step 6: Capture start and end date inputs from the user using a calendar-type date selector
start_date = st.date_input("Select Start Date:", value=datetime(2024, 1, 1))
end_date = st.date_input("Select End Date:", value=datetime(2024, 9, 30))

# Step 7: Ensure the filtered DataFrame is only processed if both dates are valid
if start_date and end_date:
    # Filter the data based on the provided date range
    filtered_df = merged_df[
        (merged_df['Date'] >= pd.to_datetime(start_date)) & 
        (merged_df['Date'] <= pd.to_datetime(end_date))
    ]

    # Ensure 'Date' is in datetime format for later processing
    filtered_df['Date'] = pd.to_datetime(filtered_df['Date'])

    # Step 8: Calculate metrics based on the filtered DataFrame
    total_consumption = filtered_df['Energy (kWh)'].sum()
    total_bill = filtered_df['Hourly Bill'].sum()
    average_hourly_price = filtered_df['Price (cent/kWh)'].mean()

    # Avoid division by zero when calculating average paid price
    average_paid_price = (total_bill / total_consumption * 100) if total_consumption > 0 else 0

    # Display the results in the dashboard
    st.write(f"\nShowing range: {start_date} ---> {end_date}\n")
    st.write(f"Total consumption over the period: {total_consumption:.1f} kWh")
    st.write(f"Total bill over the period: {total_bill:.1f} €")
    st.write(f"Average hourly price: {average_hourly_price:.2f} cents")
    st.write(f"Average paid price: {average_paid_price:.2f} cents")

    # Grouping interval selection for time-based aggregation
    grouping_interval = st.selectbox("Select grouping interval", ("Daily", "Weekly", "Monthly"))

    # Step 9: Aggregate data based on the selected interval
    if grouping_interval == 'Daily':
        summary = filtered_df.groupby('Date').agg(
            Daily_Consumption=('Energy (kWh)', 'sum'),
            Daily_Bill=('Hourly Bill', 'sum'),
            Average_Price=('Price (cent/kWh)', 'mean'),
            Average_Temperature=('Temperature', 'mean')
        ).reset_index()

    elif grouping_interval == 'Weekly':
        summary = filtered_df.resample('W', on='Date').agg(
            Weekly_Consumption=('Energy (kWh)', 'sum'),
            Weekly_Bill=('Hourly Bill', 'sum'),
            Average_Price=('Price (cent/kWh)', 'mean'),
            Average_Temperature=('Temperature', 'mean')
        ).reset_index()

    elif grouping_interval == 'Monthly':
        summary = filtered_df.resample('M', on='Date').agg(
            Monthly_Consumption=('Energy (kWh)', 'sum'),
            Monthly_Bill=('Hourly Bill', 'sum'),
            Average_Price=('Price (cent/kWh)', 'mean'),
            Average_Temperature=('Temperature', 'mean')
        ).reset_index()

    # Step 10: Visualization of data using Plotly
    if not summary.empty:
        # Set chart dimensions
        chart_width = 800
        chart_height = 600

        # Consumption plot
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=summary['Date'], 
                                   y=summary.iloc[:, 1],  # Consumption column depending on interval
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
                                   y=summary.iloc[:, 2],  # Bill column depending on interval
                                   mode='lines+markers',
                                   name='Bill (€)', line=dict(color='orange')))
        fig2.update_layout(title='Total Bill Over Time',
                           xaxis_title='Date',
                           yaxis_title='Bill (€)',
                           xaxis_tickangle=-45,
                           width=chart_width,
                           height=chart_height)
        st.plotly_chart(fig2)

        # Average price plot
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=summary['Date'], 
                                   y=summary['Average_Price'], 
                                   mode='lines+markers',
                                   name='Average Price (cent/kWh)', line=dict(color='green')))
        fig3.update_layout(title='Average Electricity Price Over Time',
                           xaxis_title='Date',
                           yaxis_title='Price (cent/kWh)',
                           xaxis_tickangle=-45,
                           width=chart_width,
                           height=chart_height)
        st.plotly_chart(fig3)

        # Temperature plot
        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(x=summary['Date'], 
                                   y=summary['Average_Temperature'], 
                                   mode='lines+markers',
                                   name='Temperature (°C)', line=dict(color='blue')))
        fig4.update_layout(title='Average Temperature Over Time',
                           xaxis_title='Date',
                           yaxis_title='Temperature (°C)',
                           xaxis_tickangle=-45,
                           width=chart_width,
                           height=chart_height)
        st.plotly_chart(fig4)
else:
    st.warning("Please select a valid date range.")


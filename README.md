# Electricity Consumption and Pricing Dashboard

## Project Overview

The **Electricity Consumption and Pricing Dashboard** is a Streamlit application that allows users to visualize and analyze their electricity consumption and pricing data over time. By integrating data from two sources—electricity consumption records and pricing information—the app enables users to gain insights into their energy usage and costs, helping them make informed decisions about their energy consumption.

## Features

- **Data Loading**: The application loads electricity consumption data from a CSV file and pricing data from another CSV file.
- **Data Cleaning**: It processes the loaded data to trim whitespace, convert date and time formats, and handle missing values.
- **Date Filtering**: Users can input a start and end date to filter the data and focus on specific periods.
- **Metrics Calculation**: The app calculates key metrics such as total energy consumption, total bill, average hourly price, and average paid price.
- **Dynamic Grouping**: Users can select a grouping interval (daily, weekly, monthly) to aggregate the data and view trends over time.
- **Visualizations**: The app provides interactive visualizations using Plotly for metrics such as total consumption, total bill, average price, and average temperature.

## Technologies Used

- **Python**: The main programming language for developing the application.
- **Pandas**: For data manipulation and analysis.
- **Streamlit**: To create the web application interface.
- **Plotly**: For creating interactive visualizations.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/duongtan259/Electricity-Consumption-and-Pricing.git
   ```

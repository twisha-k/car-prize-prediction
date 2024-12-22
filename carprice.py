import numpy as np
import pandas as pd
import streamlit as st

# Dictionary containing positive integers in the form of words as keys and corresponding former as values.
words_dict = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "eight": 8, "twelve": 12}

# Function to map words to numbers
def num_map(series):
    return series.map(words_dict)

# Loading the dataset
@st.cache_data
def load_data():
    # Reading the dataset
    try:
        cars_df = pd.read_csv("car-prices.csv")
    except FileNotFoundError:
        st.error("Dataset file 'car-prices.csv' not found. Please check the file path.")
        return None

    # Extract the name of the manufacturers from the car names
    car_companies = pd.Series([car.split(" ")[0] for car in cars_df['CarName']], index=cars_df.index)
    cars_df['car_company'] = car_companies

    # Replace misspelled 'car_company' names with correct names
    replacements = {
        "vw": "volkswagen",
        "vokswagen": "volkswagen",
        "porcshce": "porsche",
        "toyouta": "toyota",
        "Nissan": "nissan",
        "maxda": "mazda"
    }
    cars_df['car_company'] = cars_df['car_company'].replace(replacements)

    # Drop 'CarName' column
    cars_df.drop(columns=['CarName'], inplace=True)

    # Map the values of 'doornumber' and 'cylindernumber' columns to their numeric values
    cars_df['cylindernumber'] = num_map(cars_df['cylindernumber'])
    cars_df['doornumber'] = num_map(cars_df['doornumber'])

    # Create dummy variables for 'carbody' with 1 column less
    car_body_new_dummies = pd.get_dummies(cars_df['carbody'], drop_first=True, dtype=int)

    # Get all categorical columns and create dummy variables
    cars_categorical_df = cars_df.select_dtypes(include=['object'])
    cars_dummies_df = pd.get_dummies(cars_categorical_df, drop_first=True, dtype=int)

    # Drop the categorical columns and concatenate the dummy variables
    cars_df.drop(list(cars_categorical_df.columns), axis=1, inplace=True)
    cars_df = pd.concat([cars_df, cars_dummies_df], axis=1)

    # Final selected columns
    final_columns = ['carwidth', 'enginesize', 'horsepower', 'drivewheel_fwd', 'car_company_buick', 'price']
    return cars_df[final_columns]

# Load the processed dataset
final_cars_df = load_data()

if final_cars_df is not None:
    # Import the individual Python files
    try:
        import home
        import data
        import plots
        import predict
    except ImportError as e:
        st.error(f"Module import error: {e}")

    # Create a dictionary 'pages_dict'
    pages_dict = {
        "Home": home,
        "View Data": data,
        "Visualise Data": plots,
        "Predict": predict
    }

    # Add radio buttons in the sidebar for navigation
    st.sidebar.title('Navigation')
    user_choice = st.sidebar.radio("Go to", tuple(pages_dict.keys()))

    # Navigate to the selected page
    if user_choice == "Home":
        home.app()  # The 'app()' function should not take any input if the selection option is "Home".
    else:
        selected_page = pages_dict[user_choice]
        selected_page.app(final_cars_df)

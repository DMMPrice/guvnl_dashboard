import streamlit as st
import pandas as pd
import plotly.express as px
import aiofiles
import asyncio
import io

st.set_page_config(layout="wide")

# Add a main header
st.header('GUVNL Dashboard')

# Add sub-links in the sidebar
st.sidebar.title('Navigation')
page = st.sidebar.radio('Go to', ['Demand', 'Open Access', 'Price', 'Solar', 'Wind'])

guvnl_files = {
    'Demand': './Data/Demand_(Forecast).csv',
    'Open Access': './Data/Open_Access_(Forecast).csv',
    'Price': './Data/Price.csv',
    'Solar': './Data/Solar_Generation.csv',
    'Wind': './Data/Wind_Generation.csv'
}

async def fetch_data(file_path):
    async with aiofiles.open(file_path, mode='r') as f:
        data = await f.read()
        return pd.read_csv(io.StringIO(data))

async def load_data():
    data = await fetch_data(guvnl_files[page])
    data['TimeStamp'] = pd.to_datetime(data['TimeStamp'], format='%d-%m-%Y %H:%M', dayfirst=True)
    data['Year'] = data['TimeStamp'].dt.year
    return data

data = asyncio.run(load_data())

def display_dashboard(title, y_columns, y_labels):
    st.title(title)

    # Create a selectbox for year selection with "All years" option
    years = ['All years'] + list(data['Year'].unique())
    selected_year = st.selectbox('Select Year', years)

    # Filter data based on selected year
    if selected_year == 'All years':
        filtered_data = data
    else:
        filtered_data = data[data['Year'] == int(selected_year)]

    # Resample data to hourly intervals
    filtered_data.set_index('TimeStamp', inplace=True)
    data_resampled = filtered_data.resample('h').mean().reset_index()

    # Create a line plot
    fig = px.line(data_resampled, x='TimeStamp', y=y_columns,
                  labels={'value': 'Demand', 'TimeStamp': 'Time'},
                  title=y_labels)
    fig.update_traces(line=dict(color='red'), selector=dict(name=y_columns[0]))
    fig.update_traces(line=dict(color='blue'), selector=dict(name=y_columns[1]))

    # Create two equal-width columns
    col1, col2 = st.columns([12, 5])

    # Display plot in the first column
    col1.plotly_chart(fig, use_container_width=True)

    # Drop the Year column from the detailed data
    filtered_data = filtered_data.reset_index().drop(columns=['Year'])

    # Display detailed data in the second column without the index
    col2.write(filtered_data)

if page == 'Demand':
    display_dashboard('Demand Forecast Dashboard', ['Demand(Actual)', 'Demand(Pred)'], 'Actual vs Predicted Demand (MW)')
elif page == 'Open Access':
    display_dashboard('Open Access Forecast Dashboard', ['Actual', 'Pred'], 'Actual vs Predicted Open Access Demand (MW)')
else:
    st.title(f'{page} Data')
    st.write(data)
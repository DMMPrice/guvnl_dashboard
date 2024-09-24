import streamlit as st
import pandas as pd
import plotly.express as px
import io

st.set_page_config(layout="wide")

# Add a main header
st.header('GUVNL Dashboard')

# Add sub-links in the sidebar
st.sidebar.title('Navigation')
page = st.sidebar.radio('Go to', ['Demand', 'Open Access', 'Price', 'Solar', 'Wind'])

guvnl_files = {
    'Demand': './Data/Demand_(Forecast).csv',
    'Open Access': './Data/Demand_(Forecast).csv',
    'Price': './Data/Demand_(Forecast).csv',
    'Solar': './Data/Demand_(Forecast).csv',
    'Wind': './Data/Demand_(Forecast).csv'
}

def fetch_data(file_path):
    with open(file_path, mode='r') as f:
        data = f.read()
        return pd.read_csv(io.StringIO(data))

def load_data():
    data = fetch_data(guvnl_files[page])
    data['TimeStamp'] = pd.to_datetime(data['TimeStamp'], format='%d/%m/%y %H:%M', dayfirst=True)
    data['Year'] = data['TimeStamp'].dt.year
    return data

data = load_data()

def display_dashboard(title, y_columns, y_labels, default_columns):
    st.title(title)

    # Create a selectbox for FY year selection with "All FYs" option
    years = ['All FYs'] + [f"{year} - {str(year + 1)[-2:]}" for year in data['Year'].unique()]
    selected_year = st.selectbox('Select FY Year', years)

    # Filter data based on selected FY year
    if selected_year == 'All FYs':
        filtered_data = data
    else:
        year = int(selected_year.split(' - ')[0])
        filtered_data = data[data['Year'] == year]

    # Resample data to hourly intervals
    filtered_data.set_index('TimeStamp', inplace=True)
    data_resampled = filtered_data.resample('h').mean().reset_index()

    # Create a line plot
    fig = px.line(data_resampled, x='TimeStamp', y=y_columns,
                  labels={'value': 'Demand', 'TimeStamp': 'Time'},
                  title=y_labels)
    fig.update_traces(line=dict(color='rgb(235, 223, 190)'), selector=dict(name=y_columns[0]))
    fig.update_traces(line=dict(color='#93dae6'), selector=dict(name=y_columns[1]))

    # Create two equal-width columns
    col1, col2 = st.columns([12, 5])

    # Display plot in the first column
    col1.plotly_chart(fig, use_container_width=True)

    # Drop the Year column from the detailed data
    filtered_data = filtered_data.reset_index().drop(columns=['Year'])

    # Create a multiselect for column selection
    columns_to_display = st.multiselect('Select columns to display', filtered_data.columns.tolist(), default=default_columns)

    # Display detailed data in the second column without the index
    col2.write(filtered_data[columns_to_display])

if page == 'Demand':
    display_dashboard('Demand Forecast Dashboard', ['Demand(Actual)', 'Demand(Pred)'],
                      'Actual vs Predicted Demand (MW)', ['TimeStamp', 'Demand(Actual)', 'Demand(Pred)'])
elif page == 'Open Access':
    display_dashboard('Open Access Forecast Dashboard', ['Actual', 'Pred'],
                      'Actual vs Predicted Open Access Demand (MW)', ['TimeStamp', 'Actual', 'Pred'])
elif page == 'Price':
    display_dashboard('Price Forecast Dashboard', ['Price (Rs/ KWh)','Pred Price(Rs/ KWh)'],
                      'Actual vs Predicted Price (Rs/kWh)', ['TimeStamp', 'Price (Rs/ KWh)', 'Pred Price(Rs/ KWh)'])
elif page == 'Solar':
    display_dashboard('Solar Forecast Dashboard', ['Solar(Actual)', 'Solar(Pred)'],
                      'Actual vs Predicted Solar Generation (MW)', ['TimeStamp', 'Solar(Actual)', 'Solar(Pred)'])
elif page == 'Wind':
    display_dashboard('Wind Forecast Dashboard', ['Wind(Actual)', 'Wind(Pred)'],
                      'Actual vs Predicted Wind Generation (MW)', ['TimeStamp', 'Wind(Actual)', 'Wind(Pred)'])
else:
    st.title(f'{page} Data')
    st.write(data)
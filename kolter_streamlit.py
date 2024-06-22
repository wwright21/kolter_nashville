import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px

# set page configurations
st.set_page_config(
    page_title="Kolter Research",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded" # 'collapsed' or 'expanded'
)

# the custom CSS lives here:
hide_default_format = """
        <style>
            .reportview-container .main footer {visibility: hidden;}    
            #MainMenu, footer {visibility: hidden;}
            section.main > div:has(~ footer ) {
                padding-bottom: 1px;
                padding-left: 20px;
                padding-right: 20px;
                padding-top: 10px;
            }
            [data-testid="stSidebar"] {
                padding-left: 18px;
                padding-right: 18px;
                padding-top: 0px;
                }
            [data-testid="collapsedControl"] {
                color: #FFFFFF;
                background-color: #737373;
                } 
            [class="stDeployButton"] {
                display: none;
                } 
            span[data-baseweb="tag"] {
                background-color: #737373 
                }
            div.stActionButton{visibility: hidden;}
        </style>
       """

# inject the CSS
st.markdown(hide_default_format, unsafe_allow_html=True)

# county select helper text
st.sidebar.markdown(
    "<p style='text-align:center;color:#252525;'>Select metro Nashville county:</p>", unsafe_allow_html=True)

# create the sidebar dropdown menu
county_list = [
    'Cannon',
    'Cheatham',
    'Davidson',
    'Dickson',
    'Hickman',
    'Macon',
    'Maury',
    'Robertson',
    'Rutherford',
    'Smith',
    'Sumner',
    'Trousdale',
    'Williamson',
    'Wilson'
]

# county select dropdown
st.sidebar.selectbox(
    label='label',
    label_visibility='collapsed',
    options=county_list
)

# sidebar separator
st.sidebar.divider()

# county select helper text
st.sidebar.markdown(
    "<p style='text-align:center;color:#252525;'>Select mapping variable:</p>", unsafe_allow_html=True)

# choropleth map variable select
st.sidebar.selectbox(
    label='label',
    label_visibility='collapsed',
    options=[
        '2023 Total Population',
        '2023 Population Density',
        '2028 Projected Population Change',
        '2023 Median Household Income'
    ]
)
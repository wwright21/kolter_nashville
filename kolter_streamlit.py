import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# set year variables to be used in map layer
current_year = 2024
projected_year = 2029

# set page configurations
st.set_page_config(
    page_title="Kolter - Nashville",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded" # 'collapsed' or 'expanded'
)

# county select helper text
st.sidebar.markdown(
    "<p style='text-align:center;color:#000000;'>Select metro Nashville county:</p>", 
    unsafe_allow_html=True
    )

# create the sidebar dropdown menu
county_list = {
    '47015': 'Cannon',
    '47021': 'Cheatham',
    '47037': 'Davidson',
    '47043': 'Dickson',
    '47081': 'Hickman',
    '47111': 'Macon',
    '47119': 'Maury',
    '47147': 'Robertson',
    '47149': 'Rutherford',
    '47159': 'Smith',
    '47165': 'Sumner',
    '47169': 'Trousdale',
    '47187': 'Williamson',
    '47189': 'Wilson'
}

# county select dropdown
county = st.sidebar.selectbox(
    label='label',
    label_visibility='collapsed',
    options=county_list.values(),
    index=2,
    key="county_dropdown"  
)

# sidebar separator
st.sidebar.markdown(
    "<p style='text-align:center;color:#000000;'>---------------</p>", 
    unsafe_allow_html=True
    )

# Update session state with selected county upon dropdown change
if 'county_dropdown' in st.session_state:  # Check if this is the first run
  st.session_state['selected_county'] = county

# set the dashboard subtitle now that the county has been selected
title_font_size = 30
title_margin_top = 25
title_margin_bottom = -20

st.markdown(
    f"""
    <div style='margin-top: {title_margin_top}px; margin-bottom: {title_margin_bottom}px;'>
        <span style='font-size: {title_font_size}px; font-weight: 700;'>Nashville Development Dashboard:</span>
        <span style='font-size: {title_font_size}px; font-weight: 200;'>{county} County Drilldown</span>
    </div>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def load_county_outline(selected_county):
    # Load county outlines from GeoPackage
    county_outline = gpd.read_file('Data/counties_simp.gpkg')

    # Define a function to filter by selected county (called within the cached function)
    def filter_by_county(selected_county):
        return county_outline[county_outline['county_stripped'] == selected_county]

    # Access selected county from session state (assuming a default is set elsewhere)
    selected_county = st.session_state.get('selected_county')

    # Filter county outlines based on selected_county
    county_outline = filter_by_county(selected_county).set_index('FIPS')

    return county_outline


# county select helper text
st.sidebar.markdown(
    "<p style='text-align:center;color:#000000;'>Map layer (by Census tract):</p>", unsafe_allow_html=True)

# choropleth map variable select
attribute = st.sidebar.selectbox(
    label='label',
    label_visibility='collapsed',
    options=[
        f'{current_year} Total Population',
        f'{current_year} Senior Population (65+)', 
        f'{current_year} Population Density',
        f'{current_year}-{projected_year} Population Growth Rate',
        f'{current_year} Median Household Income',
        f'{current_year}-{projected_year} Homeownership Growth Rate'
    ]
)

# opacity slider helper text
st.sidebar.write(" ")
st.sidebar.write(" ")
st.sidebar.markdown(
    "<p style='text-align:center;color:#000000;'>Layer opacity:</p>", unsafe_allow_html=True)

# set choropleth opacity
opacity = st.sidebar.slider(
    label='label',
    label_visibility='collapsed',
    min_value=0.2,
    max_value=1.0,
    value=0.6,
    step=0.1
)

# Basemap helper text
st.sidebar.write(" ")
st.sidebar.markdown(
    "<p style='text-align:center;color:#000000;'>Basemap:</p>", unsafe_allow_html=True)

# set basemap
base_map = st.sidebar.radio(
    label='label',
    label_visibility='collapsed',
    options=['Light', 'Dark'],
    index=0,
    horizontal=True,
)

# convert basemap to cartoDB basemap
base_map_dict = {
    'Light': 'carto-positron',
    'Dark': 'carto-darkmatter'
}

# sidebar separator
st.sidebar.markdown(
    "<p style='text-align:center;color:#000000;'>---------------</p>", 
    unsafe_allow_html=True
    )

# @st.cache_data
def load_geometry():
    # Load the geometry data
    return gpd.read_file('Data/tracts_simp.gpkg')

# @st.cache_data
def load_attribute(attribute_file):
    # Load an attribute data
    return pd.read_csv(attribute_file, dtype={'GEOID': 'str'})

# CHOROPLETH MAP ---------------------------------------------------------------------
# Load the geometry data once
geometry_gdf = load_geometry()

# Map dropdown to file paths
attribute_files = {
    f'{current_year} Total Population': f'Data/CSV/Color-coded maps - {current_year} Total Population.csv',
    f'{current_year} Senior Population (65+)': f'Data/CSV/Color-coded maps - {current_year} Senior Population.csv',
    f'{current_year} Population Density': f'Data/CSV/Color-coded maps - {current_year} Population Density.csv',
    f'{current_year}-{projected_year} Population Growth Rate': f'Data/CSV/Color-coded maps - {current_year}-{projected_year} Growth Rate Population.csv',
    f'{current_year} Median Household Income': f'Data/CSV/Color-coded maps - {current_year} Median Household Income.csv',
    f'{current_year}-{projected_year} Homeownership Growth Rate': f'Data/CSV/Color-coded maps - {current_year}-{projected_year} Growth Rate Owner Occ HUs.csv'
}

# Map dropdown to column names
attribute_columnNames = {
    f'{current_year} Total Population': f'{current_year} Total Population',
    f'{current_year} Senior Population (65+)': f'{current_year} Senior Population',
    f'{current_year} Population Density': f'{current_year} Population Density',
    f'{current_year}-{projected_year} Population Growth Rate': f'{current_year}-{projected_year} Growth Rate: Population',
    f'{current_year} Median Household Income': f'{current_year} Median Household Income',
    f'{current_year}-{projected_year} Homeownership Growth Rate': f'{current_year}-{projected_year} Growth Rate: Owner Occ HUs'
}

# Map dropdown to tooltip number formats
attribute_numberFormats = {
    f'{current_year} Total Population': lambda x: f"{x:,}",
    f'{current_year} Senior Population (65+)': lambda x: f"{x:,}",
    f'{current_year} Population Density': lambda x: f"{x:,.0f}",
    f'{current_year}-{projected_year} Population Growth Rate': lambda x: f"{x * 100:.2f}%",
    f'{current_year} Median Household Income': lambda x: f"${x:,.0f}",
    f'{current_year}-{projected_year} Homeownership Growth Rate': lambda x: f"{x * 100:.2f}%"  
}

# Map dropdown to colorbar number formats
attribute_colorbarFormats = {
    f'{current_year} Total Population': ',',
    f'{current_year} Senior Population (65+)': ',',
    f'{current_year} Population Density': ',',
    f'{current_year}-{projected_year} Population Growth Rate': '.2%',
    f'{current_year} Median Household Income': '$,',
    f'{current_year}-{projected_year} Homeownership Growth Rate': '.1%'  
}

# Map dropdown to choropleth colors
attribute_choroColor = {
    f'{current_year} Total Population': 'Blues',
    f'{current_year} Senior Population (65+)': 'Oranges',
    f'{current_year} Population Density': 'BuPu',
    f'{current_year}-{projected_year} Population Growth Rate': 'Reds',
    f'{current_year} Median Household Income': 'Greens',
    f'{current_year}-{projected_year} Homeownership Growth Rate': 'Purples'
}

# Map dropdown to choropleth legend title
attribute_choroLegend = {
    f'{current_year} Total Population': 'Population',
    f'{current_year} Senior Population (65+)': 'Senior Population',
    f'{current_year} Population Density': 'Population Density',
    f'{current_year}-{projected_year} Population Growth Rate': 'Population Growth Rate',
    f'{current_year} Median Household Income': 'Median Income',
    f'{current_year}-{projected_year} Homeownership Growth Rate': 'Homeownership Growth Rate'
}

# Load the selected attribute data
attribute_df = load_attribute(attribute_files[attribute])
attribute_df['tooltip'] = attribute_df[attribute_columnNames[attribute]].apply(attribute_numberFormats[attribute])

# Before merging, have to format the GEOID column
def split_and_format(value):
    # Split the value on the period
    parts = value.split('.')
    # Take the first part and concatenate it with the zero-filled second part
    formatted_value = parts[0] + parts[1].zfill(2)
    return formatted_value


# Apply the function to the GEOID column
attribute_df['GEOID'] = attribute_df['GEOID'].apply(split_and_format)

# Merge geometry with attribute data
merged_gdf = geometry_gdf.merge(attribute_df, on='GEOID').set_index('GEOID')
merged_gdf['county_name'] = merged_gdf['FIPS'].map(county_list)

# Initialize session state if not already done
if 'map_center' not in st.session_state:
  st.session_state['map_center'] = [36.00734326974716, -86.75460358901837]
if 'zoom_level' not in st.session_state:
  st.session_state['zoom_level'] = 7.2

# define mapping parameters
map_starting_center = st.session_state['map_center']  
map_starting_zoom = st.session_state['zoom_level']

# define the main mapping figure
fig = px.choropleth_mapbox(
    merged_gdf,
    geojson=merged_gdf.geometry,
    locations=merged_gdf.index,
    color=attribute_columnNames[attribute],
    color_continuous_scale=attribute_choroColor[attribute],
    custom_data=['tooltip', 'county_name'],
    labels={
        'tooltip': attribute_columnNames[attribute]
    },
    center={"lat": map_starting_center[0], "lon": map_starting_center[1]},
    mapbox_style=base_map_dict[base_map],
    zoom=map_starting_zoom,
    opacity=opacity,
    height=650
    )

# customize the tooltip for the choropleth map
fig.update_traces(
    hovertemplate = "<b>%{customdata[1]} County: </b>%{customdata[0]}",
    marker_line_width=0.2
)

fig.update_layout(
    margin=dict(l=10, r=10, t=20, b=1),
)

# style and customize the map
fig.update_coloraxes(
    colorbar_x=0.5,
    colorbar_y=0,
    colorbar_thickness=30,
    colorbar_tickformat = attribute_colorbarFormats[attribute],
    colorbar_tickfont_size=12,
    colorbar_title_font_size=14,
    colorbar_orientation='h',
    colorbar_title_text=attribute_choroLegend[attribute],
    colorbar_tickangle=90
    )

# Load the county outline
selected_county = st.session_state.get('selected_county')
county_outline = load_county_outline(selected_county)

# extract coordinates
coord_df = county_outline['geometry'].get_coordinates()

# specifically extract x (longitude) and y (latitude) values
lon = coord_df['x'].values
lat = coord_df['y'].values

# define county outline based on basemap
base_map_flip = {
    'Light': 'black',
    'Dark': 'white'
}

# create the county outline
scatter_trace = go.Scattermapbox(
    mode='lines',
    lon=lon,
    lat=lat,
    line=dict(
        width=4, 
        color=base_map_flip[base_map]
        ),
    hoverinfo='none'  
)

# add the county outline to choropleth
fig.add_trace(scatter_trace)

# hide modebar
config = {'displayModeBar': False}

# define columns
col1, col2 = st.columns([0.8,1])

# draw map
col1.plotly_chart(
    fig, 
    config=config,
    theme='streamlit',
    use_container_width=True
    )

# BUILDING PERMITS SECTION ---------------------------------------------------------
building_permits = pd.read_csv(
    'Data/building_permits.csv',
    dtype={
        'FIPS':'str'
    })

# filter permit data by county that is selected
county_fips = str(county_outline.index[0])
building_permits = building_permits[building_permits['FIPS'] == county_fips]

# spacer
col2.write(" ")

# Create the line chart
fig_permits = px.line(
    building_permits,
    x='date',
    y='Permits',
    color='Series',
    labels={'Permits': 'Total Permits', 'Series': 'Permit Type'},
    custom_data=['month_year', 'Series', 'Permits'],
    title='Building Permits by Month',
    height=230
)

fig_permits.update_traces(
    mode="markers+lines", 
    hovertemplate=
        "<b>%{customdata[0]}</b><br>"+
        "%{customdata[2]:,}"+
        "<extra></extra>"
)

fig_permits.update_xaxes(title=None)
fig_permits.update_yaxes(tickformat=',',title=None)
fig_permits.update_layout(
    margin=dict(l=10, r=10, t=50, b=1),
)

# draw building permit line chart
col2.plotly_chart(
    fig_permits, 
    config=config,
    theme='streamlit',
    use_container_width=True
    )

# create KPI variables
permit_12mo_total = building_permits[(building_permits['Series']=='Single-Family Units') & (building_permits['date']>='2023-06-01')]['Permits'].sum()

KPI_margin_top = 2
KPI_margin_bottom = 0
KPI_label_font_size = 12
KPI_value_font_size = 15

col2.markdown(
    f"""
    <div style='margin-top: {KPI_margin_top}px; margin-bottom: {KPI_margin_bottom}px;'>
        <span style='font-size: {KPI_label_font_size}px; font-weight: 200;'>Total 12-month SF Permits:</span><br>
        <span style='font-size: {KPI_value_font_size}px; font-weight: 800;'>{permit_12mo_total:,.0f}</span>
    </div>
    """,
    unsafe_allow_html=True
)

col2.divider()

# the custom CSS lives here:
hide_default_format = """
        <style>
            .reportview-container .main footer {visibility: hidden;}    
            #MainMenu, footer {visibility: hidden;}
            section.main > div:has(~ footer ) {
                padding-bottom: 1px;
                padding-left: 20px;
                padding-right: 20px;
                padding-top: 30px;
            }
            .stRadio [role=radiogroup]{
                align-items: center;
                justify-content: center;
            }
            [data-testid="stSidebar"] {
                padding-left: 10px;
                padding-right: 10px;
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
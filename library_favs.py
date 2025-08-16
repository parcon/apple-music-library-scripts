import dash
from dash import dcc, html, dash_table
import plotly.express as px
import pandas as pd
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime

# --- Data Processing Functions ---

def parse_itunes_xml(xml_file):
    """
    Parses the iTunes XML library file to extract track information.

    Args:
        xml_file (str): The path to the iTunes XML library file.

    Returns:
        pandas.DataFrame: A DataFrame containing track data with columns 
                          ['Album', 'Artist', 'Release Date', 'Play Count'].
    """
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Error parsing XML file: {e}")
        return pd.DataFrame() # Return empty DataFrame on error
    except FileNotFoundError:
        print(f"Error: The file '{xml_file}' was not found.")
        return pd.DataFrame()

    # The track data is nested in a structure like: dict -> key (Tracks) -> dict
    tracks_dict = root.find('dict/dict')
    if tracks_dict is None:
        return pd.DataFrame()

    all_tracks = []
    # Iterate through each track's dictionary
    for track_dict in tracks_dict.findall('dict'):
        track_info = {}
        # Keys and values are siblings, so we iterate through all elements
        key = None
        for elem in track_dict:
            if elem.tag == 'key':
                key = elem.text
            else:
                # Extract Album, Artist, Release Date, and Play Count
                if key in ['Album', 'Artist', 'Release Date', 'Play Count']:
                    if key == 'Play Count':
                        # Convert play count to integer
                        track_info[key] = int(elem.text) if elem.text is not None else 0
                    else:
                        track_info[key] = elem.text if elem.text is not None else ''
                key = None # Reset key after finding its value
        
        # Add default values if they are not present for a track
        if 'Play Count' not in track_info:
            track_info['Play Count'] = 0
        if 'Artist' not in track_info:
            track_info['Artist'] = 'Unknown Artist'
            
        # Only add tracks that have album and release date information
        if 'Album' in track_info and 'Release Date' in track_info:
            all_tracks.append(track_info)

    df = pd.DataFrame(all_tracks)
    
    # --- Data Cleaning ---
    if 'Release Date' in df.columns:
        # Convert 'Release Date' to datetime objects, coercing errors to NaT
        df['Release Date'] = pd.to_datetime(df['Release Date'], errors='coerce')
        # Drop rows where the date could not be parsed
        df.dropna(subset=['Release Date'], inplace=True)
        # Extract the year for easy filtering and grouping
        df['Year'] = df['Release Date'].dt.year
    else:
        # If no release dates were found, add an empty 'Year' column
        df['Year'] = None

    return df

# --- Main Script ---

# Load and process the data from your library file
# Ensure 'AugLibrary.xml' is in the same directory as this script
df = parse_itunes_xml('AugLibrary.xml')

# 1. Prepare data for the Album Releases by Year graph
if not df.empty and 'Year' in df.columns and 'Album' in df.columns:
    # Group by year and count the number of *unique* albums
    albums_by_year = df.groupby('Year')['Album'].nunique().reset_index()
    albums_by_year.columns = ['Year', 'Album Count']
else:
    albums_by_year = pd.DataFrame({'Year': [], 'Album Count': []})


# 2. Prepare data for the Top Albums of the Current Year table
current_year = datetime.now().year
if not df.empty and 'Release Date' in df.columns and 'Play Count' in df.columns:
    df_current_year = df[df['Release Date'].dt.year == current_year].copy()
    
    if not df_current_year.empty:
        # Extract month name for grouping
        df_current_year['Month'] = df_current_year['Release Date'].dt.strftime('%B')
        
        # Define the order of months for correct sorting
        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                       'July', 'August', 'September', 'October', 'November', 'December']
        df_current_year['Month'] = pd.Categorical(df_current_year['Month'], categories=month_order, ordered=True)

        # Find the top 5 albums for each month based on total play count
        top_albums_data = []
        for month, group in df_current_year.groupby('Month'):
            if not group.empty:
                # Group by album and artist, then sum the play counts
                album_play_counts = group.groupby(['Album', 'Artist'])['Play Count'].sum().reset_index()
                
                # Get the top 5 albums with the highest play counts
                top_5_albums = album_play_counts.nlargest(5, 'Play Count')
                
                for rank, (_, row) in enumerate(top_5_albums.iterrows(), 1):
                    top_albums_data.append({
                        'Month': month,
                        'Rank': rank,
                        'Artist': row['Artist'],
                        'Album': row['Album'], 
                        'Total Plays': row['Play Count']
                    })
        
        top_albums_df = pd.DataFrame(top_albums_data)
    else:
        top_albums_df = pd.DataFrame({'Month': [], 'Rank': [], 'Artist': [], 'Album': [], 'Total Plays': []})
else:
    top_albums_df = pd.DataFrame({'Month': [], 'Rank': [], 'Artist': [], 'Album': [], 'Total Plays': []})


# --- Dash App Layout ---

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Music Library Analysis"

# Create the bar chart figure
fig = px.bar(
    albums_by_year, 
    x='Year', 
    y='Album Count',
    title='Album Releases by Year',
    labels={'Year': 'Release Year', 'Album Count': 'Number of Unique Albums'},
    template='plotly_dark'
)
fig.update_layout(
    xaxis_title="Release Year",
    yaxis_title="Number of Unique Albums",
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='white')
)

# Define the layout of the web application
app.layout = html.Div(style={'backgroundColor': '#1a1a1a', 'color': '#e0e0e0', 'fontFamily': 'sans-serif', 'padding': '20px'}, children=[
    html.H1(
        children='My Music Library Dashboard',
        style={'textAlign': 'center', 'marginBottom': '30px'}
    ),

    html.Div(className='graph-container', children=[
        html.H2('Total Album Releases by Year', style={'textAlign': 'center'}),
        dcc.Graph(
            id='albums-by-year-graph',
            figure=fig
        )
    ]),

    html.Div(className='table-container', style={'marginTop': '50px'}, children=[
        html.H2(f'Top 5 Albums of {current_year} (by Total Plays)', style={'textAlign': 'center'}),
        dash_table.DataTable(
            id='top-albums-table',
            columns=[{"name": i, "id": i} for i in top_albums_df.columns],
            data=top_albums_df.to_dict('records'),
            style_cell={'textAlign': 'left', 'backgroundColor': '#333', 'color': 'white', 'border': '1px solid #444', 'padding': '10px'},
            style_header={
                'backgroundColor': '#444',
                'fontWeight': 'bold',
                'border': '1px solid #555'
            },
            style_table={'borderRadius': '8px', 'overflow': 'hidden'},
            # Conditional styling to add a top border for each new month
            style_data_conditional=[
                {
                    'if': {
                        'filter_query': '{Rank} = 1',
                    },
                    'borderTop': '2px solid #777'
                }
            ]
        )
    ])
])

# --- Run the App ---
if __name__ == '__main__':
    # To run this, you'll need to install dash, pandas, and plotly:
    # pip install dash pandas plotly
    app.run(debug=True)

import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection
import sys

st.set_page_config(
    page_title="Beacon Data Visualization",
    page_icon="📊",
    layout="wide"
)

# Create a connection to the Google Sheet
conn = st.connection("gsheets", type=GSheetsConnection)

df = None

# Read the data (only columns A through M)
@st.cache_data(ttl=600)  # Cache data for 10 minutes
def load_data():
    sheet_data = conn.read(
        worksheet="Beacon Tracker - AAK625",  # Assuming the data is in the first worksheet
        usecols=list(range(13)),  # Use columns A through M (0-12)
        ttl=600
    )
    return sheet_data

# Load the data
try:
    df = load_data()
except Exception as e:
    st.error(f"Error connecting to Google Sheet: {e}")
    st.stop()

# Display app title and description
st.title("Beacon Data Visualization")
st.write("This app visualizes data from the Google Sheet.")

# Process the Time Log column to calculate statistics
def convert_time_to_seconds(time_str):
    if pd.isna(time_str) or time_str == "":
        return None
    try:
        parts = time_str.split(':')
        if len(parts) == 2:
            minutes, seconds = map(float, parts)
            return minutes * 60 + seconds
        else:
            return None
    except:
        return None

def format_seconds_to_time(seconds):
    if pd.isna(seconds):
        return "N/A"
    minutes = int(seconds // 60)
    remaining_seconds = round(seconds % 60, 1)
    return f"{minutes}:{remaining_seconds:04.1f}"

# Sidebar for visualization options
st.sidebar.title("Visualization Options")

# Multiselect that allows filtering by one or more Version values
all_versions = df["Version"].dropna().unique().tolist()
selected_versions = st.sidebar.multiselect(
    "Version(s)", options=all_versions, default=all_versions
)

# Apply the filter if versions are selected
filtered_df = df.copy()
if selected_versions:
    filtered_df = filtered_df[filtered_df["Version"].isin(selected_versions)]

# Convert Time Log to seconds for calculations
filtered_df['Time_Log_Seconds'] = filtered_df['Time Log'].apply(convert_time_to_seconds)

if filtered_df.empty or not 'Time_Log_Seconds' in filtered_df.columns:
    st.stop()

# Calculate statistics
time_stats = {}
if not filtered_df.empty and 'Time_Log_Seconds' in filtered_df.columns:
    valid_times = filtered_df['Time_Log_Seconds'].dropna()
    if not valid_times.empty:
        time_stats = {
            "Average": valid_times.mean(),
            "Median": valid_times.median(),
            "Std Dev": valid_times.std(),
            "Min": valid_times.min(),
            "Max": valid_times.max()
        }

# Display statistics in columns with a nice format
st.subheader("Time Log Statistics")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="Average",
        value=format_seconds_to_time(time_stats.get("Average"))
    )

with col2:
    st.metric(
        label="Median",
        value=format_seconds_to_time(time_stats.get("Median"))
    )
    
with col3:
    st.metric(
        label="Std Dev",
        value=format_seconds_to_time(time_stats.get("Std Dev"))
    )
    
with col4:
    st.metric(
        label="Min",
        value=format_seconds_to_time(time_stats.get("Min"))
    )
    
with col5:
    st.metric(
        label="Max",
        value=format_seconds_to_time(time_stats.get("Max"))
    )

# Show the Time Log distribution histogram
time_log_values = filtered_df['Time_Log_Seconds'].dropna()
if not time_log_values.empty:
    import plotly.express as px
    import numpy as np
    # Compute histogram bin edges
    nbins = 50
    counts, bin_edges = np.histogram(time_log_values, bins=nbins)
    # Format bin edges as mm:ss
    def sec_to_mmss(sec):
        m = int(sec // 60)
        s = int(sec % 60)
        return f"{m}:{s:02d}"
    tickvals = [(bin_edges[i] + bin_edges[i+1]) / 2 for i in range(len(bin_edges)-1)]
    ticktext = [sec_to_mmss(edge) for edge in bin_edges]
    fig = px.histogram(
        x=time_log_values,
        nbins=nbins,
        labels={"x": "Time Log (mm:ss)", "y": "Count"},
        title="Distribution",
        color_discrete_sequence=["#4e79a7"]
    )
    fig.update_layout(
        bargap=0.05, title_x=0.5,
        xaxis = dict(
            tickmode = 'array',
            tickvals = bin_edges[::max(1, len(bin_edges)//10)],
            ticktext = [sec_to_mmss(edge) for edge in bin_edges][::max(1, len(bin_edges)//10)]
        )
    )
    st.plotly_chart(fig, use_container_width=True)


# Visualization section
st.subheader("Data Visualizations")

# Show summary charts for key categorical columns
chart_columns = [
    ("Beacon Type", "Percent by Beacon Type"),
    ("Bug?", "Bug?"),
    ("AI/PVP?", "Harmed by AI/PVP/Other"),
    ("Was a Trap?", "Beacon Trap?"),
    ("Mission", "Mission Type"),
    ("Location", "Location Distribution")
]

# Set up columns for the charts
chart_cols = st.columns(len(chart_columns))

for idx, (col_name, chart_title) in enumerate(chart_columns):
    if not filtered_df.empty and col_name in filtered_df.columns:
        value_counts = filtered_df[col_name].dropna().value_counts()
        if len(value_counts) > 8:
            # Use horizontal bar chart for Location if too many unique values
            fig = px.bar(
                x=value_counts.values,
                y=value_counts.index,
                orientation='h',
                title=chart_title,
                labels={"x": "Count", "y": col_name}
            )
        else:
            fig = px.pie(
                names=value_counts.index,
                values=value_counts.values,
                title=chart_title,
                hole=0.3
            )
        chart_cols[idx].plotly_chart(fig, use_container_width=True)


# --- Data Table Section ---

# Columns to hide from the bottom dataframe
cols_to_hide = ["index", "calculate?", "Time_Log_Seconds"]
visible_cols = [col for col in filtered_df.columns if col not in cols_to_hide]

# Search box
search_query = st.text_input("Search table:", "")

# Filter the dataframe by search query (case-insensitive, any visible column)
table_df = filtered_df[visible_cols].copy()
if search_query:
    mask = table_df.apply(lambda row: row.astype(str).str.contains(search_query, case=False, na=False).any(), axis=1)
    table_df = table_df[mask]

# Display the filtered dataframe with hidden index
st.dataframe(table_df, hide_index=True)

# Footer
st.markdown("---")
st.markdown("Data source: [Google Sheet](https://docs.google.com/spreadsheets/d/1aZvvNwm5l0HoqTFY5XFnXMVnfog_1DXdwySpsmcNc4w/edit)")

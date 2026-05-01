import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# Page configuration
st.set_page_config(
    page_title="Global Internet Usage Dashboard",
    page_icon="🌐",
    layout="wide"
)

# Sidebar styling
st.markdown("""
<style>
section[data-testid="stSidebar"] {
    background-color: #0f172a;
}

/* Improve tab readability */
button[data-baseweb="tab"] {
    font-size: 15px;
    color: #e5e7eb;
    background-color: rgba(15, 23, 42, 0.6);
    border-radius: 6px;
    padding: 6px;
}

button[aria-selected="true"] {
    color: #ffffff !important;
    border-bottom: 3px solid #3b82f6 !important;
    background-color: rgba(15, 23, 42, 0.9);
}

/* Dark overlay for background */
.stApp::before {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.45);
    z-index: -1;
}
</style>
""", unsafe_allow_html=True)

# Set background image
def set_background(image_path):
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-attachment: fixed;
    }}
    </style>
    """, unsafe_allow_html=True)

set_background("background.jpg")

# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv("data/processed/cleaned_data.csv")

df = load_data()

# Apply dark theme to charts
def apply_dark_theme(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        font=dict(color="white")
    )
    return fig

# Sidebar filters
st.sidebar.markdown("## 🔎 Filters")

min_year = int(df["Year"].min())
max_year = int(df["Year"].max())

year_range = st.sidebar.slider(
    "Year Range",
    min_year,
    max_year,
    (min_year, max_year)
)

country_list = sorted(df["Country"].unique())
selected_country = st.sidebar.multiselect(
    "Country",
    ["All"] + country_list,
    default=["All"]
)

region_list = sorted(df["Region"].dropna().unique())
selected_region = st.sidebar.multiselect(
    "Region",
    ["All"] + region_list,
    default=["All"]
)

income_list = sorted(df["IncomeGroup"].dropna().unique())
selected_income = st.sidebar.multiselect(
    "Income Group",
    ["All"] + income_list,
    default=["All"]
)

# Apply filtering
filtered_df = df.copy()

filtered_df = filtered_df[
    (filtered_df["Year"] >= year_range[0]) &
    (filtered_df["Year"] <= year_range[1])
]

if "All" not in selected_country:
    filtered_df = filtered_df[filtered_df["Country"].isin(selected_country)]

if "All" not in selected_region:
    filtered_df = filtered_df[filtered_df["Region"].isin(selected_region)]

if "All" not in selected_income:
    filtered_df = filtered_df[filtered_df["IncomeGroup"].isin(selected_income)]

# Handle empty data
if filtered_df.empty:
    st.warning("⚠️ No data available for selected filters.")
    st.stop()

# Title
st.markdown(f"""
# 🌐 Global Internet Usage Dashboard ({year_range[0]} - {year_range[1]})
Explore internet usage across countries, regions, and income groups.
""")

# KPI section
col1, col2, col3 = st.columns(3)

avg_usage = filtered_df["Internet_Users_Percent"].mean()
top_country = filtered_df.loc[
    filtered_df["Internet_Users_Percent"].idxmax(), "Country"
]
low_country = filtered_df.loc[
    filtered_df["Internet_Users_Percent"].idxmin(), "Country"
]

col1.metric("🌍 Avg Usage (%)", f"{avg_usage:.2f}")
col2.metric("🏆 Top Country", top_country)
col3.metric("📉 Lowest Country", low_country)

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Global Trends",
    "🌍 Regional Comparison",
    "💰 Income Comparison",
    "🔎 Country Analysis",
    "🗺️ World Map",
    "📋 Data View"
])

# Global trend
with tab1:
    st.subheader("📈 Global Internet Usage Over Time")

    trend = filtered_df.groupby("Year")["Internet_Users_Percent"].mean().reset_index()

    fig = px.line(trend, x="Year", y="Internet_Users_Percent", markers=True)
    fig.update_traces(
        hovertemplate="<b>Year:</b> %{x}<br><b>Usage:</b> %{y:.2f}%<extra></extra>"
    )
    fig = apply_dark_theme(fig)
    st.plotly_chart(fig, use_container_width=True)

    st.info(
        f"Internet usage increased from {trend['Internet_Users_Percent'].min():.1f}% "
        f"to {trend['Internet_Users_Percent'].max():.1f}%."
    )

# Region comparison
with tab2:
    st.subheader("🌍 Average Internet Usage by Region")

    region_df = filtered_df.groupby("Region")["Internet_Users_Percent"].mean().reset_index()
    region_df = region_df.sort_values("Internet_Users_Percent", ascending=False)

    fig = px.bar(region_df, x="Region", y="Internet_Users_Percent", color="Region")
    fig.update_traces(
        hovertemplate="<b>Region:</b> %{x}<br><b>Usage:</b> %{y:.2f}%<extra></extra>"
    )
    fig = apply_dark_theme(fig)
    st.plotly_chart(fig, use_container_width=True)

# Income comparison
with tab3:
    st.subheader("💰 Internet Usage by Income Group")

    income_df = filtered_df.groupby("IncomeGroup")["Internet_Users_Percent"].mean().reset_index()
    income_df = income_df.sort_values("Internet_Users_Percent", ascending=False)

    fig = px.bar(income_df, x="IncomeGroup", y="Internet_Users_Percent", color="IncomeGroup")
    fig.update_traces(
        hovertemplate="<b>Group:</b> %{x}<br><b>Usage:</b> %{y:.2f}%<extra></extra>"
    )
    fig = apply_dark_theme(fig)
    st.plotly_chart(fig, use_container_width=True)

# Country comparison (FIXED)
with tab4:
    st.subheader("🔎 Compare Countries")

    selected_compare = st.multiselect(
        "Select up to 5 countries",
        country_list
    )

    if len(selected_compare) == 0:
        st.info("Please select up to 5 countries to compare.")
    elif len(selected_compare) > 5:
        st.warning("Maximum 5 countries allowed.")
    else:
        compare_df = filtered_df[filtered_df["Country"].isin(selected_compare)]

        fig = px.line(compare_df, x="Year", y="Internet_Users_Percent", color="Country", markers=True)
        fig = apply_dark_theme(fig)
        st.plotly_chart(fig, use_container_width=True)

# World map
# World map
with tab5:
    st.subheader("🗺️ Global Internet Usage Map")

    map_df = filtered_df.sort_values("Year").groupby("Code").tail(1)

    fig = px.choropleth(
        map_df,
        locations="Code",
        color="Internet_Users_Percent",
        hover_name="Country",
        color_continuous_scale="Viridis"
    )

    fig.update_geos(
        bgcolor="#0e1117",
        landcolor="#1f2a38",
        showcountries=True,
        countrycolor="gray",
        projection_type="natural earth"
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0)
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "staticPlot": True   # BEST OPTION
        }
    )

    st.caption("Map shows latest available data for each country.")

# Data view
with tab6:
    st.subheader("📋 Filtered Dataset")

    st.dataframe(filtered_df.head(200), use_container_width=True)

    st.download_button(
        "⬇️ Download CSV",
        filtered_df.to_csv(index=False),
        "filtered_data.csv"
    )

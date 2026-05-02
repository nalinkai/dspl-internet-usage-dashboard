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


# Plotly configuration (remove unnecessary toolbar buttons)
PLOT_CONFIG = {
    "displaylogo": False,
    "modeBarButtonsToRemove": [
        "zoom", "pan", "zoomIn", "zoomOut",
        "autoScale", "resetScale2d", "lasso2d", "select2d"
    ],
    "modeBarButtonsToAdd": ["toImage"],
    "displayModeBar": True
}


# Apply UI styling
st.markdown("""
<style>

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: #0f172a;
}

/* Page spacing */
.block-container {
    padding-top: 2rem;
}

/* Sticky header */
h1 {
    position: sticky;
    top: 0;
    background: rgba(0,0,0,0.7);
    padding: 10px;
    z-index: 999;
}

/* Tabs styling */
button[data-baseweb="tab"] {
    background-color: rgba(15, 23, 42, 0.8);
    border-radius: 10px;
}

/* Footer styling */
.footer {
    text-align: center;
    padding: 15px;
    background-color: rgba(0,0,0,0.6);
    margin-top: 30px;
    border-radius: 10px;
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

year_range = st.sidebar.slider(
    "Year Range",
    int(df["Year"].min()),
    int(df["Year"].max()),
    (1990, 2025)
)

selected_country = st.sidebar.multiselect(
    "Country",
    ["All"] + sorted(df["Country"].unique()),
    default=["All"]
)

selected_region = st.sidebar.multiselect(
    "Region",
    ["All"] + sorted(df["Region"].dropna().unique()),
    default=["All"]
)

selected_income = st.sidebar.multiselect(
    "Income Group",
    ["All"] + sorted(df["IncomeGroup"].dropna().unique()),
    default=["All"]
)


# Apply filtering
filtered_df = df[
    (df["Year"] >= year_range[0]) &
    (df["Year"] <= year_range[1])
]

if "All" not in selected_country:
    filtered_df = filtered_df[filtered_df["Country"].isin(selected_country)]

if "All" not in selected_region:
    filtered_df = filtered_df[filtered_df["Region"].isin(selected_region)]

if "All" not in selected_income:
    filtered_df = filtered_df[filtered_df["IncomeGroup"].isin(selected_income)]


# Handle empty dataset
if filtered_df.empty:
    st.warning("No data available for selected filters.")
    st.stop()


# Dashboard title
st.markdown(f"# 🌐 Global Internet Usage Dashboard ({year_range[0]} - {year_range[1]})")
st.write("Explore internet usage across countries, regions, and income groups.")


# KPI metrics
col1, col2, col3 = st.columns(3)

col1.metric("🌍 Avg Usage (%)", f"{filtered_df['Internet_Users_Percent'].mean():.2f}")
col2.metric("🏆 Top Country", filtered_df.loc[filtered_df['Internet_Users_Percent'].idxmax(), 'Country'])
col3.metric("📉 Lowest Country", filtered_df.loc[filtered_df['Internet_Users_Percent'].idxmin(), 'Country'])


# Create tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Global Trends",
    "🌍 Regional Analysis",
    "💰 Income Analysis",
    "🔎 Country Analysis",
    "🗺️ World Map",
    "📋 Data View"
])


# Global trends
with tab1:
    trend = filtered_df.groupby("Year")["Internet_Users_Percent"].mean().reset_index()

    fig = px.line(trend, x="Year", y="Internet_Users_Percent", markers=True)
    st.plotly_chart(apply_dark_theme(fig), use_container_width=True, config=PLOT_CONFIG)


# Regional analysis + drill-down
with tab2:
    region_df = filtered_df.groupby("Region")["Internet_Users_Percent"].mean().reset_index()

    fig = px.bar(region_df, x="Region", y="Internet_Users_Percent", color="Region")
    st.plotly_chart(apply_dark_theme(fig), use_container_width=True, config=PLOT_CONFIG)

    selected_drill_region = st.selectbox("Select region for drill-down", region_df["Region"])

    drill_df = filtered_df[filtered_df["Region"] == selected_drill_region]
    top_countries = drill_df.groupby("Country")["Internet_Users_Percent"].mean().nlargest(10).reset_index()

    fig = px.bar(top_countries, x="Country", y="Internet_Users_Percent")
    st.plotly_chart(apply_dark_theme(fig), use_container_width=True, config=PLOT_CONFIG)


# Income analysis
with tab3:
    income_df = filtered_df.groupby("IncomeGroup")["Internet_Users_Percent"].mean().reset_index()

    fig = px.bar(income_df, x="IncomeGroup", y="Internet_Users_Percent", color="IncomeGroup")
    st.plotly_chart(apply_dark_theme(fig), use_container_width=True, config=PLOT_CONFIG)


# Country comparison
with tab4:
    selected_compare = st.multiselect("Select up to 5 countries", sorted(df["Country"].unique()))

    if len(selected_compare) == 0:
        st.info("Please select countries.")
    elif len(selected_compare) > 5:
        st.warning("Maximum 5 countries allowed.")
    else:
        compare_df = filtered_df[filtered_df["Country"].isin(selected_compare)]

        fig = px.line(compare_df, x="Year", y="Internet_Users_Percent", color="Country")
        st.plotly_chart(apply_dark_theme(fig), use_container_width=True, config=PLOT_CONFIG)


# World map visualization
with tab5:
    map_df = filtered_df.sort_values("Year").groupby("Code").tail(1)

    fig = px.choropleth(
        map_df,
        locations="Code",
        color="Internet_Users_Percent",
        hover_name="Country",
        projection="natural earth"
    )

    fig.update_geos(fitbounds="locations", visible=False)

    st.plotly_chart(
        apply_dark_theme(fig),
        use_container_width=True,
        config={
            "displaylogo": False,
            "scrollZoom": False,
            "modeBarButtonsToAdd": ["toImage"]
        }
    )


# Data table view
with tab6:
    st.dataframe(filtered_df.head(200), use_container_width=True)

    st.download_button(
        "Download CSV",
        filtered_df.to_csv(index=False),
        "filtered_data.csv"
    )


# Footer
st.markdown("""
<div class='footer'>
Project By: w2055140 Nalinka Iluppalla | DSPL Coursework
</div>
""", unsafe_allow_html=True)

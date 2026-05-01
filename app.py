import streamlit as st
import pandas as pd
import plotly.express as px

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
</style>
""", unsafe_allow_html=True)

# Background image setup
def set_background(image_path):
    import base64
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


# Apply consistent dark theme to charts
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


# Filtering logic
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


# Handle empty results
if filtered_df.empty:
    st.warning("⚠️ No data found. Try adjusting filters such as year range or region.")
    st.stop()


# Dashboard title
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
    fig = apply_dark_theme(fig)
    st.plotly_chart(fig, use_container_width=True)

    st.info(
        f"Internet usage increased from {trend['Internet_Users_Percent'].min():.1f}% "
        f"to {trend['Internet_Users_Percent'].max():.1f}% over the selected period."
    )


# Region comparison
with tab2:
    st.subheader("🌍 Average Internet Usage by Region")

    region_df = filtered_df.groupby("Region")["Internet_Users_Percent"].mean().reset_index()
    region_df = region_df.sort_values("Internet_Users_Percent", ascending=False)

    fig = px.bar(region_df, x="Region", y="Internet_Users_Percent", color="Region")
    fig = apply_dark_theme(fig)
    st.plotly_chart(fig, use_container_width=True)

    top_region = region_df.iloc[0]
    st.info(f"Highest usage region: {top_region['Region']} ({top_region['Internet_Users_Percent']:.1f}%)")


# Income comparison
with tab3:
    st.subheader("💰 Internet Usage by Income Group")

    income_df = filtered_df.groupby("IncomeGroup")["Internet_Users_Percent"].mean().reset_index()
    income_df = income_df.sort_values("Internet_Users_Percent", ascending=False)

    fig = px.bar(income_df, x="IncomeGroup", y="Internet_Users_Percent", color="IncomeGroup")
    fig = apply_dark_theme(fig)
    st.plotly_chart(fig, use_container_width=True)

    top_income = income_df.iloc[0]
    st.info(f"{top_income['IncomeGroup']} countries show the highest usage ({top_income['Internet_Users_Percent']:.1f}%)")


# Country comparison
with tab4:
    st.subheader("🔎 Compare Countries")

    selected_compare = st.multiselect(
        "Select Countries to Compare",
        ["All"] + country_list,
        default=["All"]
    )

    if "All" in selected_compare:
        top5 = (
            filtered_df.sort_values("Internet_Users_Percent", ascending=False)
            .groupby("Country")
            .tail(1)
            .nlargest(5, "Internet_Users_Percent")["Country"]
        )
        compare_df = filtered_df[filtered_df["Country"].isin(top5)]
    else:
        if len(selected_compare) > 5:
            st.warning("Select up to 5 countries for better comparison.")
            st.stop()
        compare_df = filtered_df[filtered_df["Country"].isin(selected_compare)]

    fig = px.line(compare_df, x="Year", y="Internet_Users_Percent", color="Country")
    fig = apply_dark_theme(fig)
    st.plotly_chart(fig, use_container_width=True)

    st.info("Tip: Select up to 5 countries for a clearer comparison.")


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
        countrycolor="gray"
    )

    st.plotly_chart(fig, use_container_width=True)

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

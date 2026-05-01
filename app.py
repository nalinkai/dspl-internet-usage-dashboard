import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="Global Internet Usage Dashboard",
    page_icon="🌐",
    layout="wide"
)

# ------------------ PLOT CONFIG ------------------
PLOT_CONFIG = {
    "displayModeBar": True,
    "displaylogo": False,
    "modeBarButtonsToRemove": [
        "zoom",
        "pan",
        "select",
        "lasso",
        "zoomIn",
        "zoomOut",
        "autoScale",
        "resetScale",
        "hoverClosestCartesian",
        "hoverCompareCartesian",
        "toggleSpikelines"
    ]
}

# ------------------ STYLING ------------------
st.markdown("""
<style>
section[data-testid="stSidebar"] {
    background-color: #0f172a;
}

/* Tabs */
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

/* Overlay FIXED */
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.45);
    pointer-events: none;
}
</style>
""", unsafe_allow_html=True)

# ------------------ BACKGROUND ------------------
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

# ------------------ LOAD DATA ------------------
@st.cache_data
def load_data():
    return pd.read_csv("data/processed/cleaned_data.csv")

df = load_data()

# ------------------ THEME ------------------
def apply_dark_theme(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        font=dict(color="white")
    )
    return fig

# ------------------ FILTERS ------------------
st.sidebar.markdown("## 🔎 Filters")

year_range = st.sidebar.slider(
    "Year Range",
    int(df["Year"].min()),
    int(df["Year"].max()),
    (int(df["Year"].min()), int(df["Year"].max()))
)

country_list = sorted(df["Country"].unique())
selected_country = st.sidebar.multiselect("Country", ["All"] + country_list, default=["All"])

region_list = sorted(df["Region"].dropna().unique())
selected_region = st.sidebar.multiselect("Region", ["All"] + region_list, default=["All"])

income_list = sorted(df["IncomeGroup"].dropna().unique())
selected_income = st.sidebar.multiselect("Income Group", ["All"] + income_list, default=["All"])

# ------------------ FILTER LOGIC ------------------
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

if filtered_df.empty:
    st.warning("⚠️ No data available for selected filters.")
    st.stop()

# ------------------ TITLE ------------------
st.markdown(f"""
# 🌐 Global Internet Usage Dashboard ({year_range[0]} - {year_range[1]})
Explore internet usage across countries, regions, and income groups.
""")

# ------------------ KPI ------------------
col1, col2, col3 = st.columns(3)

col1.metric("🌍 Avg Usage (%)", f"{filtered_df['Internet_Users_Percent'].mean():.2f}")
col2.metric("🏆 Top Country", filtered_df.loc[filtered_df["Internet_Users_Percent"].idxmax(), "Country"])
col3.metric("📉 Lowest Country", filtered_df.loc[filtered_df["Internet_Users_Percent"].idxmin(), "Country"])

st.markdown("---")

# ------------------ TABS ------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Global Trends",
    "🌍 Regional Comparison",
    "💰 Income Comparison",
    "🔎 Country Analysis",
    "🗺️ World Map",
    "📋 Data View"
])

# ------------------ GLOBAL TREND ------------------
with tab1:
    trend = filtered_df.groupby("Year")["Internet_Users_Percent"].mean().reset_index()

    fig = px.line(trend, x="Year", y="Internet_Users_Percent", markers=True)
    fig.update_traces(hovertemplate="Year: %{x}<br>Usage: %{y:.2f}%")
    st.plotly_chart(apply_dark_theme(fig), use_container_width=True, config=PLOT_CONFIG)

# ------------------ REGION ------------------
with tab2:
    region_df = filtered_df.groupby("Region")["Internet_Users_Percent"].mean().reset_index()

    fig = px.bar(region_df, x="Region", y="Internet_Users_Percent", color="Region")
    st.plotly_chart(apply_dark_theme(fig), use_container_width=True, config=PLOT_CONFIG)

    selected_region_drill = st.selectbox("🔍 Drill-down Region", region_df["Region"])

    drill_df = filtered_df[filtered_df["Region"] == selected_region_drill]

    top_countries = (
        drill_df.groupby("Country")["Internet_Users_Percent"]
        .mean().sort_values(ascending=False).head(10).reset_index()
    )

    fig2 = px.bar(top_countries, x="Country", y="Internet_Users_Percent")
    st.plotly_chart(apply_dark_theme(fig2), use_container_width=True, config=PLOT_CONFIG)

# ------------------ INCOME ------------------
with tab3:
    income_df = filtered_df.groupby("IncomeGroup")["Internet_Users_Percent"].mean().reset_index()

    fig = px.bar(income_df, x="IncomeGroup", y="Internet_Users_Percent", color="IncomeGroup")
    st.plotly_chart(apply_dark_theme(fig), use_container_width=True, config=PLOT_CONFIG)

# ------------------ COUNTRY ------------------
with tab4:
    selected_compare = st.multiselect("Select up to 5 countries", country_list)

    if len(selected_compare) == 0:
        st.info("Please select countries.")
    elif len(selected_compare) > 5:
        st.warning("Max 5 countries allowed.")
    else:
        compare_df = filtered_df[filtered_df["Country"].isin(selected_compare)]

        fig = px.line(compare_df, x="Year", y="Internet_Users_Percent",
                      color="Country", markers=True)

        st.plotly_chart(apply_dark_theme(fig), use_container_width=True, config=PLOT_CONFIG)

# ------------------ MAP ------------------
with tab5:
    map_df = filtered_df.sort_values("Year").groupby("Code").tail(1)

    fig = px.choropleth(
        map_df,
        locations="Code",
        color="Internet_Users_Percent",
        hover_name="Country",
        color_continuous_scale="Viridis"
    )

    fig.update_traces(hovertemplate="%{hovertext}<br>%{z:.2f}%")

    fig.update_layout(dragmode=False)

    fig.update_geos(
        projection_type="natural earth",
        showcountries=True,
        countrycolor="gray",
        showframe=False,
        bgcolor="#0e1117"
    )

    st.plotly_chart(fig, use_container_width=True, config=PLOT_CONFIG)

# ------------------ DATA ------------------
with tab6:
    st.dataframe(filtered_df.head(200), use_container_width=True)

    st.download_button(
        "⬇️ Download CSV",
        filtered_df.to_csv(index=False),
        "filtered_data.csv"
    )

# ------------------ FOOTER ------------------
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#cbd5e1;'>Project By: w2055140 Nalinka Iluppalla | DSPL Coursework</p>",
    unsafe_allow_html=True
)

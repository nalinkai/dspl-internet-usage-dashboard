import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# ---------------- Page setup ----------------
st.set_page_config(
    page_title="Global Internet Usage Dashboard",
    page_icon="🌐",
    layout="wide"
)

# ---------------- Theme toggle ----------------
mode = st.sidebar.radio("🎨 Theme Mode", ["Dark", "Light"], index=0)

if mode == "Dark":
    bg_overlay = "rgba(0,0,0,0.5)"
    text_color = "white"
else:
    bg_overlay = "rgba(255,255,255,0.7)"
    text_color = "black"

# ---------------- Background setup ----------------
def set_background(image_path):
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
        }}

        .stApp::before {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: {bg_overlay};
            z-index: -1;
        }}

        section[data-testid="stSidebar"] {{
            background-color: #0f172a;
        }}

        button[data-baseweb="tab"] {{
            font-size: 16px;
            color: #e5e7eb;
            background-color: rgba(15, 23, 42, 0.6);
            border-radius: 8px;
            padding: 8px;
        }}

        button[aria-selected="true"] {{
            color: #ffffff !important;
            border-bottom: 3px solid #3b82f6 !important;
            background-color: rgba(15, 23, 42, 0.9);
        }}

        </style>
    """, unsafe_allow_html=True)

set_background("background.jpg")

# ---------------- Load data ----------------
@st.cache_data
def load_data():
    return pd.read_csv("data/processed/cleaned_data.csv")

df = load_data()

# ---------------- Chart theme ----------------
def apply_theme(fig):
    fig.update_layout(
        template="plotly_dark" if mode == "Dark" else "plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=text_color)
    )
    return fig

# ---------------- Sidebar filters ----------------
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

# ---------------- Filtering ----------------
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

if filtered_df.empty:
    st.warning("⚠️ No data found. Try adjusting filters.")
    st.stop()

# ---------------- Title ----------------
st.markdown(f"""
# 🌐 Global Internet Usage Dashboard ({year_range[0]} - {year_range[1]})
Explore internet usage across countries, regions, and income groups.
""")

# ---------------- KPIs ----------------
col1, col2, col3 = st.columns(3)

col1.metric("🌍 Avg Usage (%)", f"{filtered_df['Internet_Users_Percent'].mean():.2f}")
col2.metric("🏆 Top Country",
            filtered_df.loc[filtered_df["Internet_Users_Percent"].idxmax(), "Country"])
col3.metric("📉 Lowest Country",
            filtered_df.loc[filtered_df["Internet_Users_Percent"].idxmin(), "Country"])

st.markdown("---")

# ---------------- Tabs ----------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Global Trends",
    "🌍 Regional Comparison",
    "💰 Income Comparison",
    "🔎 Country Analysis",
    "🗺️ World Map",
    "📋 Data View"
])

# ---------------- Global trends ----------------
with tab1:
    trend = filtered_df.groupby("Year")["Internet_Users_Percent"].mean().reset_index()

    fig = px.line(trend, x="Year", y="Internet_Users_Percent", markers=True)
    fig.update_traces(
        hovertemplate="<b>Year:</b> %{x}<br><b>Usage:</b> %{y:.2f}%"
    )
    st.plotly_chart(apply_theme(fig), use_container_width=True)

# ---------------- Region ----------------
with tab2:
    region_df = filtered_df.groupby("Region")["Internet_Users_Percent"].mean().reset_index()

    fig = px.bar(region_df, x="Region", y="Internet_Users_Percent", color="Region")
    fig.update_traces(
        hovertemplate="<b>Region:</b> %{x}<br><b>Usage:</b> %{y:.2f}%"
    )
    st.plotly_chart(apply_theme(fig), use_container_width=True)

# ---------------- Income ----------------
with tab3:
    income_df = filtered_df.groupby("IncomeGroup")["Internet_Users_Percent"].mean().reset_index()

    fig = px.bar(income_df, x="IncomeGroup", y="Internet_Users_Percent", color="IncomeGroup")
    st.plotly_chart(apply_theme(fig), use_container_width=True)

# ---------------- Country analysis ----------------
with tab4:
    st.markdown("### Select up to 5 countries")

    selected_compare = st.multiselect(
        "Choose countries",
        country_list
    )

    if len(selected_compare) == 0:
        st.info("Please select up to 5 countries to compare.")

    elif len(selected_compare) > 5:
        st.warning("Maximum 5 countries allowed.")

    else:
        compare_df = filtered_df[filtered_df["Country"].isin(selected_compare)]

        fig = px.line(compare_df, x="Year", y="Internet_Users_Percent", color="Country", markers=True)
        st.plotly_chart(apply_theme(fig), use_container_width=True)

# ---------------- Map ----------------
with tab5:
    map_df = filtered_df.sort_values("Year").groupby("Code").tail(1)

    fig = px.choropleth(
        map_df,
        locations="Code",
        color="Internet_Users_Percent",
        hover_name="Country",
        hover_data={"Internet_Users_Percent": True},
        color_continuous_scale="Viridis"
    )

    fig.update_geos(
        showcountries=True,
        countrycolor="gray"
    )

    st.plotly_chart(apply_theme(fig), use_container_width=True)

# ---------------- Data view ----------------
with tab6:
    st.dataframe(filtered_df.head(200), use_container_width=True)

    st.download_button(
        "⬇️ Download CSV",
        filtered_df.to_csv(index=False),
        "filtered_data.csv"
    )

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import calendar

st.set_page_config(page_title="US Stock Commodity Analyst", layout="wide", initial_sidebar_state="expanded")

st.sidebar.title("Menu Navigation")

df = pd.read_parquet(US_Stock_Data_Cleaned.csv)

norm_df = df.copy()

for col in norm_df.columns:
    first = norm_df[col].iloc[0]
    norm_df[col] = (norm_df[col] / first) * 100
    norm_df[col] = norm_df[col].rolling(window=14, min_periods=1).mean()

norm_df = norm_df.drop(norm_df.index[0], axis=0) 

corr_df = norm_df.corr()

if "page" not in st.session_state:
    st.session_state.page = "Overview"

if "selected_asset" not in st.session_state:
    st.session_state.selected_asset = norm_df.columns[0]

if "selected_year" not in st.session_state:
    st.session_state.selected_year = norm_df.index.year.unique()[0]

if "selected_catergory" not in st.session_state:
    st.session_state.selected_catergory = "Tech Stocks"

if "selected_indi_corr" not in st.session_state:
    st.session_state.selected_indi_corr = norm_df.columns[0]

if "selected_category_plot" not in st.session_state:
    st.session_state.selected_category_plot = "Tech Stocks"

if st.sidebar.button("Overview", use_container_width=True):
    st.session_state.page = "Overview"
if st.sidebar.button("Seasonal Analysis", use_container_width=True):
    st.session_state.page = "Seasonal Analysis"
if st.sidebar.button("Correlation Analysis", use_container_width=True):
    st.session_state.page = "Correlation Analysis"
if st.sidebar.button("Portofolio", use_container_width=True):
    st.session_state.page = "Portofolio"

page = st.session_state.page

if page == "Overview":
    st.title("Overview of US Market")
    from utils.function_overview_page import(
        create_data_overview_page
    )
    create_data_overview_page(df)

elif page == "Seasonal Analysis":
    st.title("Seasonal Analysis of US Market")

    asset = st.selectbox(
        "Select Asset", 
        norm_df.columns,
        index=list(norm_df.columns).index(st.session_state.selected_asset)
    )

    st.session_state.selected_asset = asset

    data = norm_df[asset]
    fig = px.line(data, x=data.index, y=norm_df[asset])
    
    with st.container():
        st.subheader(f"{asset.replace('_',' ')} Price Over Time 2020-2023")
        st.plotly_chart(fig, use_container_width=True)

        col1, col2, col3, col4, col5 = st.columns(5, border=True)

        with col1:
            st.metric("Open Price", f"{data.iloc[0]:.2f}", delta=None)
            st.write(data.index[0].strftime("%Y-%m-%d"))
        with col2:
            st.metric("Close Price", f"{data.iloc[-1]:.2f}", delta=None)
            st.write(data.index[-1].strftime("%Y-%m-%d"))
        with col3:
            st.metric("Max Price", f"{data.max():.2f}", delta=None)
            st.write(data.idxmax().strftime("%Y-%m-%d"))
        with col4:
            st.metric("Min Price", f"{data.min():.2f}", delta=None)
            st.write(data.idxmin().strftime("%Y-%m-%d"))
        with col5:
            st.metric("Average Price", f"{data.mean():.2f}", delta=None)

    st.markdown("---")
    st.container()
    from utils.function_seasonal_page import(
        tap_year_seasonal
    )
    with st.container():
        st.subheader(f"{asset.replace('_',' ')} Price per Year Seasonal Analysis")
        tahun = data.index.year.unique()

        selected_year = st.radio(
            "Select Year", 
            options=tahun, 
            horizontal=True,
            index=list(tahun).index(st.session_state.selected_year)
        )
        st.session_state.selected_year = selected_year
        tap_year_seasonal(data, selected_year)

elif page == "Correlation Analysis":
    st.title("Correlation Analysis of US Market")

    from utils.fungction_correlation_page import(
        main_correlation,
        correlation_summary,
        categori_correlation,
        single_correlation,
        price_line_plot,
        plot_custom_asset
    )

    st.subheader("Correlation Heatmap of US Market Assets")

    main_correlation(corr_df)

    st.markdown("---")

    asset_categories = {
    'Tech Stocks': ['Apple_Price', 'Tesla_Price', 'Microsoft_Price', 'Google_Price',
                   'Nvidia_Price', 'Netflix_Price', 'Amazon_Price', 'Meta_Price'],
    'Cryptocurrencies': ['Bitcoin_Price', 'Ethereum_Price'],
    'Commodities': ['Natural_Gas_Price', 'Crude_oil_Price', 'Copper_Price',
                   'Silver_Price', 'Gold_Price', 'Platinum_Price'],
    'Market Indices': ['S&P_500_Price', 'Nasdaq_100_Price', 'Berkshire_Price']    
    }

    st.subheader("Correlation Analysis of Categories of Assets")
    categories = st.selectbox(
        "Select Asset Category",
        options=list(asset_categories.keys()),
        index=list(asset_categories.keys()).index(st.session_state.selected_catergory),
        key="corr_categories"
    )

    asset_tect = asset_categories[categories]

    st.session_state.selected_catergory = categories
    available_tech = [asset for asset in asset_tect if asset in corr_df.columns]

    tech_corr = corr_df.loc[available_tech, available_tech]

    categori_correlation(categories, tech_corr, available_tech)

    st.markdown("---")
    st. title   ("Individual Asset Correlation Analysis")

    # Asset selection
    selected_asset = st.selectbox(
        "Select Asset for Analysis:",
        options=norm_df.columns,
        index=list(norm_df.columns).index(st.session_state.selected_indi_corr)
    )
    st.session_state.selected_indi_corr = selected_asset

    asset_correlations = norm_df.corr()[selected_asset].drop(selected_asset).sort_values(ascending=False)

    # Main layout
    st.subheader(f"{selected_asset.replace('_Price', '')} Correlation with All Assets")

    # Create heatmap for single asset
    single_correlation(asset_correlations, selected_asset)

    # Summary section
    st.markdown("---")
    st.subheader(f"Correlation Summary for {selected_asset.replace('_Price', '')}")

    # Create 4 columns for different correlation strengths
    correlation_summary(asset_correlations)

    st.title(f"{categories} Price Trends Over Time")
    categories = st.selectbox(
        "Select Asset Category",
        options=list(asset_categories.keys()),
        index=list(asset_categories.keys()).index(st.session_state.selected_category_plot),
        key="plot_categories"
    )

    st.session_state.selected_category_plot = categories
    selected_assets = asset_categories[categories]
    available_assets = [asset for asset in selected_assets if asset in norm_df.columns]
    category_data = norm_df[available_assets]

    st.subheader("Customize Assets Display")
    filtered_assets = st.multiselect(
    f"Select {categories} assets to display:",
    options=available_assets,
    default=available_assets,  # Default semua assets
    format_func=lambda x: x.replace('_Price', ''),
    key=f"filter_assets_{categories}"
    )
    
    if filtered_assets:
        category_data = norm_df[filtered_assets]
        price_line_plot(category_data, filtered_assets, categories, norm_df)

    else:
        st.warning(f"Please select at least one {categories} asset to display")

    st.title("Custom Asset Plot")

    selected_custom_assets = st.multiselect(
        "Select Assets to Plot:",
        options=norm_df.columns,
        default=norm_df.columns[:3],  # Default 3 asset pertama
        format_func=lambda x: x.replace('_Price', '')
    )

    if selected_custom_assets:
        plot_custom_asset(norm_df, selected_custom_assets)

    else:
        st.info("Please select at least one asset to plot")

elif page == "Portofolio":

    from utils.function_portofolio_page import(
        describe_portofolio,
        rank_asset_analisis,
        asset_performance,
        portofolio_custom
    )
    st.title("Portofolio Analysis of US Stock Market")

    st.subheader("Detailed Statistical Analysis")

    # Create comprehensive statistics table with all metrics
    describe_portofolio(df)

    st.subheader("Asset Performance Leaderboard")

    # Create leaderboard with ranking and grades
    rank_asset_analisis(df)

    st.subheader("Performance by Category")

    asset_performance(df)

    st.subheader("Portfolio Builder")

    portofolio_custom(df)

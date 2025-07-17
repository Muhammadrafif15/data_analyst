import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import calendar

st.set_page_config(page_title="US Stock Commodity Analyst", layout="wide", initial_sidebar_state="expanded")

st.sidebar.title("Menu Navigation")

df = pd.read_parquet('US_Stock_Data_Cleaned.csv')

norm_df = df.copy()

for col in norm_df.columns:
    first = norm_df[col].iloc[0]
    norm_df[col] = (norm_df[col] / first) * 100
    norm_df[col] = norm_df[col].rolling(window=14, min_periods=1).mean()

norm_df = norm_df.drop(norm_df.index[0], axis=0) 

if "page" not in st.session_state:
    st.session_state.page = "Overview"

if "selected_asset" not in st.session_state:
    st.session_state.selected_asset = norm_df.columns[0]

if "selected_year" not in st.session_state:
    st.session_state.selected_year = norm_df.index.year.unique()[0]

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
    st.title("Overview of US Stock Market")

elif page == "Seasonal Analysis":
    st.title("Seasonal Analysis of US Stock Market")

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
    st.title("Correlation Analysis of US Stock Market")

elif page == "Portofolio":
    st.title("Portofolio Analysis of US Stock Market")
        



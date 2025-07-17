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

corr_df = norm_df.corr()

if "page" not in st.session_state:
    st.session_state.page = "Overview"

if "selected_asset" not in st.session_state:
    st.session_state.selected_asset = norm_df.columns[0]

if "selected_year" not in st.session_state:
    st.session_state.selected_year = norm_df.index.year.unique()[0]

if "selected_catergory" not in st.session_state:
    st.session_state.selected_catergory = "Tech Stocks"

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

    st.subheader("Correlation Heatmap of US Market Assets")

    fig = go.Figure(data=go.Heatmap(
        z=corr_df.values,
        x=corr_df.columns,
        y=corr_df.columns,
        colorscale='Greys',
        zmin=-1, zmax=1,
        texttemplate='%{z:.2f}',
        hovertemplate='%{x} vs %{y}: %{z:.2f}',
    ))
    fig.update_layout(
        title="Correlation Heatmap",
        height=800,
        width=800,
        xaxis=dict(tickangle=-25),
        yaxis=dict(tickangle=0)
    )

    st.plotly_chart(fig, use_container_width=True)  

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
        index=list(asset_categories.keys()).index(st.session_state.selected_catergory)
    )

    asset_tect = asset_categories[categories]

    st.session_state.selected_catergory = categories
    available_tech = [asset for asset in asset_tect if asset in corr_df.columns]

    tech_corr = corr_df.loc[available_tech, available_tech]

    corr, summary = st.columns([2,1])

    with corr:
        st.subheader(f"Correlation of {categories} Assets")

        clean_labels = [asset.replace('_Price', '') for asset in available_tech]
        fig = go.Figure(data=go.Heatmap(
            z=tech_corr.values,
            x=clean_labels,
            y=clean_labels,
            colorscale='Greys',
            zmin=-1, zmax=1,
            texttemplate='%{z:.3f}',
            hovertemplate='%{x} vs %{y}: %{z:.6f}',
        ))
        fig.update_layout(
            title="Correlation Heatmap of {categories}",
            height=800,
            width=800,
        )
        st.plotly_chart(fig, use_container_width=True)

    with summary:
        st.subheader("Summary of Correlation")
        corr_pairs = []
        for i in range(len(available_tech)):
            for j in range(i+1, len(available_tech)):
                corr_pairs.append({
                    'Asset1': available_tech[i],
                    'Asset2': available_tech[j],
                    'Correlation': tech_corr.iloc[i, j]
                })
        
        if corr_pairs:
            corr_df = pd.DataFrame(corr_pairs)
            corr_df = corr_df.sort_values(by='Correlation', ascending=False)
            
            poss, neg = st.columns(2)

            with poss:
                st.subheader("Top Positive")
                top_positive = corr_df.head(6)
                
                for idx, row in top_positive.iterrows():
                    with st.container(border=True):
                        st.write(f"**{row['Asset1'].replace('_Price', '')}** <-> **{row['Asset2'].replace('_Price', '')}**")
                        st.write(f"Correlation: {row['Correlation']:.3f}")

            with neg:    
                st.subheader("Top Negative")
                top_negative = corr_df.tail(6)
                
                for idx, row in top_negative.iterrows():
                    with st.container(border=True):
                        st.write(f"**{row['Asset1'].replace('_Price', '')}** <-> **{row['Asset2'].replace('_Price', '')}**")
                        st.write(f"Correlation: {row['Correlation']:.3f}")

    st.markdown("---")
    st.subheader("🔍 Individual Asset Correlation Analysis")

    # Asset selection
    selected_asset = st.selectbox(
        "Select Asset for Analysis:",
        options=norm_df.columns,
        index=0
    )

    asset_correlations = norm_df.corr()[selected_asset].drop(selected_asset).sort_values(ascending=False)

    # Main layout
    st.markdown("---")
    st.subheader(f"📊 {selected_asset.replace('_Price', '')} Correlation with All Assets")

    # Create heatmap for single asset
    fig = go.Figure(data=go.Heatmap(
        z=[asset_correlations.values],  # Single row
        x=[col.replace('_Price', '') for col in asset_correlations.index],
        y=[selected_asset.replace('_Price', '')],
        colorscale='RdBu',
        zmin=-1, zmax=1,
        zmid=0,
        text=[asset_correlations.values],
        texttemplate='%{text:.3f}',
        textfont={"size": 10},
        hovertemplate='%{y} vs %{x}: %{z:.3f}<extra></extra>',
    ))

    fig.update_layout(
        title=f"{selected_asset.replace('_Price', '')} Correlation Heatmap",
        xaxis_title="Assets",
        yaxis_title="Selected Asset",
        height=350,
        width=1000,
        xaxis=dict(tickangle=-45),
        yaxis=dict(tickangle=0)
    )

    st.plotly_chart(fig, use_container_width=True)

    # Summary section
    st.markdown("---")
    st.subheader(f"📈 Correlation Summary for {selected_asset.replace('_Price', '')}")

    # Create 4 columns for different correlation strengths
    col1, col2, col3, col4 = st.columns(4)

    # Categorize correlations by strength
    very_strong_pos = asset_correlations[asset_correlations >= 0.8]
    strong_pos = asset_correlations[(asset_correlations >= 0.6) & (asset_correlations < 0.8)]
    moderate_pos = asset_correlations[(asset_correlations >= 0.3) & (asset_correlations < 0.6)]
    weak_pos = asset_correlations[(asset_correlations >= 0.1) & (asset_correlations < 0.3)]

    very_strong_neg = asset_correlations[asset_correlations <= -0.8]
    strong_neg = asset_correlations[(asset_correlations <= -0.6) & (asset_correlations > -0.8)]
    moderate_neg = asset_correlations[(asset_correlations <= -0.3) & (asset_correlations > -0.6)]
    weak_neg = asset_correlations[(asset_correlations <= -0.1) & (asset_correlations > -0.3)]

    with col1:
        st.markdown("### 🔥 STRONGEST")
        st.markdown("**POSITIVE CORRELATION** *(> 0.8)*")
        with st.container(border=True):
        
            if len(very_strong_pos) > 0:
                for i, (asset, corr) in enumerate(very_strong_pos.head(3).items()):
                    st.write(f"**{i+1}. {asset.replace('_Price', '')}** {corr:.3f}")
            else:
                st.write("*No very strong positive correlations*")
        
        st.markdown("**NEGATIVE CORRELATION** *(< -0.8)*")
        with st.container(border=True):
        
            if len(very_strong_neg) > 0:
                for i, (asset, corr) in enumerate(very_strong_neg.head(3).items()):
                    st.write(f"**{i+1}. {asset.replace('_Price', '')}** {corr:.3f}")
            else:
                st.write("*No very strong negative correlations*")

    with col2:
        st.markdown("### 💪 STRONG")
        st.markdown("**POSITIVE CORRELATION** *(0.6 - 0.8)*")
        
        with st.container(border=True):
            if len(strong_pos) > 0:
                for i, (asset, corr) in enumerate(strong_pos.head(3).items()):
        
                    
                        st.write(f"**{i+1}. {asset.replace   ('_Price', '')}** {corr:.3f}")

            else:
                st.write("*No strong positive correlations*")
            
        st.markdown("**NEGATIVE CORRELATION** *(−0.6 - −0.8)*")
        
        with st.container(border=True):
            if len(strong_neg) > 0:
                for i, (asset, corr) in enumerate(strong_neg.head(3).items()):
                    st.write(f"**{i+1}. {asset.replace   ('_Price', '')}** {corr:.3f}")

            else:
                st.write("*No strong negative correlations*")

    with col3:
        st.markdown("### 🤝 MODERATE")
        st.markdown("**POSITIVE CORRELATION** *(0.3 - 0.6)*")
        
        with st.container(border=True):
            if len(moderate_pos) > 0:
                for i, (asset, corr) in enumerate(moderate_pos.head(3).items()):
                    st.write(f"**{i+1}. {asset.replace   ('_Price', '')}** {corr:.3f}")

            else:
                st.write("*No moderate positive correlations*")
            
        st.markdown("**NEGATIVE CORRELATION** *(−0.3 - −0.6)*")
        
        with st.container(border=True):
            if len(moderate_neg) > 0:
                for i, (asset, corr) in enumerate(moderate_neg.head(3).items()):
                    st.write(f"**{i+1}. {asset.replace   ('_Price', '')}** {corr:.3f}")
            else:
                st.write("*No moderate negative correlations*")

    with col4:
        st.markdown("### 👌 WEAK")
        st.markdown("**POSITIVE CORRELATION** st.markdown("")")
        
        with st.container(border=True):
            if len(weak_pos) > 0:
                for i, (asset, corr) in enumerate(weak_pos.head(3).items()):
                    st.write(f"**{i+1}. {asset.replace   ('_Price', '')}** {corr:.3f}")

            else:
                st.write("*No weak positive correlations*")
            
        st.markdown("**NEGATIVE CORRELATION** *(−0.1 - −0.3)*")
        
        with st.container(border=True):
            if len(weak_neg) > 0:
                for i, (asset, corr) in enumerate(weak_neg.head(3).items()):
                    st.write(f"**{i+1}. {asset.replace   ('_Price', '')}** {corr:.3f}")

            else:
                st.write("*No weak negative correlations*")

    # Bottom statistics and insights section
    st.markdown("---")

elif page == "Portofolio":
    st.title("Portofolio Analysis of US Stock Market")
        



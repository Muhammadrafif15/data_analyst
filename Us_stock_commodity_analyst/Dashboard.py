import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
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
    st.title("Portofolio Analysis of US Stock Market")

    st.subheader("📊 Detailed Statistical Analysis")

    # Create comprehensive statistics table with all metrics
    stats_columns = ['Asset', 'Return', 'Risk', 'Sharpe', 'VaR', 'MaxDD', 'Skew', 'Kurt', 'Beta', 'Alpha', 'Corr']
    stats_data = []

    for asset in df.columns:
        asset_data = df[asset]
        returns = asset_data.pct_change().dropna()
        
        # Calculate all statistics
        total_return = ((asset_data.iloc[-1] / asset_data.iloc[0]) - 1) * 100
        volatility = returns.std() * np.sqrt(252) * 100
        sharpe = (returns.mean() * 252) / (returns.std() * np.sqrt(252))
        var_95 = np.percentile(returns, 5) * 100
        max_dd = ((asset_data / asset_data.cummax() - 1).min() * 100)
        skewness = returns.skew()
        kurtosis = returns.kurtosis()
        
        stats_data.append([
            asset.replace('_Price', ''),
            f"{total_return:.1f}%",
            f"{volatility:.1f}%", 
            f"{sharpe:.2f}",
            f"{var_95:.1f}%",
            f"{max_dd:.1f}%",
            f"{skewness:.2f}",
            f"{kurtosis:.1f}",
            "1.23",  # Placeholder
            "0.15",  # Placeholder
            "0.83"   # Placeholder
        ])

    stats_df = pd.DataFrame(stats_data, columns=stats_columns)
    st.dataframe(stats_df, use_container_width=True)

    st.subheader("🏆 Asset Performance Leaderboard")

    # Create leaderboard with ranking and grades
    leaderboard_data = []
    returns_list = []

    for asset in df.columns:
        asset_data = df[asset]
        returns = asset_data.pct_change().dropna()
        total_return = ((asset_data.iloc[-1] / asset_data.iloc[0]) - 1) * 100
        volatility = returns.std() * np.sqrt(252) * 100
        sharpe = (returns.mean() * 252) / (returns.std() * np.sqrt(252))
        
        # Determine category
        category = "Other"
        if asset in ['Apple_Price', 'Tesla_Price', 'Microsoft_Price', 'Google_Price', 'Nvidia_Price', 'Netflix_Price', 'Amazon_Price', 'Meta_Price']:
            category = "Tech Stock"
        elif asset in ['Bitcoin_Price', 'Ethereum_Price']:
            category = "Crypto"
        elif asset in ['Natural_Gas_Price', 'Crude_oil_Price', 'Copper_Price', 'Silver_Price', 'Gold_Price', 'Platinum_Price']:
            category = "Commodity"
        elif asset in ['S&P_500_Price', 'Nasdaq_100_Price', 'Berkshire_Price']:
            category = "Index"
        
        # Assign grade based on return
        if total_return >= 80: grade = "A+"
        elif total_return >= 60: grade = "A"
        elif total_return >= 40: grade = "A-"
        elif total_return >= 20: grade = "B+"
        elif total_return >= 0: grade = "B"
        elif total_return >= -10: grade = "C"
        else: grade = "D-"
        
        returns_list.append((asset, total_return))
        
        leaderboard_data.append({
            'Asset': asset.replace('_Price', ''),
            'Return': f"{total_return:.1f}%",
            'Risk': f"{volatility:.1f}%",
            'Sharpe': f"{sharpe:.2f}",
            'Category': category,
            'Grade': grade
        })

    # Sort by return and add ranking
    returns_list.sort(key=lambda x: float(x[1]), reverse=True)
    sorted_leaderboard = []

    for i, (asset, _) in enumerate(returns_list):
        # Find corresponding data
        asset_data = next(item for item in leaderboard_data if item['Asset'] == asset.replace('_Price', ''))
        
        # Add rank emoji
        if i == 0: rank = "🥇1"
        elif i == 1: rank = "🥈2" 
        elif i == 2: rank = "🥉3"
        else: rank = f"{i+1}"
        
        sorted_leaderboard.append({
            'Rank': rank,
            **asset_data
        })

    leaderboard_df = pd.DataFrame(sorted_leaderboard)
    st.dataframe(leaderboard_df, use_container_width=True, hide_index=True)

    st.subheader("📂 Performance by Category")

    asset_categories = {
        '💻 TECH STOCKS': ['Apple_Price', 'Tesla_Price', 'Microsoft_Price', 'Google_Price', 'Nvidia_Price', 'Netflix_Price', 'Amazon_Price', 'Meta_Price'],
        '🪙 CRYPTO': ['Bitcoin_Price', 'Ethereum_Price'],
        '🏭 COMMODITIES': ['Natural_Gas_Price', 'Crude_oil_Price', 'Copper_Price', 'Silver_Price', 'Gold_Price', 'Platinum_Price'],
        '📈 INDICES': ['S&P_500_Price', 'Nasdaq_100_Price', 'Berkshire_Price']
    }

    col1, col2, col3, col4 = st.columns(4)
    columns = [col1, col2, col3, col4]

    for i, (category, assets) in enumerate(asset_categories.items()):
        available_assets = [asset for asset in assets if asset in df.columns]
        
        if available_assets and i < len(columns):
            category_data = []
            for asset in available_assets:
                asset_data = df[asset]
                total_return = ((asset_data.iloc[-1] / asset_data.iloc[0]) - 1) * 100
                category_data.append((asset, total_return))
            
            # Sort by return
            category_data.sort(key=lambda x: x[1], reverse=True)
            avg_return = np.mean([x[1] for x in category_data])
            best_asset, best_return = category_data[0]
            
            with columns[i]:
                st.markdown(f"### {category}")
                st.metric("Avg", f"{avg_return:.1f}%")
                st.metric("Best", best_asset.replace('_Price', ''))
                st.metric("Return", f"{best_return:.1f}%")
                st.markdown("────────────")
                
                # Show top assets in category
                for asset, return_val in category_data[:5]:
                    st.write(f"• {asset.replace('_Price', '')} {return_val:+.1f}%")

    st.subheader("🎯 Portfolio Builder")

    # Control panel in header style
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        investment_year = st.selectbox("Investment Year", [2020, 2021, 2022, 2023])
    with col2:
        total_investment = st.number_input("Total Investment ($)", min_value=100, value=1200, step=100)
    with col3:
        st.write("") # spacer
    with col4:
        st.write("") # spacer

    st.markdown("**Select Assets for Portfolio:**")

    # Asset selection with checkboxes in grid
    assets_per_row = 4
    available_assets = df.columns.tolist()
    selected_assets = []

    for i in range(0, len(available_assets), assets_per_row):
        cols = st.columns(assets_per_row)
        for j, col in enumerate(cols):
            if i + j < len(available_assets):
                asset = available_assets[i + j]
                with col:
                    if st.checkbox(asset.replace('_Price', ''), key=f"portfolio_{asset}"):
                        selected_assets.append(asset)

    if selected_assets:
        st.session_state.portfolio_assets = selected_assets
        st.session_state.portfolio_investment = total_investment
        st.success(f"✅ Portfolio built with {len(selected_assets)} assets!")

    if 'portfolio_assets' in st.session_state and st.session_state.portfolio_assets:
        st.subheader("Portfolio Allocation")
        
        portfolio_assets = st.session_state.portfolio_assets
        total_investment = st.session_state.portfolio_investment
        
        # Calculate allocation based on positive returns
        allocation_data = []
        for asset in portfolio_assets:
            asset_data = df[asset]
            total_return = ((asset_data.iloc[-1] / asset_data.iloc[0]) - 1) * 100
            if total_return > 0:  # Only positive returns for allocation
                allocation_data.append({
                    'Asset': asset.replace('_Price', ''),
                    'Return': total_return
                })
        
        if allocation_data:
            allocation_df = pd.DataFrame(allocation_data)
            total_positive_returns = allocation_df['Return'].sum()
            allocation_df['Weight'] = allocation_df['Return'] / total_positive_returns
            allocation_df['Amount'] = allocation_df['Weight'] * total_investment
            
            # Two-column layout for pie chart and table
            col1, col2 = st.columns([2,1])
            
            with col1:
                # Interactive donut chart
                fig = px.pie(
                    allocation_df, 
                    values='Weight', 
                    names='Asset',
                    title="Portfolio Allocation",
                    color_discrete_sequence=px.colors.qualitative.T10
                )
                fig.update_traces(
                    textposition='inside', 
                    textinfo='percent+label',
                    textfont_size=16
                )

                fig.update_layout(
                    height=800,  # Pixel height
                    width=800    # Pixel width
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("**Allocation Table**")
                
                # Format table data
                table_data = allocation_df.copy()
                table_data['Weight'] = (table_data['Weight'] * 100).round(1).astype(str) + '%'
                table_data['Amount'] = '$' + table_data['Amount'].round(0).astype(int).astype(str)
                table_data['Return'] = table_data['Return'].round(1).astype(str) + '%'
                
                # Display formatted table
                st.dataframe(
                    table_data[['Asset', 'Weight', 'Amount', 'Return']], 
                    use_container_width=True, 
                    hide_index=True,
                    column_config={
                        "Asset": "Asset",
                        "Weight": "Weight",
                        "Amount": "Amount", 
                        "Return": "Expected Return"
                    }
                )
        else:
            st.warning("No assets with positive returns selected for allocation.")
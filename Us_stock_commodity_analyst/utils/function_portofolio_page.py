import streamlit as st
import pandas as pd
import numpy as np


def describe_portofolio (df):
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

def rank_asset_analisis(df):
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

def asset_performance(df):
    asset_categories = {
        'TECH STOCKS': ['Apple_Price', 'Tesla_Price', 'Microsoft_Price', 'Google_Price', 'Nvidia_Price', 'Netflix_Price', 'Amazon_Price', 'Meta_Price'],
        'CRYPTO': ['Bitcoin_Price', 'Ethereum_Price'],
        'COMMODITIES': ['Natural_Gas_Price', 'Crude_oil_Price', 'Copper_Price', 'Silver_Price', 'Gold_Price', 'Platinum_Price'],
        'INDICES': ['S&P_500_Price', 'Nasdaq_100_Price', 'Berkshire_Price']
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

def portofolio_custom(df):
    total_investment = st.number_input("Total Investment ($)", min_value=100, value=1200, step=100)

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
                    
    st.session_state.portfolio_assets = selected_assets
    st.session_state.portfolio_investment = total_investment
    st.success(f"Portfolio built with {len(selected_assets)} assets!")

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
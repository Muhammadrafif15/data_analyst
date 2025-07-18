import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def asset_correlation_strength(corr):
    with st.container(border=True):        
        if len(corr) > 0:
            for i, (asset, corr) in enumerate(corr.head(3).items()):
                st.write(f"**{i+1}. {asset.replace('_Price', '')}** {corr:.3f}")
        else:
            st.write("*No correlations*")

def stastistic_correlation(top_corr):
    for idx, row in top_corr.iterrows():
        with st.container(border=True):
            st.write(f"**{row['Asset1'].replace('_Price', '')}** <-> **{row['Asset2'].replace('_Price', '')}**")
            st.write(f"Correlation: {row['Correlation']:.3f}")

def correlation_summary(asset_correlations):
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
        st.markdown("### STRONGEST")
        st.markdown("**POSITIVE CORRELATION** *(> 0.8)*")
        asset_correlation_strength(very_strong_pos)
        
        st.markdown("**NEGATIVE CORRELATION** *(< -0.8)*")
        asset_correlation_strength(very_strong_neg)

    with col2:
        st.markdown("### STRONG")
        st.markdown("**POSITIVE CORRELATION** *(0.6 - 0.8)*")
        asset_correlation_strength(strong_pos)     

        st.markdown("**NEGATIVE CORRELATION** *(−0.6 - −0.8)*")
        asset_correlation_strength(strong_neg)

    with col3:
        st.markdown("### MODERATE")
        st.markdown("**POSITIVE CORRELATION** *(0.3 - 0.6)*")
        asset_correlation_strength(moderate_pos)
        
            
        st.markdown("**NEGATIVE CORRELATION** *(−0.3 - −0.6)*")
        asset_correlation_strength(moderate_neg)

    with col4:
        st.markdown("### WEAK")
        st.markdown("**POSITIVE CORRELATION** *(−0.1 - −0.3)*")

        asset_correlation_strength(weak_pos)

        st.markdown("**NEGATIVE CORRELATION** *(−0.1 - −0.3)*")
        
        asset_correlation_strength(weak_neg)
    # Bottom statistics and insights section
    st.markdown("---")

def single_correlation (asset_correlations, selected_asset):

    fig = go.Figure(data=go.Heatmap(
        z=[asset_correlations.values],  # Single row
        x=[col.replace('_Price', '') for col in asset_correlations.index],
        y=[selected_asset.replace('_Price', '')],
        colorscale='RdBu',
        zmin=-1, zmax=1,
        zmid=0,
        text=[asset_correlations.values],
        texttemplate='%{text:.3f}',
        textfont={"size": 16},
        hovertemplate='%{y} vs %{x}: %{z:.3f}<extra></extra>',
    ))

    fig.update_layout(
        title=f"{selected_asset.replace('_Price', '')} Correlation Heatmap",
        xaxis_title="Assets",
        yaxis_title="Selected Asset",
        height=350,
        width=1000,
        yaxis=dict(
            tickfont=dict(size=13)
        ),
        xaxis=dict(
            tickfont=dict(size=13)
        )
    )

    st.plotly_chart(fig, use_container_width=True)

def categori_correlation(categories, tech_corr, available_tech):
    corr, summary = st.columns([2,1])

    with corr:
        st.subheader(f"Correlation of {categories} Assets")

        clean_labels = [asset.replace('_Price', '') for asset in available_tech]
        fig = go.Figure(data=go.Heatmap(
            z=tech_corr.values,
            x=clean_labels,
            y=clean_labels,
            colorscale='RdBu',
            zmin=-1, zmax=1,
            textfont={"size" : 16},
            texttemplate='%{z:.3f}',
            hovertemplate='%{x} vs %{y}: %{z:.6f}',
        ))
        fig.update_layout(
            title=f"Correlation Heatmap of {categories}",
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
                stastistic_correlation(top_positive)
                
            with neg:    
                st.subheader("Top Negative")
                top_negative = corr_df.tail(6)
                stastistic_correlation(top_negative)

def main_correlation(corr_df):
    fig = go.Figure(data=go.Heatmap(
        z=corr_df.values,
        x=[col.replace("_Price", "") for col in corr_df.columns],
        y=[col.replace("_Price", "") for col in corr_df.columns],
        colorscale='RdBu',
        zmin=-1, zmax=1,
        texttemplate='%{z:.2f}',
        hovertemplate='%{x} vs %{y}: %{z:.2f}',
    ))
    fig.update_layout(
        title="Correlation Heatmap",
        height=800,
        width=800,
        xaxis=dict(tickangle=-25, tickfont=dict(size = 13)),
        yaxis=dict(tickangle=0, tickfont=dict(size = 13))
    )

    st.plotly_chart(fig, use_container_width=True)  


def price_line_plot(category_data, available_assets, categories, norm_df):
    fig = px.line(
        category_data,
        x=category_data.index,
        y=available_assets,
        title=f"{categories} Price Movement",
        labels={'index': 'Date', 'value': 'Normalized Price', 'variable': 'Assets'},
        height=600
    )
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Normalized Price",
        legend_title="Assets",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)

    metrics_data = []
    for asset in available_assets:
        info_asset = norm_df[asset]
        metrics_data.append({
            'Asset': asset.replace('_Price', ''),
            'Close': info_asset.iloc[-1],
            'Start': info_asset.iloc[0],
            'Max': info_asset.max(),
            'Min': info_asset.min(),
            'Average': info_asset.mean(),
            'Change': ((info_asset.iloc[-1] - info_asset.iloc[0]) / info_asset.iloc[0]) * 100,
            'Volatility': info_asset.std()
        })

    metrics_df = pd.DataFrame(metrics_data)

    # Display metrics table
    st.dataframe(
        metrics_df.round(3),
        use_container_width=True,
        column_config={
            "Asset": "Asset Name",
            "Close": st.column_config.NumberColumn("Current Price", format="%.3f"),
            "Start": st.column_config.NumberColumn("Start Price", format="%.3f"),
            "Max": st.column_config.NumberColumn("Max Price", format="%.3f"),
            "Min": st.column_config.NumberColumn("Min Price", format="%.3f"),
            "Average": st.column_config.NumberColumn("Avg Price", format="%.3f"),
            "Change": st.column_config.NumberColumn("Total Change (%)", format="%.2f%%"),
            "Volatility": st.column_config.NumberColumn("Volatility", format="%.3f")
        }
    )

def plot_custom_asset(norm_df, selected_custom_assets):
    date_filter = st.checkbox("Filter by Date Range")
        
    if date_filter:
        start_date = st.date_input("Start Date", norm_df.index[0])
        end_date = st.date_input("End Date", norm_df.index[-1])
        
        # Filter data berdasarkan date range
        mask = (norm_df.index.date >= start_date) & (norm_df.index.date <= end_date)
        plot_data = norm_df.loc[mask, selected_custom_assets]
    else:
        plot_data = norm_df[selected_custom_assets]
    
    fig = px.line(
        plot_data,
        x=plot_data.index,
        y=selected_custom_assets,
        title="Custom Assets Comparison",
        labels={'index': 'Date', 'value': 'Normalized Price', 'variable': 'Assets'}
    )
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Normalized Price",
        legend_title="Assets",
        height=600,
        hovermode='x unified'
    )
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    for i, trace in enumerate(fig.data):
        fig.data[i].line.width = 3
        fig.data[i].line.color = colors[i % len(colors)]
    
    st.plotly_chart(fig, use_container_width=True)
    
    if len(selected_custom_assets) > 0:
        st.subheader("Selected Assets Summary")
        
        cols = st.columns(len(selected_custom_assets))
        
        for i, asset in enumerate(selected_custom_assets):
            with cols[i]:
                asset_data = plot_data[asset] if date_filter else norm_df[asset]
                current_price = asset_data.iloc[-1]
                start_price = asset_data.iloc[0]
                change = ((current_price - start_price) / start_price) * 100
                
                st.metric(
                    label=asset.replace('_Price', ''),
                    value=f"{current_price:.3f}",
                    delta=f"{change:+.2f}%"
                )
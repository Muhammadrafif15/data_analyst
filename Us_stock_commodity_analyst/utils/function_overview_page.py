import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

def get_dataset_info(df):
    """Get basic dataset information"""
    return {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'total_assets': len(df.columns) - 1,  # Exclude Date column
        'total_data_points': len(df) * (len(df.columns) - 1),
        'file_size': f"{len(df) * len(df.columns) * 8 / (1024*1024):.1f} MB",  # Approximate
    }

def categorize_assets():
    """Define asset categories"""
    return {
        '💻 TECH STOCKS': ['Apple_Price', 'Tesla_Price', 'Microsoft_Price', 'Google_Price', 
                           'Nvidia_Price', 'Netflix_Price', 'Amazon_Price', 'Meta_Price'],
        '🏭 COMMODITIES': ['Natural_Gas_Price', 'Crude_oil_Price', 'Copper_Price', 
                           'Platinum_Price', 'Silver_Price', 'Gold_Price'],
        '🪙 CRYPTO': ['Bitcoin_Price', 'Ethereum_Price'],
        '📈 INDICES': ['S&P_500_Price', 'Nasdaq_100_Price', 'Berkshire_Price']
    }

def create_dataset_header(df):
    """Create dataset summary header"""
    info = get_dataset_info(df)
    
    st.markdown("""
    <div style="padding: 20px; border-radius: 10px; border-left: 5px solid #1f77b4;">
        <h3>DATASET INFORMATION</h3>
        <p><strong>Dataset:</strong> US Stock & Commodity Price Data (Cleaned)</p>
        <p><strong>Total Records:</strong> {total_rows} trading days</p>
        <p><strong>Total Columns:</strong> {total_columns} (1 Date + {total_assets} Asset Prices)</p>
        <p><strong>Total Data Points:</strong> {total_rows} × {total_assets} = {total_data_points} price records</p>
        <p><strong>File Format:</strong> CSV | <strong>Encoding:</strong> UTF-8 | <strong>Status:</strong> Cleaned & Ready</p>
    </div>
    """.format(**info), unsafe_allow_html=True)

def create_data_structure_overview(df):
    """Create data structure overview"""
    st.subheader("Data Structure Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Rows", f"{len(df)}")
        st.metric("Date Column", "1 (String/DateTime)")
    
    with col2:
        st.metric("Total Columns", f"{len(df.columns)}")
        st.metric("Price Columns", f"{len(df.columns) - 1} (Float)")
    
    with col3:
        st.metric("Data Points", f"{len(df) * (len(df.columns) - 1):,}")
        st.metric("Data Type", "Normalized Prices")


def create_category_breakdown(df):
    """Create category distribution breakdown"""
    st.subheader("Asset Categories Breakdown")
    
    asset_categories = categorize_assets()
    asset_columns = [col for col in df.columns if col != 'Date']
    
    # Calculate category stats
    category_stats = {}
    for category, assets in asset_categories.items():
        available_assets = [asset for asset in assets if asset in asset_columns]
        category_stats[category] = {
            'count': len(available_assets),
            'percentage': len(available_assets) / len(asset_columns) * 100,
            'assets': available_assets,
            'records': len(df) * len(available_assets)
        }
    
    # Create 4 columns for categories
    cols = st.columns(4)
    
    for i, (category, stats) in enumerate(category_stats.items()):
        with cols[i]:
            st.markdown(f"### {category}")
            st.metric("Count", f"{stats['count']} assets")
            st.metric("Percentage", f"{stats['percentage']:.0f}%")
            
            st.markdown("**Assets:**")
            for asset in stats['assets'][:5]:  # Show first 5
                asset_display = asset.replace('_Price', '').replace('_', ' ')
                st.write(f"• {asset_display}")
            
            if len(stats['assets']) > 5:
                st.write(f"• +{len(stats['assets']) - 5} more...")
            
            st.markdown("────────────")
            st.metric("Records", f"{stats['records']:,} points")


def create_sample_data_structure(df):
    """Show sample data structure"""
    st.subheader("Data Sample Structure")
    
    # Show first 10 rows with proper formatting
    sample_df = df.head(10).copy()
    
    # If Date is in index, reset it to show as column
    if 'Date' not in sample_df.columns:
        sample_df = sample_df.reset_index()
    
    st.write("**First 10 rows of the dataset:**")
    st.dataframe(
        sample_df,
        use_container_width=True,
        height=400
    )

def create_data_overview_page(df):
    """Main function to create complete data overview page"""
    
    st.title("Data Overview & Information")
    st.markdown("Complete information about the dataset structure")

    create_dataset_header(df)
    st.markdown("---")

    create_sample_data_structure(df)
    st.markdown("---")
    
    # 1. Dataset Header
    
    
    # 2. Data Structure Overview
    create_data_structure_overview(df)
    st.markdown("---")
    
    # 4. Category Breakdown
    create_category_breakdown(df)
    st.markdown("---")

    
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import calendar

def yearly_seasonal_plot(data_tahun, year):

    colom1, colom2 = st.columns([3, 1])
    with colom1:
        fig = px.line(data_tahun, x=data_tahun.index, y=data_tahun)

        fig.update_layout(
            title=f"{year} Price Trend",
            xaxis_title="Date",
            yaxis_title="Price",
            height=600
        )
        st.plotly_chart(fig, use_container_width=False)                

    with colom2:
        st.subheader(f"Price Statistics of {year}")
        st.metric("Total Days", len(data_tahun), delta=None)
        st.write(f"From {data_tahun.index[0].strftime('%Y-%m-%d')} to {data_tahun.index[-1].strftime('%Y-%m-%d')}")

        col1, col2 = st.columns(2)
                        
        with col1:
            with st.container(border=True):
                st.metric("Starting Price", f"{data_tahun.iloc[0]:.2f}", delta=None)
                st.write(data_tahun.index[0].strftime("%Y-%m-%d"))
            
            with st.container(border=True):
                st.metric("Closing Price", f"{data_tahun.iloc[-1]:.2f}", delta=None)
                st.write(data_tahun.index[-1].strftime("%Y-%m-%d"))

        with col2:
            with st.container(border=True):
                st.metric("Max Price", f"{data_tahun.max():.2f}", delta=None)
                st.write(data_tahun.idxmax().strftime("%Y-%m-%d"))
            
            with st.container(border=True):
                st.metric("Min Price", f"{data_tahun.min():.2f}", delta=None)
                st.write(data_tahun.idxmin().strftime("%Y-%m-%d"))

def monthly_mean_seasonal_plot(data_tahun, year):

    colom3, colom4 = st.columns([3,1])
    with colom3:
        monthly_mean = data_tahun.groupby(data_tahun.index.to_period("M")).mean()
        fig = px.line(monthly_mean, x=monthly_mean.index.astype(str), y=monthly_mean, markers=True,)

        fig.layout.update(
            title=f"Mean of {year}",
            xaxis_title="Month",
            yaxis_title="Mean Price",
        )
        st.plotly_chart(fig, use_container_width=False)

    with colom4:
        st.subheader(f"Mean Price Statistics of {year}")
        col5, col6 = st.columns(2)
        with col5:
            with st.container(border=True):
                st.metric("Max Monthly Mean", f"{monthly_mean.max():.2f}", delta=None)
                st.write(monthly_mean.idxmax().strftime("%Y-%m"))
        with col6:
            with st.container(border=True):
                st.metric("Min Monthly Mean", f"{monthly_mean.min():.2f}", delta=None)
                st.write(monthly_mean.idxmin().strftime("%Y-%m")) 

def card_monthly_seasonal(data_month, month_name):
    if len(data_month) > 0:  # Check if data exists
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data_month.index,
            y=data_month,
            mode='lines+markers',
            name=f'{month_name}',
            line=dict(width=3),
            marker=dict(size=8)
        ))
        fig.update_layout(
            height=250,
            margin=dict(l=20, r=20, t=20, b=20),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Area untuk statistics
        stats_container = st.container()
        with stats_container:
            # Metrics dalam 2 kolom
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            
            with metric_col1:
                st.metric("Start", f"{data_month.iloc[0]:.2f}")
                st.metric("High", f"{data_month.max():.2f}")
                st.metric("Days", f"{len(data_month)}")
            
            with metric_col2:
                st.metric("End", f"{data_month.iloc[-1]:.2f}")
                st.metric("Low", f"{data_month.min():.2f}")
                st.metric("Avg", f"{data_month.mean():.2f}")

            with metric_col3:
                change_start_end = data_month.iloc[-1] - data_month.iloc[0]
                change_percent = (change_start_end / data_month.iloc[0])
                st.metric("Start-End", f"{change_start_end:+.2f}", f"{change_percent:+.1%}")
                change_high_low = data_month.max() - data_month.min()
                change_high_low_percent = (change_high_low / data_month.min())
                st.metric("High-Low", f"{change_high_low:+.2f}", f"{change_high_low_percent:+.1%}") 
                                                                    
    else:
        st.info(f"No data available for {month_name}")

def card_layout(data_tahun, year):
    
    months = list(range(1, 13))  # 1-12 untuk bulan
    month_names = [calendar.month_name[i] for i in months]

    for row in range(4):
        # Buat 3 kolom untuk setiap baris
        col1, col2, col3 = st.columns(3)

        for i, col in enumerate([col1, col2, col3]):
            month_index = row * 3 + i
            if month_index < 12:
                month_num = months[month_index]
                month_name = month_names[month_index]
                data_month = data_tahun[data_tahun.index.month == month_num]

                with col:
                    with st.container(border=True):
                        st.subheader(f"{month_name.upper()} {year}" )
                        card_monthly_seasonal(data_month, month_name)

        if row < 3:
            st.markdown("---")  # Garis pemisah antar baris

def summary_year_seasonal(data_tahun):

    st.markdown("### 📈 Year Summary")
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)

    # Calculate monthly stats for summary
    monthly_stats = []
    for month in range(1, 13):
        month_data = data_tahun[data_tahun.index.month == month]
        if len(month_data) > 0:
            monthly_change = ((month_data.iloc[-1] - month_data.iloc[0]) / month_data.iloc[0]) * 100
            monthly_stats.append({
                'month': calendar.month_name[month],
                'change': monthly_change,
                'avg_price': month_data.mean()
            })

    if monthly_stats:
        # Find best and worst months
        best_month = max(monthly_stats, key=lambda x: x['change'])
        worst_month = min(monthly_stats, key=lambda x: x['change'])
        
        with summary_col1:
            st.metric("Best Month", best_month['month'], f"+{best_month['change']:.1f}%")
            
        with summary_col2:
            st.metric("Worst Month", worst_month['month'], f"{worst_month['change']:.1f}%")
            
        with summary_col3:
            avg_price = sum([stat['avg_price'] for stat in monthly_stats]) / len(monthly_stats)
            st.metric("Avg Price", f"{avg_price:.2f}")
            
        with summary_col4:
            volatility = data_tahun.std()
            st.metric("Volatility", f"{volatility:.2f}")
    else:
        with summary_col1:
            st.metric("Best Month", "N/A", "N/A")
        with summary_col2:
            st.metric("Worst Month", "N/A", "N/A")
        with summary_col3:
            st.metric("Avg Price", "N/A")
        with summary_col4:
            st.metric("Volatility", "N/A")  
    
def tap_year_seasonal(data ,year):
    data_tahun = data[data.index.year == year]
    
    st.subheader(f"Seasonal Analysis of {year}")
    
    # Plot yearly trend
    yearly_seasonal_plot(data_tahun, year)
    st.markdown("---")

    # Monthly mean plot
    monthly_mean_seasonal_plot(data_tahun, year)
    st.markdown("---")

    # Card layout for monthly seasonal data
    card_layout(data_tahun, year)
    st.markdown("---")

    # Summary of the data_tahun, year
    summary_year_seasonal(data_tahun)
    st.markdown("---")
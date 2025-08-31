# US Stock & Commodity Analyst

A data analysis project focusing on US stock markets and commodities, featuring interactive visualizations through Streamlit.

## Features

- stock and commodity data analysis
- Statistical analysis and data visualization
- Optimize portofolio
- Correlation Assets
- Interactive Streamlit dashboard
- Detailed documentation and code explanations

## Project Structure

- `Us_stock_commodity_analyst/US_stock_commodity.zip/` : Raw datasets and preprocessed data
- `Us_stock_commodity_analyst/Notebook_Us_stock_and_commodity.ipynb/` : Jupyter notebooks for exploration and analysis
- `Dashboard.py/` : Streamlit dashboard files
- `utils/`: Page of dashboard

## Setup & Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/us_stock_commodity_analyst.git
cd us_stock_commodity_analyst
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Streamlit App

1. Navigate to the project directory:
```bash
cd Us_stock_commodity_analyst
```
```
# path untuk deploy
file_path = os.path.join(os.path.dirname(__file__), "US_Stock_Data_Cleaned.csv")
df = pd.read_parquet(file_path)

# path untuk local
# df = pd.read_parquet("US_Stock_Data_Cleaned.csv")
```

2. Run the Streamlit app:
```bash
streamlit run Dashboard.py
```

3. Open your browser and go to `http://localhost:8501`



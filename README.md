# Uber-trip-analysis-dashboard
Data analysis project I was working on
# Uber Trip Analysis Dashboard

## Overview
An interactive dashboard built with Streamlit to analyze Uber trip data in New York City. The dashboard provides insights into trip patterns, fare analysis, and geographical distribution of rides.

## Features
- Interactive filters for date range and trip distance
- Fare analysis and revenue metrics
- Geographical visualization of pickup and dropoff locations
- Time-based analysis of trip patterns
- Secure access with password protection

## Technologies Used
- Python
- Streamlit
- Pandas
- Plotly
- PyArrow (for Parquet file handling)

## Installation
1. Clone the repository
```bash
git clone https://github.com/yourusername/uber-analysis-dashboard.git
cd uber-analysis-dashboard
```

2. Install required packages
```bash
pip install -r requirements.txt
```

3. Set up secrets
Create a `.streamlit/secrets.toml` file with your password:
```toml
password = "your-password-here"
```

4. Run the application
```bash
streamlit run app.py
```

## Usage
1. Start the application
2. Enter the password when prompted
3. Use the sidebar filters to analyze specific data ranges
4. Download filtered data as CSV if needed

## Data Requirements
The application expects a Parquet file with the following columns:
- pickup_datetime
- dropoff_datetime
- trip_miles
- base_passenger_fare
- dispatching_base_num
- (other columns as needed)

## Contributing
Feel free to fork this repository and submit pull requests for any improvements.

## License
MIT License

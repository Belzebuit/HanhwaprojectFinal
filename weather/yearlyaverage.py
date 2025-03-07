import pandas as pd

def process_weather_data(input_file):
    """
    Process weather data to calculate yearly averages for Korea-wide and region-specific data.

    Parameters:
        input_file (str): Path to the weather data CSV file.

    Returns:
        yearly_averages (DataFrame): Yearly averages for Korea-wide.
        region_averages (DataFrame): Yearly averages by region.
    """
    # Load the weather data
    weather_data = pd.read_csv(input_file, encoding='euc-kr')

    # Extract year from 관측시각 (KST)
    weather_data['연도'] = weather_data['관측시각 (KST)'].astype(str).str[:4]

    # Rename column '국내 지점번호' to '지역'
    weather_data.rename(columns={'국내 지점번호': '지역'}, inplace=True)

    # Round numeric columns to one decimal place
    numeric_cols = weather_data.select_dtypes(include='number').columns
    numeric_cols = numeric_cols.drop('관측시각 (KST)', errors='ignore')  # Exclude 관측시각 (KST)
    weather_data[numeric_cols] = weather_data[numeric_cols].round(1)

    # Calculate yearly averages for Korea-wide
    yearly_averages = weather_data.groupby('연도')[numeric_cols].mean().round(1)

    # Calculate yearly averages by region
    region_averages = weather_data.groupby(['연도', '지역'])[numeric_cols].mean().round(1)

    return yearly_averages, region_averages

# Example usage
input_file = './1224weather.csv'  # Replace with your file path
yearly_averages, region_averages = process_weather_data(input_file)

# Save results to CSV files with ANSI encoding
yearly_averages.to_csv('./yearly_averages_korea.csv', index=True, encoding='ansi')
region_averages.to_csv('./yearly_averages_by_region.csv', index=True, encoding='ansi')

print("Yearly averages for Korea-wide and by region have been saved.")
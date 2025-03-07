import pandas as pd

def process_quarterly_weather_data(input_file):
    """
    Process weather data to calculate quarterly averages for Korea-wide and region-specific data.

    Parameters:
        input_file (str): Path to the weather data CSV file.

    Returns:
        quarterly_averages (DataFrame): Quarterly averages for Korea-wide.
        region_quarterly_averages (DataFrame): Quarterly averages by region.
    """
    # Load the weather data
    weather_data = pd.read_csv(input_file, encoding='euc-kr')

    # Extract year and quarter from 관측시각 (KST)
    weather_data['연도'] = weather_data['관측시각 (KST)'].astype(str).str[:4]
    분기 = weather_data['관측시각 (KST)'].astype(str).str[4:6].astype(int).apply(lambda x: (x - 1) // 3 + 1)
    weather_data['분기'] = 분기.astype(str) + '분기'

    # Rename column '국내 지점번호' to '지역'
    weather_data.rename(columns={'국내 지점번호': '지역'}, inplace=True)

    # Round numeric columns to one decimal place
    numeric_cols = weather_data.select_dtypes(include='number').columns
    numeric_cols = numeric_cols.drop('관측시각 (KST)', errors='ignore')  # Exclude 관측시각 (KST)
    weather_data[numeric_cols] = weather_data[numeric_cols].round(1)

    # Calculate quarterly averages for Korea-wide
    weather_data['연도_분기'] = weather_data['연도'] + '-' + weather_data['분기']
    quarterly_averages = weather_data.groupby('연도_분기')[numeric_cols].mean().round(1)

    # Calculate quarterly averages by region
    region_quarterly_averages = weather_data.groupby(['연도_분기', '지역'])[numeric_cols].mean().round(1)

    return quarterly_averages, region_quarterly_averages

# Example usage
input_file = './cleaned_1224weather.csv'  # Replace with your file path
quarterly_averages, region_quarterly_averages = process_quarterly_weather_data(input_file)

# Save results to CSV files with ANSI encoding
quarterly_averages.to_csv('./quarterly_averages_korea.csv', index=True, encoding='ansi')
region_quarterly_averages.to_csv('./quarterly_averages_by_region.csv', index=True, encoding='ansi')

print("Quarterly averages for Korea-wide and by region have been saved.")

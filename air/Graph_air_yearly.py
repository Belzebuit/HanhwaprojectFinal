import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc

# Set font to display Korean characters properly
rc("font", family="Malgun Gothic")  # For Windows, replace with "AppleGothic" for macOS or "NanumGothic" for Linux
plt.rcParams['axes.unicode_minus'] = False  # Prevent minus sign issues

# Load the CSV file
annual_avg = pd.read_csv('region_yearly_avg.csv', encoding="utf-8-sig")

# Visualization function
def plot_annual_pollutant_data_by_city(data, pollutant, y_limit=None):
    for city in data["지역"].unique():
        city_data = data[data["지역"] == city]
        city_data = city_data[city_data["Year"] < 2024]  # Exclude 2024 data
        if pollutant == "PM2.5(μg/m³)":
            city_data = city_data[city_data["Year"] >= 2015]
        plt.figure(figsize=(12, 6))
        plt.plot(
            city_data["Year"].astype(str),
            city_data[pollutant].interpolate(method='linear'),  # Interpolate missing values
            marker="o",
            label=city
        )
        plt.title(f"{pollutant} Annual Averages - {city}")
        plt.xlabel("Year")
        plt.ylabel(pollutant)
        plt.xticks(city_data["Year"].astype(str), rotation=45)
        if y_limit:
            max_value = city_data[pollutant].max() * 1.2 if not city_data[pollutant].max() < y_limit else y_limit
            plt.ylim(0, max(max_value, y_limit))  # Ensure y_limit accommodates data
        plt.legend(loc="best")
        plt.tight_layout()
        plt.show()

# Set consistent y-axis limit for all pollutants
y_limit = {
    "PM2.5(μg/m³)": 50,
    "PM10(μg/m³)": 80,
    "아황산가스(ppm)": 0.01,
    "오존(ppm)": 0.04,
    "이산화질소(ppm)": 0.05,
    "일산화질소(ppm)": 1
}

# Visualize each pollutant for each city
for pollutant in y_limit.keys():
    plot_annual_pollutant_data_by_city(annual_avg, pollutant, y_limit.get(pollutant))

print("Annual pollutants visualized by city.")

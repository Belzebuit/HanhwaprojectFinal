import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc

# Set font to display Korean characters properly
rc("font", family="Malgun Gothic")  # For Windows, replace with "AppleGothic" for macOS or "NanumGothic" for Linux
plt.rcParams['axes.unicode_minus'] = False  # Prevent minus sign issues

# Load the CSV file
quarterly_avg = pd.read_csv('region_quarterly_avg.csv', encoding="utf-8-sig")

# Visualization function
def plot_pollutant_data_by_city(data, pollutant, y_limit=None):
    for city in data["지역"].unique():
        city_data = data[data["지역"] == city]
        if pollutant == "PM2.5(μg/m³)":
            city_data = city_data[city_data["Year"] >= 2015]
        plt.figure(figsize=(12, 6))
        plt.plot(
            city_data["Year"].astype(str) + "Q" + city_data["Quarter"].astype(str),
            city_data[pollutant].interpolate(method='linear'),  # Interpolate missing values
            marker="o",
            label=city
        )
        plt.title(f"{pollutant} Quarterly Averages - {city}")
        plt.xlabel("Year-Quarter")
        plt.ylabel(pollutant)
        # Set all quarter labels but only show Q1 as text
        x_labels = city_data["Year"].astype(str) + "Q" + city_data["Quarter"].astype(str)
        x_text_labels = [f"{year}Q1" if quarter == 1 else "" for year, quarter in zip(city_data["Year"], city_data["Quarter"])]
        plt.xticks(x_labels, labels=x_text_labels, rotation=45)
        if y_limit:
            plt.ylim(0, y_limit)  # Use a fixed y_limit for consistent scale
        plt.legend(loc="best")
        plt.tight_layout()
        plt.show()

# Set consistent y-axis limit for all pollutants
y_limit = {
    "PM2.5(μg/m³)": 50,
    "PM10(μg/m³)": 80,
    "아황산가스(ppm)": 0.012,
    "오존(ppm)": 0.06,
    "이산화질소(ppm)": 0.05,
    "일산화질소(ppm)": 1
}

# Visualize each pollutant for each city
for pollutant in y_limit.keys():
    plot_pollutant_data_by_city(quarterly_avg, pollutant, y_limit.get(pollutant))

print("Pollutants visualized by city.")

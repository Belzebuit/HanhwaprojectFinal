import os
import pandas as pd

def merge_csv_files(input_folder, output_file):
    """
    Merge all CSV files in a folder into a single CSV file.

    Parameters:
        input_folder (str): Path to the folder containing CSV files.
        output_file (str): Path to save the merged CSV file.
    """
    # List to store individual DataFrames
    csv_list = []

    # Iterate through all files in the input folder
    for filename in os.listdir(input_folder):
        # Check if the file is a CSV
        if filename.endswith('.csv'):
            file_path = os.path.join(input_folder, filename)
            print(f"Reading file: {file_path}")
            # Read the CSV file and append it to the list
            csv_list.append(pd.read_csv(file_path))

    # Concatenate all DataFrames in the list
    merged_csv = pd.concat(csv_list, ignore_index=True)

    # Save the merged DataFrame to a new CSV file
    merged_csv.to_csv(output_file, index=False)
    print(f"Merged CSV saved to: {output_file}")

# Example usage
input_folder = './1224weather'  # 폴더 경로를 지정하세요
output_file = './1224weather.csv'  # 병합된 파일 저장 경로를 지정하세요

merge_csv_files(input_folder, output_file)

import os.path
from datetime import datetime
import pandas as pd
import sys

file_path = 'medicines.csv'

def check_expired_med(file_path):
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            df['Expiry Date'] = pd.to_datetime(df['Expiry Date'], format='%Y-%m-%d', errors='coerce')
            expired_medicines = df[df['Expiry Date'] < datetime.now()]
            if not expired_medicines.empty:
                expired_medicines.to_csv('Expired Medicines.csv', index=False)
                print("::set-output name=expired_report_exists::true")  # GitHub Actions output
            else:
                print("No expired medicines found.")
                print("::set-output name=expired_report_exists::false")
        except Exception as e:
            print(f"Exception error: {e}")
            print("::set-output name=expired_report_exists::false")  # No report due to error
    else:
        print("File not found.")
        print("::set-output name=expired_report_exists::false")  # No report as file not found

def main():
    check_expired_med(file_path)

if __name__ == '__main__':
    main()

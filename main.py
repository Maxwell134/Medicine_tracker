import time

import pandas as pd
from datetime import datetime
import os
import streamlit as st

# Set a password for the app (just a basic example, for more secure solutions, see below)
PASSWORD = "mintu"


# Streamlit UI for password input
def authenticate():
	st.title("Medicine Expiry Checker")

	password = st.text_input("Enter the password to access the app", type="password")

	if password != PASSWORD:
		st.error("Incorrect password! Please try again.")
		return False

	return True

# Load Data
def load_data():
	file_path = 'medicines.csv'

	# Check if the file exists
	if not os.path.exists(file_path):
		# If the file doesn't exist, create it with default columns
		st.warning(
			f"File {file_path} does not exist. Creating a default file with 'Medicine' and 'Expiry Date' columns.")
		df = pd.DataFrame(columns=['Medicine', 'Description', 'Availability', 'Expiry Date'])
		df.to_csv(file_path, index=False)  # Save the default DataFrame to the file
		return df

	try:
		# Attempt to load the CSV file
		df = pd.read_csv(file_path)

		# Check if the necessary columns ('Medicine', 'Availability', 'Expiry Date') are present
		if not {'Medicine', 'Description', 'Availability', 'Expiry Date'}.issubset(df.columns):
			# If not, reset the file to include the required columns
			st.warning(f"File {file_path} does not contain the required columns. Resetting the file.")
			df = pd.DataFrame(columns=['Medicine', 'Description', 'Availability', 'Expiry Date'])
			df.to_csv(file_path, index=False)  # Save the default DataFrame to the file
			return df

		# If the CSV has valid data but possibly malformed, ensure 'Expiry Date' is datetime
		df['Expiry Date'] = pd.to_datetime(df['Expiry Date'], errors='coerce')

	except pd.errors.EmptyDataError:
		# Handle the case where the file is empty or malformed
		st.warning(f"File {file_path} is empty or malformed. Returning an empty DataFrame.")
		df = pd.DataFrame(columns=['Medicine', 'Description', 'Availability', 'Expiry Date'])
		df.to_csv(file_path, index=False)  # Save the default DataFrame to the file
		return df

	return df

# Save Data
def save_data(df):
	df.to_csv('medicines.csv', index=False)

# Ensure Expired Medicines file exists
def ensure_expired_medicines_file():
	expired_file_path = 'Expired Medicines.csv'
	if not os.path.exists(expired_file_path):
		# Create the file with the required columns if it doesn't exist
		expired_df = pd.DataFrame(columns=['Medicine', 'Description', 'Availability', 'Expiry Date'])
		expired_df.to_csv(expired_file_path, index=False)

# Save expired medicines to the "Expired Medicines.csv" file
def save_expired_medicines(df):
	expired_medicines = df[df['Expiry Date'] < datetime.now()]

	if not expired_medicines.empty:
		expired_file_path = 'Expired Medicines.csv'

		# Ensure the expired medicines file exists


		# Append expired medicines to the file
		expired_medicines.to_csv(expired_file_path, mode='a', header=False, index=False,
		                         columns=['Medicine', 'Description','Availability', 'Expiry Date'])

	return expired_medicines

# Remove expired medicines from the main dataset
def remove_expired():
	# Load the existing data from the CSV file
	df = load_data()

	# Identify expired medicines
	expired_medicines = df[df['Expiry Date'] < datetime.now()]

	if not expired_medicines.empty:
		# Filter out expired medicines
		new_dataset = df[df['Expiry Date'] >= datetime.now()]

		ensure_expired_medicines_file()
		# Save the updated dataset (without expired medicines) to the CSV file
		save_data(new_dataset)

		# Save expired medicines to the expired file (appending them)
		save_expired_medicines(df)

		st.success(f"Expired medicines moved to 'Expired Medicines.csv' and removed from main dataset.")
	else:
		st.info("No expired medicines found.")


# Add New Medicines
def add_new_medicines(medicine_name, Description, Availability, expiry_date):
	if not medicine_name or not expiry_date or not Availability:
		return load_data()

	try:
		expiry_date = pd.to_datetime(expiry_date, format='%Y-%m-%d')
	except ValueError:
		st.error("Invalid expiry date format. Please use YYYY-MM-DD format.")
		return load_data()

	new_entry = pd.DataFrame([{'Medicine': medicine_name, 'Description': Description , 'Availability': Availability, 'Expiry Date': expiry_date}])
	df = load_data()
	df = pd.concat([df, new_entry], ignore_index=True)
	return df

def get_all_expired_meds():
	try:
		df = pd.read_csv('Expired Medicines.csv')
	except FileNotFoundError:
		df = pd.DataFrame(columns=['Medicine', 'Description', 'Availability', 'Expiry Date'])

	return st.write(df)
# Streamlit UI
def main():

	st.title("Medicine Expiry Checker")

	# Add a medicine
	with st.form(key='add_medicine_form'):
		new_medicine = st.text_input('Enter medicine name:').lower()
		Description = st.text_input('Enter description:').lower()
		Availability = st.selectbox('Select True or False', options=['Yes', 'No'])
		expiry_date = st.date_input("Enter Expiry Date (YYYY-MM-DD):")
		submit_button = st.form_submit_button(label="Add Medicine")

		if submit_button:
			df = add_new_medicines(new_medicine, Description, Availability, expiry_date)
			save_data(df)
			st.success("Medicine added successfully!")

	# Display the medicines data
	if authenticate():
		st.subheader("Current Medicines Data")
		df = load_data()
		if not df.empty:
			st.write(df)
		else:
			st.warning("No medicines found.")

		# Check for expired medicines and remove them
		st.subheader("Currently Expired Medicines")
		expired_medicines = df[df['Expiry Date'] < datetime.now()]

		if not expired_medicines.empty:
			st.write(expired_medicines)
		# else:
		# 	st.info("No expired medicines found.")

		# Remove expired medicines from the main dataset
		remove_expired()
		st.subheader('List of Expired medicines')
		get_all_expired_meds()
	# 	Auto refresh every 10 seconds
	time.sleep(120)
	st.rerun()


if __name__ == '__main__':
	main()

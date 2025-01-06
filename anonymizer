import pandas as pd
import hashlib
from faker import Faker
import random
import string

# Initialize the Faker instance
faker = Faker()

# Function to hash a username
def hash_username(username):
    return hashlib.sha256(username.encode()).hexdigest()

# Function to generate a random password with only uppercase, lowercase, and digits
def generate_password(length=12):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))

# Function to anonymize the data from an input CSV file
def anonymize_csv(input_file, output_file, hash_file, domain):
    # Read the CSV input file
    df = pd.read_csv(input_file)

    # Ensure the required columns exist
    required_columns = ["Alias", "FirstName", "LastName", "Extension"]
    if not all(column in df.columns for column in required_columns):
        raise ValueError(f"Input CSV must contain the following columns: {required_columns}")

    # Create a mapping of hashed aliases to anonymized data
    hash_map = {}
    anonymized_data = []

    for _, row in df.iterrows():
        original_alias = row['Alias']
        first_name = row['FirstName']
        last_name = row['LastName']
        extension = row['Extension']

        # Hash the original alias
        alias_hash = hash_username(original_alias)

        # Generate anonymized name
        fake_first_name = faker.first_name()
        fake_last_name = faker.last_name()
        username = f"{fake_first_name.lower()}{fake_last_name.lower()}"
        email_address = f"{username}@{domain}"
        password = generate_password()

        # Preserve mapping in hash_map
        hash_map[alias_hash] = {
            "OriginalAlias": original_alias,
            "AnonymizedAlias": username,
            "FirstName": fake_first_name,
            "LastName": fake_last_name
        }

        # Append anonymized row data
        anonymized_data.append({
            "Username": username,
            "FirstName": fake_first_name,
            "LastName": fake_last_name,
            "Password": password,
            "EmailAddress": email_address,
            "ipPhone": extension
        })

    # Save hash map to a file for reference
    pd.DataFrame.from_dict(hash_map, orient='index').to_csv(hash_file)

    # Save anonymized data to a new CSV file
    anonymized_df = pd.DataFrame(anonymized_data)
    anonymized_df.to_csv(output_file, index=False)

# Function to generate random anonymized data
def generate_random_data(count, output_file, domain):
    anonymized_data = []
    for _ in range(count):
        fake_first_name = faker.first_name()
        fake_last_name = faker.last_name()
        username = f"{fake_first_name.lower()}{fake_last_name.lower()}"
        email_address = f"{username}@{domain}"
        extension = faker.random_number(digits=4, fix_len=True)
        password = generate_password()

        anonymized_data.append({
            "Username": username,
            "FirstName": fake_first_name,
            "LastName": fake_last_name,
            "Password": password,
            "EmailAddress": email_address,
            "ipPhone": extension
        })

    # Save anonymized data to a new CSV file
    anonymized_df = pd.DataFrame(anonymized_data)
    anonymized_df.to_csv(output_file, index=False)

# Main function to select mode
def main():
    print("Select mode:")
    print("1. Use input CSV file")
    print("2. Generate random anonymized data")
    choice = input("Enter your choice (1 or 2): ").strip()

    domain = input("Enter the domain for the email addresses (e.g., abc.inc): ").strip()

    if choice == "1":
        input_csv = input("Enter the path to the input CSV file: ").strip()
        anonymized_csv = input("Enter the path for the anonymized output CSV file: ").strip()
        hash_csv = input("Enter the path for the hash map CSV file: ").strip()
        anonymize_csv(input_csv, anonymized_csv, hash_csv, domain)
        print(f"Anonymized data saved to {anonymized_csv} and hash map saved to {hash_csv}.")
    elif choice == "2":
        count = int(input("How many random entries would you like to generate? ").strip())
        output_file = input("Enter the path for the anonymized output CSV file: ").strip()
        generate_random_data(count, output_file, domain)
        print(f"Random anonymized data saved to {output_file}.")
    else:
        print("Invalid choice. Please run the script again and select a valid option.")

if __name__ == "__main__":
    main()

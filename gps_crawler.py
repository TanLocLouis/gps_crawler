import requests
import time
import csv
import os
import hashlib
import configparser
import argparse
import getpass
from datetime import datetime
from dotenv import load_dotenv

base_url = "https://gps.toanthangjsc.vn/"
data_path = os.path.join(os.path.dirname(__file__), "data")

load_dotenv()
USER_NAME = os.getenv("USER_NAME")
PASSWORD = os.getenv("PASSWORD")
TRACKER_ID = os.getenv("TRACKER_ID")
VEH_ID = os.getenv("VEH_ID")
SERVER_IP = os.getenv("SERVER_IP")



# Function to hash the password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to store user credentials
def store_user_credentials(username, hashed_password):
    if not os.path.exists('users'):
        os.makedirs('users')
    user_file = os.path.join('users', f'{username}.conf')
    config = configparser.ConfigParser()
    config['User'] = {'username': username, 'password': hashed_password}
    with open(user_file, 'w') as configfile:
        config.write(configfile)

# Function to delete user credentials
def delete_user_credentials(username):
    user_file = os.path.join('users', f'{username}.conf')
    if os.path.exists(user_file):
        os.remove(user_file)
        print(f"User {username} deleted successfully.")
    else:
        print(f"User {username} does not exist.")

# Argument parser setup
parser = argparse.ArgumentParser(description='GPS Crawler')
parser.add_argument('--add', action='store_true', help='Add a new user')
parser.add_argument('--rm', action='store_true', help='Remove an existing user')

args = parser.parse_args()

if args.add:
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")
    hashed_password = hash_password(password)
    store_user_credentials(username, hashed_password)
    print("User created successfully.")
    exit()

if args.rm:
    username = input("Enter username to remove: ")
    delete_user_credentials(username)
    exit()



def dict_to_csv(data, output_file):
    """
    Convert a nested dictionary into a CSV file.
    
    Args:
        data (dict): The input dictionary to be converted.
        output_file (str): Path to the output CSV file.
    """
    # Flatten the dictionary for the 'd' key
    flat_data = data.get('d', {})
    
    # Open the CSV file for writing
    # Create folder if it does not exist
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    file_path = data_path + "/" + output_file
    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Write the headers (keys) only if the file is empty
        if file.tell() == 0:
            writer.writerow(flat_data.keys())
        
        # Write the values (values) to the CSV
        writer.writerow(flat_data.values())

def login():
    # Step 1: GET to get session ID
    # Define the headers for the request
    headers = {
        "Host": "gps.toanthangjsc.vn",
        "Sec-Ch-Ua": '" Not A;Brand";v="99", "Chromium";v="96"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "Linux",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9",
    }

    # Send the GET request without following redirects
    response = requests.get(base_url, headers=headers, allow_redirects=False)

    # Output the response details
    print("Status Code:", response.status_code)
    print("Headers:", response.headers)
    print("Cookies:", response.cookies.get_dict())
    print("Body:", response.text)
    session_cookie = response.cookies.get("ASP.NET_SessionId")
    print(f"Session ID: {session_cookie}")

    # Step 2: POST to login
    login_url = f"{base_url}/Login.aspx/CheckLogin"
    headers_post_login = {
        "Cookie": f"ASP.NET_SessionId={session_cookie}",
        "Sec-Ch-Ua": '" Not A;Brand";v="99", "Chromium";v="96"',
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/json; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Sec-Ch-Ua-Mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
        "Sec-Ch-Ua-Platform": "Linux",
        "Origin": base_url,
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": f"{base_url}/Domain/gps.toanthangjsc.vn/login.html?v=2.01.01",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9",
    }
    login_payload = {
        "Username": USER_NAME,
        "Password": PASSWORD,
        "Type": 0
    }

    login_response = requests.post(login_url, headers=headers_post_login, json=login_payload)
    if login_response.status_code == 200:
        print("Login successful.")
    else:
        print("Login failed.")
        exit()

    return session_cookie

def get_info(session_cookie):
    # Step 3: POST to get vehicle information
    vehicle_info_url = f"{base_url}/Default.aspx/VehicleStatus"
    headers_post_vehicle = {
        "Cookie": f"ASP.NET_SessionId={session_cookie}",
        "Sec-Ch-Ua": '" Not A;Brand";v="99", "Chromium";v="96"',
        "Accept": "*/*",
        "Content-Type": "application/json; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Sec-Ch-Ua-Mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
        "Sec-Ch-Ua-Platform": "Linux",
        "Origin": base_url,
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": f"{base_url}/Default1.aspx",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9",
    }
    vehicle_payload = {
        "TrackerID": TRACKER_ID,
        "VehID": VEH_ID,
        "Show_Output": 0,
        "OBD": 0,
        "VehicleType": "2169",
        "ServerIp": SERVER_IP 
    }

    vehicle_response = requests.post(vehicle_info_url, headers=headers_post_vehicle, json=vehicle_payload)
    if vehicle_response.status_code == 200:
        print("Vehicle information retrieved successfully.")
        data = vehicle_response.json()
        print(data)

        current_date = datetime.now()
        filename_date = current_date.strftime("%Y-%m-%d") + ".csv"
        data = dict_to_csv(data, filename_date)
    else:
        print("Failed to retrieve vehicle information.")

def main():
    # Login to the website to get the session cookie
    # This cookie will expire after 20 mins of inactivity
    session_cookie = login()

    # Continuously get vehicle information every 10 seconds
    while True:
        get_info(session_cookie)
        time.sleep(10)

if __name__ == "__main__":
    main()
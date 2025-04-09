
import requests
import json
import urllib3
from datetime import datetime

# Suppress SSL warnings (useful for self-signed certificates)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



# Define the correct base URI for API requests without v1
base_url = "https://vrni.shank.com/api/ni"
ldap_auth_url = f"{base_url}/auth/token"

############################
# CUSTOMER INPUT Values START
############################
# The query you want to run
query = {
    "query": "firewall rules where source ip = 1.2.3.4 and Source != any and Destination != any"
}
############################
# CUSTOMER INPUT Values END
############################

# LDAP authentication credentials
username = "ryan@shank.com"  #your username here
password = "P@ssw0rd123!"
auth_data = {
    "username": username,
    "password": password,
    "domain": {
        "domain_type": "LDAP",  # Your method here like AD or local
        "value": "shank.com"  # Your AD domain here
    }
}

auth_headers = {
    "Content-Type": "application/json"
}

# Step 1: Request Bearer Token using username, password, and domain (LDAP authentication)
try:
    print(f"Attempting to authenticate at URL: {ldap_auth_url}")
    auth_response = requests.post(ldap_auth_url, headers=auth_headers, json=auth_data, verify=False, timeout=30)

    # Check if the authentication was successful
    if auth_response.status_code == 200:
        try:
            response_json = auth_response.json()
            bearer_token = response_json.get("access_token") or response_json.get("token")

            if bearer_token:
                print(f"Bearer Token received: {bearer_token}")

                expiry_timestamp = response_json.get("expiry")
                if expiry_timestamp:
                    expiry_time = datetime.utcfromtimestamp(expiry_timestamp / 1000)
                    print(f"Token expires at: {expiry_time}")
                else:
                    print("No expiry time found in the token response.")
            else:
                print("No Bearer token found in the response.")
                exit(1)
        except ValueError as e:
            print(f"Failed to parse the JSON response: {e}")
            exit(1)
    else:
        print(f"Failed to authenticate: {auth_response.status_code}")
        print(f"Response content: {auth_response.text}")
        exit(1)
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
    exit(1)

# Step 2: Send the search query request
api_url = f"{base_url}/search/ql"  # Replace with your API endpoint for Aria Operations
headers = {
    "Authorization": f"NetworkInsight {bearer_token}",
    "Content-Type": "application/json"
}

try:
    print(f"Sending custom search query to URL: {api_url}")
    print(f"Request Headers: {json.dumps(headers, indent=2)}")  # Debug headers
    print(f"Request Body: {json.dumps(query, indent=2)}")  # Debug request body

    search_response = requests.post(api_url, headers=headers, json=query, verify=False, timeout=30)

    if search_response.status_code == 200:
        data = search_response.json()
        print(f"Search results: {json.dumps(data, indent=4)}")
    else:
        print(f"Failed to send search query: {search_response.status_code}")
        print(f"Response content: {search_response.text}")
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
    exit(1)

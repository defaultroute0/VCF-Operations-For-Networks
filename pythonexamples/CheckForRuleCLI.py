import requests
import json
import urllib3
from datetime import datetime
import argparse

# Suppress SSL warnings (useful for self-signed certificates)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Define the correct base URI for API requests without v1
base_url = "https://vrni.shank.com/api/ni"
ldap_auth_url = f"{base_url}/auth/token"

# Set up argparse to accept the query as a CLI parameter
parser = argparse.ArgumentParser(description="Query Aria Operations for Network firewall rules.")
parser.add_argument("query", type=str, help="Custom search query for firewall rules.")
args = parser.parse_args()

############################
# CUSTOMER INPUT Values START
############################
query = {
    "query": args.query  # Use the query passed in via the CLI
}
############################
# CUSTOMER INPUT Values END
############################

# LDAP authentication credentials
username = "ryan@shank.com"  # your username here
password = "XXXX!"  # your password here
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
print("Step 1: Authenticating with LDAP...")
try:
    auth_response = requests.post(ldap_auth_url, headers=auth_headers, json=auth_data, verify=False, timeout=30)

    # Check if the authentication was successful
    if auth_response.status_code == 200:
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
    else:
        print(f"Failed to authenticate: {auth_response.status_code}")
        print(f"Response content: {auth_response.text}")
        exit(1)
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
    exit(1)

# Step 2: Send the search query request
print("Step 2: Sending custom search query to Aria Operations API...")
api_url = f"{base_url}/search/ql"
headers = {
    "Authorization": f"NetworkInsight {bearer_token}",
    "Content-Type": "application/json"
}

try:
    search_response = requests.post(api_url, headers=headers, json=query, verify=False, timeout=30)

    if search_response.status_code == 200:
        data = search_response.json()

        # Debug: print the raw data returned
        print(f"Raw search results: {json.dumps(data, indent=4)}")

        # Check if the results contain entities
        if "entity_list_response" in data:
            results = data["entity_list_response"].get("results", [])

            # Step 3: Fetch rule details for each search result using firewall rule ID
            print("Step 3: Fetching rule details using firewall rule ID...")
            for rule in results:
                entity_id = rule.get("entity_id")

                # Ensure entity_id is available
                if not entity_id:
                    print(f"Skipping rule due to missing entity_id.")
                    continue

                print(f"Fetching details for rule with ID: {entity_id}")

                # Modify the URL to use the correct endpoint for fetching rule details
                rule_details_url = f"{base_url}/entities/firewall-rules/{entity_id}"
                print(f"Fetching details from URL: {rule_details_url}")  # Debug URL

                rule_details_response = requests.get(rule_details_url, headers=headers, verify=False, timeout=30)

                if rule_details_response.status_code == 200:
                    rule_details = rule_details_response.json()

                    # Extract details like rule name and hit count (assuming they are present in the response)
                    rule_name = rule_details.get("name", "Unknown")
                    hit_count = rule_details.get("hitCount", 0)

                    print(f"Rule ID: {entity_id}")
                    print(f"Rule Name: {rule_name}")
                    print(f"Hit Count: {hit_count}")
                    print("-" * 50)
                else:
                    # Provide more debugging info on failure
                    print(f"Failed to fetch details for rule with entity_id: {entity_id}")
                    print(f"Response: {rule_details_response.text}")
                    print(f"Error URL: {rule_details_url}")
        else:
            print("No valid results found.")
    else:
        print(f"Failed to send search query: {search_response.status_code}")
        print(f"Response content: {search_response.text}")
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
    exit(1)

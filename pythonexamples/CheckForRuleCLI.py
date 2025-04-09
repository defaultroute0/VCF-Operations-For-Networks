import requests
import json
import argparse
import urllib3
from datetime import datetime

# Suppress SSL warnings (useful for self-signed certificates)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Define the correct base URI for API requests without v1
base_url = "https://vrni.shank.com/api/ni"
ldap_auth_url = f"{base_url}/auth/token"

# Parse CLI arguments
parser = argparse.ArgumentParser(description='Query firewall rules from Aria Operations for Network.')
parser.add_argument('query', help='The base query for the firewall rules.')
parser.add_argument('--exclude-src-any', action='store_true', help='Exclude Source == any from the query.')
parser.add_argument('--exclude-dest-any', action='store_true', help='Exclude Destination == any from the query.')
parser.add_argument('--exclude-both-any', action='store_true', help='Exclude Source == any and Destination == any from the query.')

args = parser.parse_args()

# Customer input for LDAP authentication
username = "ryan@shank.com"  # Replace with your username
password = "XXXX"    # Replace with your password
auth_data = {
    "username": username,
    "password": password,
    "domain": {
        "domain_type": "LDAP",  # Your method here like AD or local
        "value": "shank.com"    # Your AD domain here
    }
}

auth_headers = {
    "Content-Type": "application/json"
}

# Step 1: Request Bearer Token using username, password, and domain (LDAP authentication)
try:
    print(f"Attempting to authenticate at URL: {ldap_auth_url}")
    auth_response = requests.post(ldap_auth_url, headers=auth_headers, json=auth_data, verify=False, timeout=30)

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

# Step 2: Construct the query based on CLI arguments
query = args.query

# Apply exclusions
if args.exclude_both_any:
    print("Excluding both Source != any and Destination != any from the query.")
    query += " and Source != any and Destination != any"
elif args.exclude_src_any:
    print("Excluding Source != any from the query.")
    query += " and Source != any"
elif args.exclude_dest_any:
    print("Excluding Destination != any from the query.")
    query += " and Destination != any"

# Display constructed query
print(f"This is what got sent as a QUERY: {query}")

# Step 3: Send the search query request
api_url = f"{base_url}/search/ql"  # Replace with your API endpoint for Aria Operations
headers = {
    "Authorization": f"NetworkInsight {bearer_token}",
    "Content-Type": "application/json"
}

search_data = {
    "query": query
}

try:
    print(f"Sending custom search query to URL: {api_url}")
    print(f"Request Headers: {json.dumps(headers, indent=2)}")
    print(f"Request Body: {json.dumps(search_data, indent=2)}")

    search_response = requests.post(api_url, headers=headers, json=search_data, verify=False, timeout=30)

    if search_response.status_code == 200:
        data = search_response.json()
        print(f"Search results returned: {data.get('search_response_total_hits', 0)} results.")

        if 'entity_list_response' in data and 'results' in data['entity_list_response']:
            results = data['entity_list_response']['results']
            if results:
                print("Rule ID | Rule Name | Hit Count")
                print("-" * 50)
                for rule in results:
                    rule_id = rule.get("entity_id")
                    # Fetch rule details using the rule entity ID
                    rule_details_url = f"{base_url}/entities/firewall-rules/{rule_id}"
                    rule_details_response = requests.get(rule_details_url, headers=headers, verify=False, timeout=30)
                    if rule_details_response.status_code == 200:
                        rule_details = rule_details_response.json()
                        rule_name = rule_details.get("name", "Unknown")
                        hit_count = rule_details.get("hit_count", "N/A")
                        print(f"{rule_id} | {rule_name} | {hit_count}")
                    else:
                        print(f"Failed to fetch details for rule ID {rule_id}: {rule_details_response.status_code}")
            else:
                print("No firewall rules found.")
        else:
            print("No results found in the search response.")

    else:
        print(f"Failed to send search query: {search_response.status_code}")
        print(f"Response content: {search_response.text}")

except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
    exit(1)

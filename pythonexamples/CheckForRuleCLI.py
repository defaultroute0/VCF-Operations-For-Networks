import argparse
import requests
import json
from datetime import datetime

# Suppress SSL warnings (useful for self-signed certificates)
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Define the correct base URI for API requests without v1
base_url = "https://vrni.shank.com/api/ni"
ldap_auth_url = f"{base_url}/auth/token"

# LDAP authentication credentials
username = "ryan@shank.com"  # your username here
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

def get_bearer_token():
    try:
        print(f"Attempting to authenticate at URL: {ldap_auth_url}")
        auth_response = requests.post(ldap_auth_url, headers=auth_headers, json=auth_data, verify=False, timeout=30)

        if auth_response.status_code == 200:
            response_json = auth_response.json()
            bearer_token = response_json.get("access_token") or response_json.get("token")
            if bearer_token:
                print(f"Bearer Token received: {bearer_token}")
                return bearer_token
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

def construct_query(base_query, exclude_source_any, exclude_destination_any):
    # Default action: Add "Source != any" and "Destination != any" if no exclusions are provided
    if not exclude_source_any and not exclude_destination_any:
        print("No specific exclusions provided. Using default filters: 'and Source != any and Destination != any'.")
        base_query += " and Source != any and Destination != any"
    else:
        if exclude_source_any:
            print("Excluding 'any' from the Source field.")
            base_query += " and Source != any"
        if exclude_destination_any:
            print("Excluding 'any' from the Destination field.")
            base_query += " and Destination != any"
    return base_query

def fetch_rule_details(bearer_token, entity_id):
    api_url = f"{base_url}/entities/firewall-rules/{entity_id}"
    headers = {
        "Authorization": f"NetworkInsight {bearer_token}",
        "Content-Type": "application/json"
    }

    try:
        print(f"Fetching details for rule with entity_id: {entity_id}...")
        response = requests.get(api_url, headers=headers, verify=False, timeout=30)
        if response.status_code == 200:
            data = response.json()
            rule_name = data.get("name", "Unknown")
            hit_count = data.get("hitCount", "Unknown")
            print(f"Rule ID: {entity_id}, Rule Name: {rule_name}, Hit Count: {hit_count}")
        else:
            print(f"Failed to fetch details for rule with entity_id: {entity_id}")
            print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

def main():
    # Command-line argument parsing
    parser = argparse.ArgumentParser(description="Query firewall rules from the API.")
    parser.add_argument("query", help="The firewall query to run (e.g. 'firewall rules where source ip = 1.2.3.4')")
    parser.add_argument("--exclude-source-any", action="store_true", help="Exclude 'any' from the Source field")
    parser.add_argument("--exclude-destination-any", action="store_true", help="Exclude 'any' from the Destination field")
    args = parser.parse_args()

    # Step 1: Get Bearer Token
    bearer_token = get_bearer_token()

    # Step 2: Construct the search query based on user input
    query = construct_query(args.query, args.exclude_source_any, args.exclude_destination_any)

    # Step 3: Send the search query
    search_url = f"{base_url}/search/ql"
    headers = {
        "Authorization": f"NetworkInsight {bearer_token}",
        "Content-Type": "application/json"
    }
    data = {
        "query": query
    }

    try:
        print(f"Sending custom search query to URL: {search_url}")
        search_response = requests.post(search_url, headers=headers, json=data, verify=False, timeout=30)

        if search_response.status_code == 200:
            search_results = search_response.json()
            print(f"Search results: {json.dumps(search_results, indent=4)}")

            # Step 4: Fetch rule details for each matching result
            for result in search_results.get("entity_list_response", {}).get("results", []):
                entity_id = result.get("entity_id")
                if entity_id:
                    fetch_rule_details(bearer_token, entity_id)
        else:
            print(f"Failed to send search query: {search_response.status_code}")
            print(f"Response content: {search_response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    main()

import requests
import json
import urllib3
import argparse
import re
from datetime import datetime

# Suppress SSL warnings (useful for self-signed certificates)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Define the correct base URI for API requests without v1
base_url = "https://vrni.shank.com/api/ni"

# Function to validate input variables
def validate_input(value):
    # Regular expression to check for valid characters (letters, digits, spaces, underscores, hyphens) as the UI does
    pattern = r"^[A-Za-z0-9\s\-_]+$"
    if not re.match(pattern, value):
        raise argparse.ArgumentTypeError(f"Invalid input: {value}. Only letters, numbers, spaces, hyphens, and underscores are allowed.")
    return value

# Step 1: Parse command-line arguments using argparse
parser = argparse.ArgumentParser(
    description="""Create application tier in VMware Aria Operation for Networks.\n
    
    Example usage:\n
    python create-app-tier.py "My-3Tier-App" "Tag = 'FIRECLOUD:MYAPP01' and NSX = 'nsx.region1.shank.com'" "tier-1"\n
    
    This script creates a new application tier with the specified name and matching criteria\n
    for virtual machines."""
)

# Define arguments with help descriptions
parser.add_argument("application_name", type=validate_input, help="The name of the application (new or existing).")
parser.add_argument("tier_match_criteria", type=validate_input, help="The filter criteria for VM search (e.g., 'Tag = FIRECLOUD:MYAPP01 and NSX = nsx.region1.shank.com').")
parser.add_argument("tier_name", type=validate_input, help="The name of the tier to be created.")

args = parser.parse_args()

# Get values from the parsed arguments
application_name = args.application_name
tier_match_criteria = args.tier_match_criteria
tier_name = args.tier_name

print(f"Application Name: {application_name}")
print(f"Tier Match Criteria: {tier_match_criteria}")
print(f"Tier Name: {tier_name}")

# Define the LDAP authentication URL and credentials
ldap_auth_url = f"{base_url}/auth/token"
username = "ryan@shank.com"
password = "XXXX"
auth_data = {
    "username": username,
    "password": password,
    "domain": {
        "domain_type": "LDAP",
        "value": "shank.com"
    }
}

auth_headers = {
    "Content-Type": "application/json"
}

# Step 2: Request Bearer Token using username, password, and domain (LDAP authentication)
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

# Step 3: Check if application already exists by name
applications_url = f"{base_url}/groups/applications"
try:
    response = requests.get(applications_url, headers={"Authorization": f"NetworkInsight {bearer_token}"},
                            verify=False, timeout=30)

    if response.status_code == 200:
        applications = response.json()
        application_id = None

        print(f"Applications response structure: {json.dumps(applications, indent=2)}")

        for app in applications:
            if isinstance(app, dict):  # Ensure we're dealing with a dictionary and not a string
                app_entity_id = app.get("entity_id")
                print(f"Checking application with entity_id: {app_entity_id}")

                app_details_url = f"{base_url}/groups/applications/{app_entity_id}"
                app_details_response = requests.get(app_details_url,
                                                    headers={"Authorization": f"NetworkInsight {bearer_token}"},
                                                    verify=False, timeout=30)

                if app_details_response.status_code == 200:
                    app_details = app_details_response.json()
                    app_name = app_details.get("name")
                    print(f"Application name: {app_name}")
                    if app_name == application_name:
                        application_id = app_entity_id
                        break

        if application_id:
            print(f"Application '{application_name}' exists with ID: {application_id}")
        else:
            print(f"Application '{application_name}' does not exist, creating it...")
            application_data = {"name": application_name}
            application_creation_response = requests.post(applications_url,
                                                          headers={"Authorization": f"NetworkInsight {bearer_token}"},
                                                          json=application_data, verify=False, timeout=30)

            if application_creation_response.status_code == 201:
                application_id = application_creation_response.json().get("entity_id")
                print(f"Application '{application_name}' created successfully with ID: {application_id}")
            else:
                print(f"Failed to create application: {application_creation_response.status_code}")
                print(f"Response content: {application_creation_response.text}")
                exit(1)

    else:
        print(f"Failed to retrieve applications: {response.status_code}")
        print(f"Response content: {response.text}")
        exit(1)

except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
    exit(1)

# Step 4: Create the application tier if application exists
if application_id:
    application_tiers_url = f"{base_url}/groups/applications/{application_id}/tiers"
    tier_data = {
        "name": tier_name,
        "source_group_entity_id": [application_id],
        "group_membership_criteria": [
            {
                "membership_type": "SearchMembershipCriteria",
                "search_membership_criteria": {
                    "entity_type": "VirtualMachine",
                    "filter": f"{tier_match_criteria}"  # Custom VM search filter injected correctly
                }
            }
        ]
    }

    tier_headers = {
        "Authorization": f"NetworkInsight {bearer_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Debugging: Print tier creation headers and data
    print(f"Creating tier under application with ID {application_id}")
    print(f"Request Headers for tier creation: {json.dumps(tier_headers, indent=2)}")
    print(f"Request Body for tier creation: {json.dumps(tier_data, indent=2)}")

    # Make the POST request to create the tier
    try:
        tier_creation_response = requests.post(application_tiers_url, headers=tier_headers,
                                               json=tier_data, verify=False, timeout=30)

        if tier_creation_response.status_code == 201:
            print(f"Tier '{tier_name}' created successfully!")
            print(tier_creation_response.json())  # Print the response if successful
        else:
            print(f"Failed to create tier: {tier_creation_response.status_code}")
            print(f"Response content: {tier_creation_response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

from optparse import Values

import requests
import json
import urllib3
from datetime import datetime

# Suppress SSL warnings (useful for self-signed certificates)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Define the correct base URI for API requests without v1
base_url = "https://vrni.shank.com/api/ni"

############################
#CUSTOMER INPUT Values START
############################
application_name = "My-3Tier-App6"  # Application name you're searching for, new or existing
tier_match_criteria = "Tag = 'FIRECLOUD:MYAPP01' and NSX = 'nsx.region1.shank.com'"  # Custom VM search filter

# Define the LDAP authentication URL and credentials
ldap_auth_url = f"{base_url}/auth/token"
username = "ryan@shank.com"
password = "XXXXXX"
auth_data = {
    "username": username,
    "password": password,
    "domain": {
        "domain_type": "LDAP",
        "value": "shank.com"
    }
}
############################
#CUSTOMER INPUT Values END
############################


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

# Step 2: Check if application already exists by name
applications_url = f"{base_url}/groups/applications"
try:
    response = requests.get(applications_url, headers={"Authorization": f"NetworkInsight {bearer_token}"},
                            verify=False, timeout=30)

    if response.status_code == 200:
        applications = response.json()
        application_id = None

        # Debugging: Print the structure of the applications data to understand the response
        print(f"Applications response structure: {json.dumps(applications, indent=2)}")

        # Now we need to get details for each application to match by name
        for app in applications:
            if isinstance(app, dict):  # Ensure we're dealing with a dictionary and not a string
                app_entity_id = app.get("entity_id")
                print(f"Checking application with entity_id: {app_entity_id}")

                # Fetch application details using the entity_id to get the name
                app_details_url = f"{base_url}/groups/applications/{app_entity_id}"
                app_details_response = requests.get(app_details_url,
                                                    headers={"Authorization": f"NetworkInsight {bearer_token}"},
                                                    verify=False, timeout=30)

                if app_details_response.status_code == 200:
                    app_details = app_details_response.json()
                    app_name = app_details.get("name")
                    print(f"Application name: {app_name}")
                    # Check if the name matches
                    if app_name == application_name:
                        application_id = app_entity_id
                        break

        # If the application ID is found, proceed to create the tier
        if application_id:
            print(f"Application '{application_name}' exists with ID: {application_id}")
        else:
            print(f"Application '{application_name}' does not exist, creating it...")
            # If application does not exist, create it
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

# Step 3: Create the application tier if application exists
if application_id:
    application_tiers_url = f"{base_url}/groups/applications/{application_id}/tiers"
    tier_data = {
        "name": "tier-1",
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
            print(f"Tier 'tier-1' created successfully!")
            print(tier_creation_response.json())  # Print the response if successful
        else:
            print(f"Failed to create tier: {tier_creation_response.status_code}")
            print(f"Response content: {tier_creation_response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

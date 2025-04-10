import requests
import json
import urllib3
import argparse
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# === Configuration ===
BASE_URL = "https://vrni.shank.com/api/ni"
AUTH_URL = f"{BASE_URL}/auth/token"
ENTITY_URL_TEMPLATE = f"{BASE_URL}/entities/firewall-rules/{{}}"
SEARCH_URL = f"{BASE_URL}/search/ql"
USERNAME = "ryan@shank.com"
PASSWORD = "XXX"
DOMAIN = "shank.com"

# === CLI Argument Parser ===
parser = argparse.ArgumentParser(description="Search firewall rules using search/ql.")
parser.add_argument("query", help="Query string (e.g., 'firewall rules where source ip = 1.2.3.4')")
parser.add_argument("--exclude-src-any", action="store_true", help="Exclude rules with 'any' in Source")
parser.add_argument("--exclude-dest-any", action="store_true", help="Exclude rules with 'any' in Destination")
parser.add_argument("--exclude-both-any", action="store_true", help="Exclude rules with 'any' in both Source and Destination")
args = parser.parse_args()

# === Step 1: Authentication ===
print(f"\n[Step 1] Authenticating at: {AUTH_URL}")
auth_payload = {
    "username": USERNAME,
    "password": PASSWORD,
    "domain": {
        "domain_type": "LDAP",
        "value": DOMAIN
    }
}
auth_headers = {"Content-Type": "application/json"}
auth_response = requests.post(AUTH_URL, headers=auth_headers, json=auth_payload, verify=False, timeout=30)

if auth_response.status_code != 200:
    print(f"[ERROR] Failed to authenticate: {auth_response.status_code} - {auth_response.text}")
    exit(1)

token_data = auth_response.json()
bearer_token = token_data.get("access_token") or token_data.get("token")
expiry_timestamp = token_data.get("expiry")
expiry_time = datetime.utcfromtimestamp(expiry_timestamp / 1000) if expiry_timestamp else "Unknown"
print(f"[SUCCESS] Token received: {bearer_token}")
print(f"[INFO] Token expires at: {expiry_time}\n")

# === Step 2: Build Query ===
query_string = args.query.strip()
if args.exclude_both_any:
    query_string += " and Source != any and Destination != any"
elif args.exclude_src_any:
    query_string += " and Source != any"
elif args.exclude_dest_any:
    query_string += " and Destination != any"

print(f"[Step 2] Sending search to: {SEARCH_URL}")
print(f"[DEBUG] This is what got sent as a QUERY:\n{{\n  \"query\": \"{query_string}\"\n}}\n")

search_payload = {"query": query_string}
search_headers = {
    "Authorization": f"NetworkInsight {bearer_token}",
    "Content-Type": "application/json"
}
search_response = requests.post(SEARCH_URL, headers=search_headers, json=search_payload, verify=False, timeout=30)

if search_response.status_code != 200:
    print(f"[ERROR] Failed to run query: {search_response.status_code} - {search_response.text}")
    exit(1)

search_data = search_response.json()
entity_results = search_data.get("entity_list_response", {}).get("results", [])

if not entity_results:
    print("[INFO] No matching firewall rules found.")
    exit(0)

print("[Step 3] Fetching rule details...\n")

# === Step 3: Display Table Header ===
print(f"{'AON Rule ID':<40} {'NSX Rule ID':<15} {'Rule Name':<40}")
print("-" * 95)

# === Step 4: Fetch Rule Details ===
for rule in entity_results:
    entity_id = rule.get("entity_id")
    if not entity_id:
        continue

    # Get detailed rule info from /entities/firewall-rules/{id}
    rule_url = ENTITY_URL_TEMPLATE.format(entity_id)
    rule_response = requests.get(rule_url, headers=search_headers, verify=False, timeout=30)

    if rule_response.status_code != 200:
        print(f"[DEBUG] Failed to fetch rule metadata for {entity_id}")
        print(f"{entity_id:<40} {'N/A':<15} {'N/A':<40}")
        continue

    rule_data = rule_response.json()
    rule_name = rule_data.get("name", "N/A")
    nsx_rule_id = rule_data.get("rule_id", "N/A")

    print(f"{entity_id:<40} {nsx_rule_id:<15} {rule_name:<40}")

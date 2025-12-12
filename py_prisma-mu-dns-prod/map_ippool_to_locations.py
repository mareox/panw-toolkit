#!/usr/bin/env python3
"""
Map ip-pool-groups to their location names
"""

import json
import yaml
import requests

# Get token
with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

client_id = config['api']['client_id']
client_secret = config['api']['client_secret']
tsg_id = config['api']['tsg_id']

auth_url = "https://auth.apps.paloaltonetworks.com/auth/v1/oauth2/access_token"
response = requests.post(
    auth_url,
    auth=(client_id, client_secret),
    data={
        'grant_type': 'client_credentials',
        'scope': f'tsg_id:{tsg_id} email profile'
    }
)

token = response.json()['access_token']

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

base_url = "https://api.sase.paloaltonetworks.com"

# Try to get mobile user settings/regions
endpoints_to_try = [
    "/sse/config/v1/mobile-agent-settings",
    "/sse/config/v1/mobile-users",
    "/sse/config/v1/bandwidth-allocations",
    "/sse/config/v1/mobile-user-ip-pool-allocations",
    "/sse/config/v1/mobile-agent/regions",
    "/sse/config/v1/mobile-agent/ip-pool",
]

print("Searching for IP Pool to Location mappings...")
print("=" * 100)
print()

for endpoint in endpoints_to_try:
    url = f"{base_url}{endpoint}"
    print(f"Testing: {endpoint}")

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ SUCCESS - Status: {response.status_code}")

            filename = f"api{endpoint.replace('/', '_')}.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)

            print(f"  Response saved to: {filename}")

            # Show structure
            if isinstance(data, list) and len(data) > 0:
                print(f"  Type: List with {len(data)} items")
                print(f"  First item: {json.dumps(data[0], indent=2)[:300]}")
            elif isinstance(data, dict):
                print(f"  Type: Dict")
                print(f"  Keys: {list(data.keys())}")
        else:
            print(f"  ✗ Failed - Status: {response.status_code}")
    except Exception as e:
        print(f"  ✗ Error: {str(e)[:100]}")

    print()

print("=" * 100)
print("\nCreating mapping file based on current DNS configuration...")
print()

# Get current DNS config to see the actual regions
dns_config = json.load(open('backup/current_dns_config.json'))
dns_servers = dns_config.get('dns_servers', [])

print("Current regions in your Mobile Users DNS configuration:")
print()

for idx, server in enumerate(dns_servers, 1):
    name = server.get('name')
    print(f"{idx:2d}. {name}")

print()
print("=" * 100)
print("MANUAL MAPPING REQUIRED")
print("=" * 100)
print()
print("To display friendly names like 'US-Eastern', 'US-Central', etc.,")
print("please create a file: config/region_mappings.yaml")
print()
print("Format:")
print("---")
print("region_names:")
print("  worldwide: Worldwide")
print("  emea: EMEA")
print("  apac: APAC")
print("  ip-pool-group-1: US-Eastern  # Example - check your console")
print("  ip-pool-group-2: US-Western  # Example - check your console")
print("  # ... add all your regions")
print()
print("You can find these names in Prisma Access console at:")
print("  Mobile Users > Infrastructure Settings > Client DNS")

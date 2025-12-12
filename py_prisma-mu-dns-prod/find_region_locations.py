#!/usr/bin/env python3
"""
Find region location mappings
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

# Try different endpoints that might have region/location info
endpoints = [
    "/sse/config/v1/locations",
    "/sse/config/v1/remote-networks",
    "/sse/config/v1/mobile-agent/locations",
    "/sse/config/v1/service-connections",
    "/mt/monitor/v1/agg/prisma-access/locations",
]

print("Searching for region location mappings...")
print("=" * 100)
print()

for endpoint in endpoints:
    url = f"{base_url}{endpoint}"
    print(f"Testing: {endpoint}")

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ SUCCESS - Status: {response.status_code}")

            filename = f"api_response{endpoint.replace('/', '_')}.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)

            print(f"  Response saved to: {filename}")

            # Show preview
            if isinstance(data, list):
                print(f"  Type: List with {len(data)} items")
                if data and len(data) > 0:
                    print(f"  First item keys: {list(data[0].keys())[:10]}")
            elif isinstance(data, dict):
                print(f"  Type: Dict")
                print(f"  Keys: {list(data.keys())[:10]}")
        else:
            print(f"  ✗ Failed - Status: {response.status_code}")
    except Exception as e:
        print(f"  ✗ Error: {str(e)[:100]}")

    print()

print("=" * 100)
print()
print("Let's also check the Panorama API for compute locations...")
print()

# Check compute locations in Panorama API
panorama_region = config['api']['panorama_region']
panorama_url = f"https://{panorama_region}.prod.panorama.paloaltonetworks.com/api/config/v9.2/configByPath"

pano_headers = {
    'x-auth-jwt': token,
    'Content-Type': 'application/json'
}

# Try to get mobile user compute locations
params = {
    'type': 'cloud',
    'folder': 'Mobile Users',
    'prefix': 'mobile-user-compute-location'
}

response = requests.get(panorama_url, params=params, headers=pano_headers, timeout=10)
print(f"Mobile User Compute Location: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    with open('panorama_compute_locations.json', 'w') as f:
        json.dump(data, f, indent=2)
    print(f"  Saved to: panorama_compute_locations.json")

print()
print("RECOMMENDATION:")
print("=" * 100)
print("Since the API doesn't provide friendly region names, we need to create a mapping.")
print("Please check your Prisma Access console and provide the friendly names for each region.")
print()
print("You can see these names in the Mobile Users > Infrastructure Settings > Client DNS page")
print("in the Prisma Access GUI.")

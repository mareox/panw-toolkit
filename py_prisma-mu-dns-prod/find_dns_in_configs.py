#!/usr/bin/env python3
"""
Find DNS configuration within the region configs
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
panorama_region = config['api']['panorama_region']

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
    'x-auth-jwt': token,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

base_url = f"https://{panorama_region}.prod.panorama.paloaltonetworks.com/api/config/v9.2/configByPath"

# Get the worldwide config
prefix = "global-protect/global-protect-portal/entry[@name='GlobalProtect_Portal']/client-config/configs/entry[@name='worldwide']"

params = {
    'type': 'cloud',
    'folder': 'Mobile Users',
    'prefix': prefix
}

print("=" * 80)
print("Fetching 'worldwide' region configuration...")
print("=" * 80)
print()

response = requests.get(base_url, params=params, headers=headers, timeout=10)

if response.status_code == 200:
    data = response.json()

    # Save the full response
    with open('worldwide_config.json', 'w') as f:
        json.dump(data, f, indent=2)

    print("Full config saved to: worldwide_config.json")
    print()

    # Try to find DNS-related keys
    def find_dns_keys(obj, path=""):
        """Recursively find keys containing 'dns', 'domain', or 'suffix'"""
        dns_paths = []

        if isinstance(obj, dict):
            for key, value in obj.items():
                if any(term in key.lower() for term in ['dns', 'domain', 'suffix']):
                    dns_paths.append((f"{path}.{key}", value))

                if isinstance(value, (dict, list)):
                    dns_paths.extend(find_dns_keys(value, f"{path}.{key}"))

        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                dns_paths.extend(find_dns_keys(item, f"{path}[{i}]"))

        return dns_paths

    dns_items = find_dns_keys(data)

    if dns_items:
        print("Found DNS-related configuration:")
        print("=" * 80)
        for path, value in dns_items:
            print(f"\nPath: {path}")
            print(f"Value: {json.dumps(value, indent=2)}")
            print("-" * 80)
    else:
        print("No DNS configuration found in this endpoint.")
        print()
        print("The configuration might be at a different level.")
        print("Response keys:", list(data.keys()))

else:
    print(f"Error: {response.status_code}")
    print(response.text[:500])

#!/usr/bin/env python3
"""
List all available configs/regions
"""

import json
import yaml
import requests
from src.panorama_utils import build_panorama_base_url

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

panorama_base = build_panorama_base_url(panorama_region)
base_url = f"{panorama_base}/api/config/v9.2/configByPath"

# Get all configs (parent level)
prefix = "global-protect/global-protect-portal/entry[@name='GlobalProtect_Portal']/client-config/configs"

params = {
    'type': 'cloud',
    'folder': 'Mobile Users',
    'prefix': prefix
}

print("=" * 80)
print("Fetching all client configs...")
print("=" * 80)
print()

response = requests.get(base_url, params=params, headers=headers, timeout=10)

if response.status_code == 200:
    data = response.json()

    # Save full response
    with open('all_configs.json', 'w') as f:
        json.dump(data, f, indent=2)

    print("Full config saved to: all_configs.json")
    print()

    # Extract and display config names
    try:
        configs = data.get('result', {}).get('configs', {}).get('entry', [])

        if configs:
            print(f"Found {len(configs)} configurations:")
            print("=" * 80)

            for cfg in configs:
                name = cfg.get('@name', 'N/A')
                print(f"\nConfig Name: {name}")

                # Check if DNS info exists
                if 'dns' in cfg:
                    print(f"  ✓ Has DNS configuration")
                    dns_data = cfg['dns']
                    print(f"  DNS Data: {json.dumps(dns_data, indent=4)}")
                else:
                    print(f"  ✗ No DNS configuration")

                # Show some key info
                print(f"  Location: {cfg.get('@loc', 'N/A')}")
                print(f"  Type: {cfg.get('@type', 'N/A')}")

        else:
            print("No configurations found.")

    except Exception as e:
        print(f"Error parsing: {e}")
        print("Response structure:")
        print(json.dumps(data, indent=2)[:1000])

else:
    print(f"Error: {response.status_code}")
    print(response.text[:500])

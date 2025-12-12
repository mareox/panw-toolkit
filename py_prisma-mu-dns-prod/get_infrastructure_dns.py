#!/usr/bin/env python3
"""
Get Infrastructure Settings including DNS
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

# Get infrastructure settings
prefix = "global-protect/global-protect-portal/entry[@name='GlobalProtect_Portal']/infrastructure-settings"

params = {
    'type': 'cloud',
    'folder': 'Mobile Users',
    'prefix': prefix
}

print("=" * 80)
print("Fetching Infrastructure Settings...")
print("=" * 80)
print()

response = requests.get(base_url, params=params, headers=headers, timeout=10)

if response.status_code == 200:
    data = response.json()

    # Save full response
    with open('infrastructure_settings.json', 'w') as f:
        json.dump(data, f, indent=2)

    print("Full config saved to: infrastructure_settings.json")
    print()

    print("Infrastructure Settings:")
    print("=" * 80)
    print(json.dumps(data, indent=2))

else:
    print(f"Error: {response.status_code}")
    print(response.text[:500])

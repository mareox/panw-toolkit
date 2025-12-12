#!/usr/bin/env python3
"""
Get region name mappings from Panorama API
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

# Get all configs which should have region display names
prefix = "global-protect/global-protect-portal/entry[@name='GlobalProtect_Portal']/client-config/configs"

params = {
    'type': 'cloud',
    'folder': 'Mobile Users',
    'prefix': prefix
}

print("Fetching client configs from Panorama API...")
print()

response = requests.get(base_url, params=params, headers=headers, timeout=30)

if response.status_code == 200:
    data = response.json()

    # Save full response
    with open('panorama_configs_full.json', 'w') as f:
        json.dump(data, f, indent=2)

    print("Full response saved to: panorama_configs_full.json")
    print()

    # Extract configs
    configs = data.get('result', {}).get('configs', {}).get('entry', [])

    if configs:
        print(f"Found {len(configs)} client configurations:")
        print("=" * 100)
        print()

        for cfg in configs:
            name = cfg.get('@name', 'N/A')
            print(f"Config Name: {name}")

            # Look for gateways which might have region info
            gateways = cfg.get('gateways', {})
            external = gateways.get('external', {})

            if external:
                print(f"  Gateway info found")

            print()
    else:
        print("No client configurations found")

else:
    print(f"Error: {response.status_code}")
    print(response.text[:1000])

print()
print("=" * 100)
print("Checking SCM API for region metadata...")
print("=" * 100)
print()

# Try SCM API mobile-agent settings which includes region info
scm_url = "https://api.sase.paloaltonetworks.com/sse/config/v1/mobile-agent/infrastructure-settings"
scm_headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

response = requests.get(scm_url, headers=scm_headers, timeout=30)

if response.status_code == 200:
    data = response.json()

    # Save response
    with open('scm_infrastructure_full.json', 'w') as f:
        json.dump(data, f, indent=2)

    print("SCM infrastructure settings saved to: scm_infrastructure_full.json")
    print()

    if isinstance(data, list) and len(data) > 0:
        config = data[0]
        dns_servers = config.get('dns_servers', [])

        print("Checking dns_servers for display names...")
        print()

        for server in dns_servers[:3]:  # Show first 3 as example
            print(f"Region: {server.get('name')}")
            print(f"  Keys: {list(server.keys())}")

            # Check for any display/label fields
            for key, value in server.items():
                if 'display' in key.lower() or 'label' in key.lower() or 'friendly' in key.lower():
                    print(f"  {key}: {value}")
            print()
else:
    print(f"SCM API Error: {response.status_code}")
    print(response.text[:500])

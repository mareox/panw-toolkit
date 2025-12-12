#!/usr/bin/env python3
"""
Test Panorama Cloud API for Mobile Users DNS Configuration

Based on discovered URL pattern from user
"""

import json
import yaml
import requests
from urllib.parse import quote

GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

print("=" * 80)
print("Testing Panorama Cloud API - Mobile Users DNS Configuration")
print("=" * 80)
print()

# Get token
print("[1/3] Getting token...")
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
print(f"{GREEN}✓ Token obtained{RESET}")
print()

# Try both header formats - browser uses x-auth-jwt for Panorama
headers_standard = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

headers_panorama = {
    'x-auth-jwt': token,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# Start with Panorama-style headers
headers = headers_panorama

# Base URL using panorama region from config
base_url = f"https://{panorama_region}.prod.panorama.paloaltonetworks.com/api/config/v9.2/configByPath"

# Test different prefix paths for DNS configuration
prefixes = [
    # User-provided working endpoint
    "global-protect/global-protect-portal/entry[@name='GlobalProtect_Portal']/client-config/root-ca",

    # DNS-related paths
    "global-protect/global-protect-portal/entry[@name='GlobalProtect_Portal']/client-config/configs",
    "global-protect/global-protect-portal/entry[@name='GlobalProtect_Portal']/client-config/configs/entry[@name='worldwide']",
    "global-protect/global-protect-portal/entry[@name='GlobalProtect_Portal']/client-config/configs/entry[@name='worldwide']/dns",
    "global-protect/global-protect-portal/entry[@name='GlobalProtect_Portal']/client-config/configs/entry[@name='North america']",
    "global-protect/global-protect-portal/entry[@name='GlobalProtect_Portal']/client-config/configs/entry[@name='US-Western']",

    # Infrastructure settings
    "global-protect/global-protect-portal/entry[@name='GlobalProtect_Portal']/infrastructure-settings",
    "global-protect/global-protect-portal/entry[@name='GlobalProtect_Portal']/infrastructure-settings/dns",

    # Client config variations
    "global-protect/global-protect-portal/entry[@name='GlobalProtect_Portal']/client-config",
    "global-protect/global-protect-portal/entry[@name='GlobalProtect_Portal']/client-config/dns-settings",

    # Try without specific portal name
    "global-protect/global-protect-portal/client-config/configs",

    # Mobile Users specific
    "mobile-users/infrastructure-settings",
    "mobile-users/client-dns",
]

print(f"[2/3] Testing {len(prefixes)} endpoint variations...")
print()

results = {
    'successful': [],
    'errors': []
}

for i, prefix in enumerate(prefixes, 1):
    # Build full URL
    params = {
        'type': 'cloud',
        'folder': 'Mobile Users',
        'prefix': prefix
    }

    print(f"{BLUE}[{i}/{len(prefixes)}]{RESET} Testing prefix: {prefix[:60]}...", end='', flush=True)

    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=10)

        result = {
            'prefix': prefix,
            'status_code': response.status_code,
            'url': response.url
        }

        if response.status_code == 200:
            try:
                data = response.json()
                result['data'] = data
                result['success'] = True
                results['successful'].append(result)

                print(f"\r{GREEN}✓ SUCCESS:{RESET} {prefix[:60]}")

                # Show preview
                if data:
                    print(f"   Response keys: {list(data.keys())[:5] if isinstance(data, dict) else 'Not a dict'}")

            except:
                result['text'] = response.text[:200]
                results['successful'].append(result)
                print(f"\r{GREEN}✓ SUCCESS (non-JSON):{RESET} {prefix[:60]}")
        else:
            result['error'] = response.text[:200]
            results['errors'].append(result)
            print(f"\r{RED}✗{RESET} {response.status_code}: {prefix[:60]}")

    except Exception as e:
        result = {
            'prefix': prefix,
            'error': str(e)
        }
        results['errors'].append(result)
        print(f"\r{RED}✗ ERROR:{RESET} {prefix[:60]}")

print()
print(f"{GREEN}✓ Testing complete{RESET}")
print()

# Display results
print("[3/3] Results")
print("=" * 80)
print()

if results['successful']:
    print(f"{GREEN}✓ FOUND {len(results['successful'])} WORKING ENDPOINTS:{RESET}")
    print("-" * 80)
    print()

    for result in results['successful']:
        print(f"{GREEN}✓{RESET} Prefix: {result['prefix']}")
        print(f"  URL: {result['url']}")
        print(f"  Status: {result['status_code']}")

        if 'data' in result:
            data = result['data']
            print(f"  Response type: {type(data).__name__}")

            if isinstance(data, dict):
                print(f"  Keys: {list(data.keys())}")

                # Show sample for DNS-related data
                data_str = json.dumps(data)
                if 'dns' in data_str.lower() or 'domain' in data_str.lower():
                    print(f"\n  {YELLOW}⭐ Contains DNS/Domain data!{RESET}")
                    print(f"  Sample: {json.dumps(data, indent=4)[:500]}")

            elif isinstance(data, list):
                print(f"  Items: {len(data)}")
                if data:
                    print(f"  First item type: {type(data[0]).__name__}")

        print()

    # Save results
    output_file = "panorama_api_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"{GREEN}✓ Detailed results saved to: {output_file}{RESET}")
    print()

else:
    print(f"{YELLOW}No successful endpoints found with these prefixes.{RESET}")
    print()
    print("The DNS configuration might be under a different path.")
    print()
    print("NEXT STEPS:")
    print("1. Go back to the Network tab in your browser")
    print("2. Look for OTHER API calls (not just the root-ca one)")
    print("3. Specifically look for calls made when you:")
    print("   - Click on 'worldwide' region")
    print("   - Click on 'North america' region")
    print("   - View or edit DNS settings")
    print()

print("=" * 80)
print("WHAT TO DO NEXT")
print("=" * 80)
print()

if results['successful']:
    print("Great! Found working endpoints.")
    print()
    print("Review the responses above to find which one contains:")
    print("  - DNS suffix/domain lists")
    print("  - Internal domain configuration")
    print("  - Public DNS settings")
    print()
    print("That's the endpoint we need!")
else:
    print("In the browser Network tab, look for API calls that:")
    print("  1. Are triggered when you click 'worldwide' or other regions")
    print("  2. Have 'configs' or 'dns' or 'infrastructure' in the URL")
    print("  3. Return JSON with domain/DNS configuration")
    print()
    print("Copy those URLs here, and I'll test them!")

print()

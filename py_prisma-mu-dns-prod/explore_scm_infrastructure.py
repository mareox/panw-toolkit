#!/usr/bin/env python3
"""
Strata Cloud Manager - Mobile Users Infrastructure Settings Explorer

Specifically targets the Client DNS configuration for regions:
- worldwide
- North america
- US-Western
"""

import json
import yaml
import requests
from datetime import datetime

GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'

print("=" * 80)
print("Strata Cloud Manager - Mobile Users Client DNS Configuration Explorer")
print("=" * 80)
print()

# Get token
print("[1/4] Authenticating...")
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

if response.status_code != 200:
    print(f"{RED}✗ Authentication failed{RESET}")
    exit(1)

token = response.json()['access_token']
print(f"{GREEN}✓ Token obtained{RESET}")
print()

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# SCM/SSE base URL
base_url = "https://api.sase.paloaltonetworks.com/sse/config/v1"

# Possible folder names
folders = [
    "Mobile Users",
    "Mobile Users - GP",
    "GlobalProtect",
    "All",
    "Shared",
]

# Possible location/region names based on what you saw in UI
regions = [
    "worldwide",
    "North america",
    "US-Western",
    "north-america",
    "us-western",
    "global",
    "Americas",
]

# SCM Infrastructure Settings endpoints
endpoints_to_test = []

# Try infrastructure-settings with different params
base_endpoints = [
    "/infrastructure-settings",
    "/mobile-users-infrastructure-settings",
    "/mobile-users/infrastructure-settings",
    "/mobile-users-globalprotect/infrastructure-settings",
    "/infrastructure/settings",
]

# Add base endpoints
endpoints_to_test.extend(base_endpoints)

# Try with folder parameter
for folder in folders:
    for endpoint in base_endpoints:
        endpoints_to_test.append(f"{endpoint}?folder={folder}")

# Try with location parameter
for location in regions:
    for endpoint in base_endpoints:
        endpoints_to_test.append(f"{endpoint}?location={location}")

# Try with both folder and location
for folder in folders[:2]:  # Just try first 2 folders
    for location in regions[:3]:  # Just try first 3 locations
        endpoints_to_test.append(f"/infrastructure-settings?folder={folder}&location={location}")

print(f"[2/4] Testing {len(endpoints_to_test)} SCM endpoint variations...")
print()

results = {
    'successful': [],
    'client_dns_found': [],
    'not_found': [],
    'errors': []
}

for i, endpoint in enumerate(endpoints_to_test, 1):
    url = f"{base_url}{endpoint}"

    print(f"\r{BLUE}[{i}/{len(endpoints_to_test)}]{RESET} {endpoint[:65]}...", end='', flush=True)

    try:
        response = requests.get(url, headers=headers, timeout=5)

        result = {
            'endpoint': endpoint,
            'url': url,
            'status_code': response.status_code
        }

        if response.status_code == 200:
            try:
                data = response.json()
                result['data'] = data
                result['success'] = True

                # Check if this looks like Client DNS config
                data_str = json.dumps(data).lower()
                result['has_dns'] = 'dns' in data_str
                result['has_client_dns'] = 'client' in data_str and 'dns' in data_str
                result['has_domains'] = 'domain' in data_str
                result['has_regions'] = any(r.lower() in data_str for r in regions)

                # Analyze structure
                if isinstance(data, dict):
                    result['keys'] = list(data.keys())

                    # Look for data array (common SCM pattern)
                    if 'data' in data and isinstance(data['data'], list):
                        result['item_count'] = len(data['data'])
                        if data['data']:
                            result['first_item_keys'] = list(data['data'][0].keys()) if isinstance(data['data'][0], dict) else None

                results['successful'].append(result)

                # Mark as high value if it has client DNS indicators
                if result['has_client_dns'] or (result['has_dns'] and result['has_domains']):
                    results['client_dns_found'].append(result)

            except:
                result['raw_response'] = response.text[:200]
                results['successful'].append(result)

        elif response.status_code == 404:
            results['not_found'].append(result)
        else:
            result['response'] = response.text[:200]
            results['errors'].append(result)

    except Exception as e:
        pass  # Skip errors for cleaner output

print("\r" + " " * 100 + "\r", end='')
print(f"{GREEN}✓ Testing complete{RESET}")
print()

# Display results
print("[3/4] Results")
print("=" * 80)
print()

if results['client_dns_found']:
    print(f"{GREEN}⭐ FOUND ENDPOINTS WITH CLIENT DNS DATA ({len(results['client_dns_found'])}):{RESET}")
    print("=" * 80)

    for result in results['client_dns_found']:
        print(f"\n{CYAN}✓✓ {result['endpoint']}{RESET}")
        print(f"   URL: {result['url']}")
        print(f"   Status: {result['status_code']}")

        if 'keys' in result:
            print(f"   Response Keys: {result['keys']}")

        if 'item_count' in result:
            print(f"   Items: {result['item_count']}")

        if 'first_item_keys' in result and result['first_item_keys']:
            print(f"   Item Keys: {result['first_item_keys'][:10]}")

        # Show sample data
        data = result.get('data', {})
        if isinstance(data, dict) and 'data' in data and isinstance(data['data'], list) and data['data']:
            print(f"\n   {YELLOW}Sample Configuration:{RESET}")
            first_item = data['data'][0]
            print(f"   {json.dumps(first_item, indent=6)[:800]}")

        print()

elif results['successful']:
    print(f"{GREEN}✓ FOUND WORKING ENDPOINTS ({len(results['successful'])}):{RESET}")
    print("-" * 80)

    for result in results['successful'][:10]:  # Show first 10
        print(f"\n{GREEN}✓{RESET} {result['endpoint']}")
        print(f"   Status: {result['status_code']}")

        if 'keys' in result:
            print(f"   Keys: {result['keys'][:5]}")

        if result.get('has_dns'):
            print(f"   {YELLOW}Contains DNS data{RESET}")

        if result.get('has_regions'):
            print(f"   {YELLOW}Contains region data{RESET}")

    print()

else:
    print(f"{RED}✗ No working endpoints found{RESET}")
    print()

# Save detailed results
output_file = f"scm_infrastructure_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

print(f"[4/4] Saving detailed results to {output_file}...")

with open(output_file, 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"{GREEN}✓ Saved{RESET}")
print()

# Recommendations
print("=" * 80)
print("NEXT STEPS")
print("=" * 80)
print()

if results['client_dns_found']:
    print(f"{GREEN}SUCCESS! Found Client DNS configuration endpoints!{RESET}")
    print()
    print("The endpoints above contain Client DNS data.")
    print()
    print("To proceed:")
    print("1. Review the sample configuration above")
    print("2. Note the structure for regions (worldwide, North america, US-Western)")
    print("3. Test updating one region with your domains from CSV")
    print("4. Update src/dns_config.py with the correct endpoint")
    print()
    print("Test with curl:")
    best_endpoint = results['client_dns_found'][0]['url']
    print(f"export PRISMA_TOKEN='your-token'")
    print(f"curl -H 'Authorization: Bearer $PRISMA_TOKEN' \\")
    print(f"     '{best_endpoint}'")

elif results['successful']:
    print(f"{YELLOW}Found working endpoints, but no clear Client DNS config yet.{RESET}")
    print()
    print(f"Review {output_file} for details.")
    print()
    print("The Client DNS config might be:")
    print("  - Under a specific region/location parameter")
    print("  - Part of a larger infrastructure object")
    print("  - Require the exact folder name from SCM")
    print()
    print("TRY:")
    print("1. Use Browser DevTools on SCM (F12)")
    print("2. Navigate to the Client DNS page")
    print("3. Capture the exact API call when viewing 'worldwide' config")

else:
    print(f"{RED}No endpoints responded successfully.{RESET}")
    print()
    print("This likely means:")
    print("  - SCM uses a different API structure")
    print("  - Need exact folder/location names")
    print("  - Browser DevTools is the best approach")
    print()
    print("ACTION REQUIRED:")
    print("1. Open https://stratacloudmanager.paloaltonetworks.com/")
    print("2. Press F12 → Network tab")
    print("3. Navigate to: workflows/mobile-users-gp/setup/infrastructure-settings")
    print("4. Click on 'worldwide' or any region")
    print("5. Find the API call in Network tab")
    print("6. Copy the endpoint URL")

print()
print("=" * 80)

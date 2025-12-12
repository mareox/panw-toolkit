#!/usr/bin/env python3
"""
Prisma SASE Mobile Users API Explorer

Specifically searches for Mobile Users CLIENT DNS configuration endpoints
(not infrastructure DNS)
"""

import json
import yaml
import requests
from datetime import datetime

GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

print("=" * 80)
print("Mobile Users Client DNS Configuration - API Explorer")
print("=" * 80)
print()

# Get token
print("[1/3] Getting authentication token...")
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

# Extended list of Mobile Users specific endpoints
mobile_users_endpoints = [
    # SCM/SSE endpoints
    "/sse/config/v1/mobile-users",
    "/sse/config/v1/mobile-users/onboarding",
    "/sse/config/v1/mobile-users/dns-config",
    "/sse/config/v1/mobile-users/client-dns",
    "/sse/config/v1/mobile-users/infrastructure-settings",
    "/sse/config/v1/mobile-users-globalprotect",
    "/sse/config/v1/mobile-users-globalprotect/dns",
    "/sse/config/v1/mobile-users-globalprotect/infrastructure",

    # GlobalProtect specific
    "/sse/config/v1/global-protect",
    "/sse/config/v1/global-protect/dns",
    "/sse/config/v1/global-protect/settings",
    "/sse/config/v1/global-protect/infrastructure-settings",

    # Portal/Gateway configs
    "/sse/config/v1/global-protect-portal",
    "/sse/config/v1/global-protect-portal-configs",
    "/sse/config/v1/global-protect-gateway",
    "/sse/config/v1/global-protect-gateway-configs",

    # Infrastructure
    "/sse/config/v1/infrastructure-settings",
    "/sse/config/v1/mobile-users-infrastructure-settings",

    # Configuration objects
    "/sse/config/v1/configuration",
    "/sse/config/v1/configurations",
    "/sse/config/v1/dns-configurations",

    # MT endpoints (alternative)
    "/mt/config/v1/mobile-users",
    "/mt/config/v1/global-protect",
    "/mt/config/v1/infrastructure-settings",

    # Explicit Proxy (alternative deployment)
    "/sse/config/v1/mobile-users-explicit-proxy/infrastructure-settings",

    # Onboarding/Client settings
    "/sse/config/v1/onboarding",
    "/sse/config/v1/onboarding/mobile-users",
    "/sse/config/v1/client-settings",
]

# Also try with folder/id structure
folder_id = "Mobile Users"  # Common folder name
additional_endpoints = []
for endpoint in mobile_users_endpoints[:10]:  # Try first 10 with folder param
    additional_endpoints.append(f"{endpoint}?folder={folder_id}")

all_endpoints = mobile_users_endpoints + additional_endpoints

print("[2/3] Testing Mobile Users specific endpoints...")
print(f"Testing {len(all_endpoints)} endpoints...")
print()

results = {
    'successful': [],
    'not_found': [],
    'unauthorized': [],
    'errors': []
}

for i, endpoint in enumerate(all_endpoints, 1):
    url = f"https://api.sase.paloaltonetworks.com{endpoint}"

    print(f"\r{BLUE}[{i}/{len(all_endpoints)}]{RESET} Testing: {endpoint[:60]}...", end='', flush=True)

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

                # Analyze the response
                if isinstance(data, dict):
                    result['keys'] = list(data.keys())
                    result['has_dns'] = any('dns' in str(k).lower() for k in data.keys())

                    # Check for nested DNS config
                    for key, value in data.items():
                        if isinstance(value, dict) and 'dns' in str(key).lower():
                            result['dns_key'] = key
                            result['dns_config'] = value

                results['successful'].append(result)

            except:
                result['raw_response'] = response.text[:200]
                results['successful'].append(result)

        elif response.status_code == 404:
            results['not_found'].append(result)
        elif response.status_code in [401, 403]:
            results['unauthorized'].append(result)
        else:
            result['response'] = response.text[:200]
            results['errors'].append(result)

    except Exception as e:
        result = {
            'endpoint': endpoint,
            'url': url,
            'error': str(e)
        }
        results['errors'].append(result)

print("\r" + " " * 100 + "\r", end='')
print(f"{GREEN}✓ Testing complete{RESET}")
print()

# Display results
print("[3/3] Results")
print("=" * 80)
print()

if results['successful']:
    print(f"{GREEN}✓ FOUND {len(results['successful'])} WORKING ENDPOINTS:{RESET}")
    print("-" * 80)

    for result in results['successful']:
        print(f"\n{GREEN}✓{RESET} {result['endpoint']}")
        print(f"   URL: {result['url']}")
        print(f"   Status: {result['status_code']}")

        if 'keys' in result:
            print(f"   Response Keys: {result['keys'][:5]}")

        if 'has_dns' in result and result['has_dns']:
            print(f"   {YELLOW}⭐ Contains DNS-related data!{RESET}")

        if 'dns_config' in result:
            print(f"   {YELLOW}⭐⭐ Found DNS configuration:{RESET}")
            print(f"   {json.dumps(result['dns_config'], indent=6)[:300]}")

        # Show sample data
        if 'data' in result and isinstance(result['data'], dict):
            data = result['data']

            # Look for interesting fields
            interesting_keys = ['dns', 'domain', 'client', 'settings', 'infrastructure']
            found_keys = [k for k in data.keys() if any(x in str(k).lower() for x in interesting_keys)]

            if found_keys:
                print(f"   {YELLOW}Interesting keys:{RESET} {found_keys}")

    print()

    # Save detailed results
    output_file = f"mobile_users_api_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"{GREEN}✓ Detailed results saved to: {output_file}{RESET}")
    print()

    # Recommendations
    print("=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print()

    if any(r.get('has_dns') for r in results['successful']):
        print(f"{GREEN}Found endpoints with DNS configuration!{RESET}")
        print()
        print("Next steps:")
        print("1. Review the DNS configuration in the output above")
        print("2. Test updating configuration with a PUT/POST request")
        print("3. Update src/dns_config.py with the correct endpoint")
    else:
        print(f"{YELLOW}No DNS-specific configuration found in these endpoints.{RESET}")
        print()
        print("The Mobile Users CLIENT DNS config might be:")
        print("  - Under a different endpoint structure")
        print("  - Part of a larger configuration object")
        print("  - Requires specific folder/container parameters")
        print()
        print("TRY NEXT:")
        print("1. Check Prisma Access UI with Browser DevTools (F12)")
        print("2. Navigate to: Workflows → Prisma Access Setup → Mobile Users")
        print("3. Look for 'Infrastructure Settings' or 'DNS' section")
        print("4. Observe the API calls in Network tab")

else:
    print(f"{RED}✗ No working endpoints found{RESET}")
    print()
    print("The Mobile Users DNS configuration might require:")
    print("  - Different URL structure")
    print("  - Specific folder or container parameters")
    print("  - Different API version")
    print()
    print("NEXT STEPS:")
    print("1. Use Browser DevTools to capture actual API calls")
    print("2. Check Prisma Access documentation for API structure")
    print("3. Verify Service Account has Mobile Users permissions")

print()
print("=" * 80)

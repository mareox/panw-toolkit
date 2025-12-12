#!/usr/bin/env python3
"""
Prisma SASE API Explorer

This script automatically discovers and tests API endpoints to find
the correct ones for Mobile Users DNS configuration.
"""

import json
import yaml
import requests
from datetime import datetime
from pathlib import Path

# ANSI color codes for better readability
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

print("=" * 80)
print("Prisma SASE API Explorer - Discovering Available Endpoints")
print("=" * 80)
print()

# Load credentials and get token
print("[1/4] Loading credentials and generating token...")
with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

client_id = config['api']['client_id']
client_secret = config['api']['client_secret']
tsg_id = config['api']['tsg_id']

# Get OAuth2 token
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
    print(f"{RED}✗ Failed to get token{RESET}")
    print(response.text)
    exit(1)

token = response.json()['access_token']
print(f"{GREEN}✓ Token generated{RESET}")
print()

# Setup headers for API calls
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# Base URLs to test
base_urls = [
    "https://api.sase.paloaltonetworks.com/sse/config/v1",
    "https://api.sase.paloaltonetworks.com/mt/config/v1",
    "https://api.sase.paloaltonetworks.com/config/v1",
]

# Endpoint patterns to test
endpoint_patterns = [
    # Mobile Users / GlobalProtect
    "/mobile-users",
    "/mobile-users/settings",
    "/mobile-users/dns",
    "/mobile-users/dns-settings",
    "/mobile-users/client-settings",
    "/mobile-users/infrastructure",
    "/globalprotect",
    "/globalprotect/settings",
    "/globalprotect/dns",
    "/globalprotect/infrastructure",
    "/globalprotect/client-settings",

    # General configuration
    "/locations",
    "/remote-networks",
    "/service-connections",
    "/internal-dns-servers",
    "/dns-servers",
    "/dns-settings",
    "/infrastructure-settings",

    # Prisma Access specific
    "/prisma-access-configs",
    "/prisma-access/settings",
    "/service-setup",
    "/deployments",
    "/config-versions",

    # Mobile Users Explicit Proxy
    "/mobile-users-explicit-proxy",
    "/mobile-users-explicit-proxy/infrastructure",
    "/mobile-users-explicit-proxy/dns-settings",
]

results = {
    'successful': [],
    'unauthorized': [],
    'not_found': [],
    'errors': []
}

print("[2/4] Testing API endpoints...")
print()

tested_count = 0
total_tests = len(base_urls) * len(endpoint_patterns)

for base_url in base_urls:
    for endpoint in endpoint_patterns:
        url = f"{base_url}{endpoint}"
        tested_count += 1

        try:
            # Show progress
            print(f"\r{BLUE}Testing {tested_count}/{total_tests}:{RESET} {url[:70]}...", end='', flush=True)

            response = requests.get(url, headers=headers, timeout=5)

            result = {
                'url': url,
                'status_code': response.status_code,
                'endpoint': endpoint,
                'base_url': base_url
            }

            if response.status_code == 200:
                result['success'] = True
                result['data'] = response.json()
                result['has_items'] = 'items' in response.json() if isinstance(response.json(), dict) else False
                result['has_data'] = 'data' in response.json() if isinstance(response.json(), dict) else False
                results['successful'].append(result)

            elif response.status_code == 401 or response.status_code == 403:
                result['message'] = 'Unauthorized/Forbidden'
                results['unauthorized'].append(result)

            elif response.status_code == 404:
                result['message'] = 'Not Found'
                results['not_found'].append(result)

            else:
                result['message'] = f"HTTP {response.status_code}"
                result['response'] = response.text[:200]
                results['errors'].append(result)

        except requests.exceptions.Timeout:
            result = {
                'url': url,
                'status_code': 'TIMEOUT',
                'endpoint': endpoint,
                'base_url': base_url,
                'message': 'Request timeout'
            }
            results['errors'].append(result)

        except Exception as e:
            result = {
                'url': url,
                'status_code': 'ERROR',
                'endpoint': endpoint,
                'base_url': base_url,
                'message': str(e)
            }
            results['errors'].append(result)

print("\r" + " " * 100 + "\r", end='')  # Clear progress line
print(f"{GREEN}✓ Completed testing {tested_count} endpoints{RESET}")
print()

# Display results
print("[3/4] API Discovery Results")
print("=" * 80)
print()

if results['successful']:
    print(f"{GREEN}✓ SUCCESSFUL ENDPOINTS ({len(results['successful'])}):{RESET}")
    print("-" * 80)

    # Group by relevance to DNS
    dns_related = []
    other_endpoints = []

    for result in results['successful']:
        if any(keyword in result['endpoint'].lower() for keyword in ['dns', 'mobile-user', 'globalprotect', 'infrastructure']):
            dns_related.append(result)
        else:
            other_endpoints.append(result)

    # Show DNS-related endpoints first
    if dns_related:
        print(f"\n{YELLOW}DNS/Mobile Users Related Endpoints:{RESET}")
        for result in dns_related:
            print(f"\n  {GREEN}✓{RESET} {result['url']}")
            print(f"     Status: {result['status_code']}")

            # Show some info about the response
            data = result.get('data', {})
            if isinstance(data, dict):
                keys = list(data.keys())[:5]
                print(f"     Response keys: {keys}")

                if 'items' in data:
                    print(f"     Items count: {len(data['items'])}")
                if 'total' in data:
                    print(f"     Total: {data['total']}")

    # Show other successful endpoints
    if other_endpoints:
        print(f"\n{YELLOW}Other Available Endpoints:{RESET}")
        for result in other_endpoints[:10]:  # Limit to first 10
            print(f"  {GREEN}✓{RESET} {result['endpoint']} - {result['status_code']}")

    print()
else:
    print(f"{YELLOW}⚠ No successful endpoints found{RESET}")
    print()

# Save detailed results
print("[4/4] Saving detailed results...")
output_file = f"api_discovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

with open(output_file, 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"{GREEN}✓ Results saved to: {output_file}{RESET}")
print()

# Summary and recommendations
print("=" * 80)
print("SUMMARY & RECOMMENDATIONS")
print("=" * 80)
print()

if results['successful']:
    print(f"{GREEN}✓ Found {len(results['successful'])} working endpoints{RESET}")

    # Find the most promising DNS endpoints
    dns_endpoints = [r for r in results['successful']
                     if any(k in r['endpoint'].lower() for k in ['dns', 'mobile-user', 'globalprotect'])]

    if dns_endpoints:
        print()
        print("Most promising endpoints for DNS configuration:")
        print()

        for endpoint in dns_endpoints[:5]:
            print(f"  → {endpoint['url']}")

            # Show sample of what's available
            data = endpoint.get('data', {})
            if isinstance(data, dict) and data:
                print(f"     Available data:")
                for key in list(data.keys())[:3]:
                    print(f"       - {key}")
            print()

        print("NEXT STEPS:")
        print(f"1. Review {output_file} for full details")
        print("2. Test these endpoints with curl or Postman")
        print("3. Look for endpoints that return DNS configuration")
        print("4. Update src/dns_config.py with the correct endpoint")
    else:
        print()
        print(f"{YELLOW}No DNS-specific endpoints found.{RESET}")
        print()
        print("This could mean:")
        print("  - DNS settings are under a different path")
        print("  - You need to use the Prisma Access UI to find the exact endpoint")
        print("  - The API structure is different for your deployment")
        print()
        print("RECOMMENDATION:")
        print("  Use Browser DevTools (F12) in Prisma Access UI:")
        print("  1. Navigate to Mobile Users → Infrastructure → DNS")
        print("  2. Watch Network tab for API calls")
        print("  3. Note the exact endpoint URLs used")

else:
    print(f"{RED}✗ No working endpoints discovered{RESET}")
    print()
    print("This could mean:")
    print("  - Service Account permissions are too restrictive")
    print("  - API endpoints use different URL patterns")
    print("  - Need to specify additional headers or parameters")
    print()
    print("NEXT STEPS:")
    print("  1. Verify Service Account has required permissions")
    print("  2. Use Browser DevTools to capture actual API calls")
    print("  3. Review Prisma Access API documentation")

print()
print("=" * 80)
print()

# Show curl examples for successful endpoints
if dns_endpoints:
    print("TESTING WITH CURL:")
    print("=" * 80)
    print()
    print("Copy these commands to test endpoints manually:")
    print()

    for endpoint in dns_endpoints[:3]:
        print(f"# Test: {endpoint['endpoint']}")
        print(f"curl -H 'Authorization: Bearer $PRISMA_TOKEN' \\")
        print(f"     '{endpoint['url']}'")
        print()

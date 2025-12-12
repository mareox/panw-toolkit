#!/usr/bin/env python3
"""
View DNS Configuration from Panorama API Results
"""

import json

print("=" * 80)
print("DNS Configuration from Panorama API")
print("=" * 80)
print()

with open('panorama_api_results.json', 'r') as f:
    results = json.load(f)

# Focus on DNS-related endpoints
dns_endpoints = [
    'worldwide\'/dns',
    'North america',
    'US-Western',
    'infrastructure-settings/dns',
    'dns-settings',
    'configs'
]

for result in results['successful']:
    prefix = result['prefix']

    # Check if this is a DNS-related endpoint
    is_dns_related = any(endpoint in prefix for endpoint in dns_endpoints)

    if is_dns_related and 'data' in result:
        print(f"{'=' * 80}")
        print(f"ENDPOINT: {prefix}")
        print(f"{'=' * 80}")
        print()
        print(json.dumps(result['data'], indent=2))
        print()
        print()

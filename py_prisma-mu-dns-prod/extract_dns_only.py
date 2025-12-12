#!/usr/bin/env python3
"""
Extract only DNS suffix/domain configuration from Panorama API Results
"""

import json

print("=" * 80)
print("DNS Suffix/Domain Configuration from Panorama API")
print("=" * 80)
print()

with open('panorama_api_results.json', 'r') as f:
    results = json.load(f)

def search_for_dns_domains(obj, path="", depth=0):
    """Recursively search for DNS-related configuration"""
    if depth > 20:  # Prevent infinite recursion
        return

    if isinstance(obj, dict):
        # Check if this dict contains DNS-related keys
        dns_keys = ['dns', 'suffix', 'domain', 'internal-domain-suffix',
                   'public-dns', 'split-dns', 'dns-suffix']

        for key in obj.keys():
            if any(dns_term in key.lower() for dns_term in dns_keys):
                print(f"  Path: {path}/{key}")
                print(f"  Value: {json.dumps(obj[key], indent=4)}")
                print()

        # Continue searching
        for key, value in obj.items():
            search_for_dns_domains(value, f"{path}/{key}", depth+1)

    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            search_for_dns_domains(item, f"{path}[{i}]", depth+1)

# Check each successful endpoint
for result in results['successful']:
    prefix = result['prefix']

    # Focus on likely DNS endpoints
    if 'dns' in prefix.lower() or 'config' in prefix:
        if 'data' in result:
            print(f"{'=' * 80}")
            print(f"Endpoint: {prefix}")
            print(f"{'=' * 80}")
            search_for_dns_domains(result['data'], "root")
            print()

#!/usr/bin/env python3
"""
API Discovery Script for Prisma SASE

This script helps discover the correct API endpoints and data structure
for your specific Prisma Access deployment.

Run this BEFORE using the main script to identify:
1. Available SDK methods
2. DNS configuration endpoints
3. Current configuration structure
"""

import argparse
import json
import sys
import yaml
from pathlib import Path


def load_config(config_path: str):
    """Load configuration from YAML file"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"ERROR: Configuration file not found: {config_path}")
        print("Please create config/config.yaml from config/config.yaml.template")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Discover Prisma SASE API endpoints and structure"
    )
    parser.add_argument(
        '-c', '--config',
        default='config/config.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '-o', '--output',
        default='api_discovery_results.json',
        help='Output file for discovered structure'
    )

    args = parser.parse_args()

    print("=" * 80)
    print("Prisma SASE API Discovery Tool")
    print("=" * 80)
    print()

    # Check if prisma_sase is installed
    try:
        import prisma_sase
    except ImportError:
        print("ERROR: prisma_sase module not found")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)

    # Load configuration
    print("[1/5] Loading configuration...")
    config = load_config(args.config)

    # Authenticate
    print("[2/5] Authenticating to Prisma SASE...")
    try:
        sdk = prisma_sase.API(controller="https://api.sase.paloaltonetworks.com")
        result = sdk.interactive.login_secret(
            client_id=config['api']['client_id'],
            client_secret=config['api']['client_secret'],
            tsg_id=config['api']['tsg_id']
        )

        if not result:
            print("ERROR: Authentication failed")
            sys.exit(1)

        print("✓ Authentication successful")
        print()

    except Exception as e:
        print(f"ERROR: Authentication failed - {str(e)}")
        sys.exit(1)

    # Discover available methods
    print("[3/5] Discovering available SDK methods...")
    print()
    print("GET methods:")
    print("-" * 40)

    get_methods = [m for m in dir(sdk.get) if not m.startswith('_')]
    for method in sorted(get_methods):
        print(f"  - sdk.get.{method}()")

    print()
    print("POST methods:")
    print("-" * 40)

    post_methods = [m for m in dir(sdk.post) if not m.startswith('_')]
    for method in sorted(post_methods):
        print(f"  - sdk.post.{method}()")

    print()

    # Try common endpoints
    print("[4/5] Testing common endpoints for DNS configuration...")
    print()

    endpoints_to_test = [
        ('prisma_access_configs', lambda: sdk.get.prisma_access_configs()),
        ('servicesetup', lambda: sdk.get.servicesetup()),
        ('mobile_users', lambda: sdk.get.mobile_users()),
        ('locations', lambda: sdk.get.locations()),
        ('tenant_service_groups', lambda: sdk.get.tenant_service_groups()),
    ]

    discovered_data = {}

    for name, func in endpoints_to_test:
        try:
            print(f"Testing sdk.get.{name}()...")
            result = func()

            if result:
                print(f"  ✓ SUCCESS - Retrieved {len(str(result))} bytes")

                # Check if it contains DNS-related keys
                if isinstance(result, dict):
                    dns_keys = [k for k in result.keys() if 'dns' in k.lower()]
                    if dns_keys:
                        print(f"  ⭐ Contains DNS-related keys: {dns_keys}")

                discovered_data[name] = result
            else:
                print(f"  ✗ No data returned")

        except AttributeError:
            print(f"  ✗ Method not available")
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")

        print()

    # Save results
    print("[5/5] Saving discovery results...")

    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(discovered_data, f, indent=2, default=str)

    print(f"✓ Results saved to: {output_path}")
    print()

    # Provide recommendations
    print("=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print()

    if discovered_data:
        print("Successfully discovered the following endpoints:")
        for endpoint in discovered_data.keys():
            print(f"  ✓ sdk.get.{endpoint}()")

        print()
        print("Next steps:")
        print(f"1. Review {args.output} to find DNS configuration structure")
        print("2. Look for keys containing 'dns', 'domain', 'resolution'")
        print("3. Update src/dns_config.py with the correct endpoint and structure")
        print()
        print("Alternative: Use browser DevTools")
        print("1. Open Prisma Access UI in browser with DevTools (F12)")
        print("2. Navigate to Mobile Users > Infrastructure > DNS Settings")
        print("3. Watch Network tab for API calls")
        print("4. Note the endpoint URLs and JSON structure")

    else:
        print("⚠ WARNING: No endpoints returned data")
        print()
        print("This could mean:")
        print("1. The SDK version doesn't support these methods")
        print("2. Your service account lacks necessary permissions")
        print("3. The deployment uses different endpoint names")
        print()
        print("Recommended approach:")
        print("→ Use browser DevTools to capture API calls from the UI")
        print("  1. Open Prisma Access UI")
        print("  2. Press F12 to open DevTools")
        print("  3. Go to Network tab")
        print("  4. Navigate to DNS settings in the UI")
        print("  5. Look for API calls in Network tab")

    print()
    print("=" * 80)

    # Logout
    try:
        sdk.get.logout()
        print("Logged out successfully")
    except:
        pass


if __name__ == "__main__":
    main()

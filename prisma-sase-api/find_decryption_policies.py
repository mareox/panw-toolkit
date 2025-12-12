#!/usr/bin/env python3
"""
Script to find decryption policies specifically in Prisma SASE API
"""

import requests
import json
import sys
from datetime import datetime

def load_bearer_token():
    """Load bearer token from saved file"""
    try:
        with open('bearer_token.json', 'r') as f:
            token_data = json.load(f)
            return token_data.get('access_token')
    except FileNotFoundError:
        print("❌ Bearer token file not found. Please run get_bearer_token.py first.")
        return None

def test_decryption_endpoints(bearer_token):
    """Test different endpoints that might contain decryption policies"""

    headers = {
        'Authorization': f'Bearer {bearer_token}',
        'Content-Type': 'application/json'
    }

    # Test various decryption-related endpoints
    endpoints_to_test = [
        # Decryption profiles
        "https://api.sase.paloaltonetworks.com/sse/config/v1/decryption-profiles",
        "https://api.sase.paloaltonetworks.com/sse/config/v1/decryption-profiles?folder=Mobile%20Users",

        # SSL/TLS decryption
        "https://api.sase.paloaltonetworks.com/sse/config/v1/ssl-decryption-profiles",
        "https://api.sase.paloaltonetworks.com/sse/config/v1/ssl-decryption-profiles?folder=Mobile%20Users",

        # Certificate profiles
        "https://api.sase.paloaltonetworks.com/sse/config/v1/certificate-profiles",
        "https://api.sase.paloaltonetworks.com/sse/config/v1/certificate-profiles?folder=Mobile%20Users",

        # Decryption settings
        "https://api.sase.paloaltonetworks.com/sse/config/v1/decryption-settings",
        "https://api.sase.paloaltonetworks.com/sse/config/v1/decryption-settings?folder=Mobile%20Users",

        # Check if decryption policies are part of security rules with specific action/profiles
        "https://api.sase.paloaltonetworks.com/sse/config/v1/security-rules?folder=Mobile%20Users&filter=name+contains+'decrypt'",
        "https://api.sase.paloaltonetworks.com/sse/config/v1/security-rules?folder=Mobile%20Users&filter=name+contains+'ssl'",
        "https://api.sase.paloaltonetworks.com/sse/config/v1/security-rules?folder=Mobile%20Users&filter=name+contains+'tls'",

        # Network security API
        "https://api.sase.paloaltonetworks.com/config/security/v1/decryption-policies",
        "https://api.sase.paloaltonetworks.com/config/security/v1/decryption-policies?folder=Mobile%20Users",

        # Try different path structures
        "https://api.sase.paloaltonetworks.com/sse/config/v1/decryption/policies",
        "https://api.sase.paloaltonetworks.com/sse/config/v1/policies/decryption",

        # Objects API
        "https://api.sase.paloaltonetworks.com/sse/config/objects/v1/decryption-profiles",
        "https://api.sase.paloaltonetworks.com/sse/config/objects/v1/ssl-decryption-profiles",
    ]

    successful_calls = []

    print("🔍 Searching for decryption policies endpoints...")
    print("=" * 60)

    for endpoint in endpoints_to_test:
        print(f"\n🔗 Testing: {endpoint}")

        try:
            response = requests.get(endpoint, headers=headers, timeout=15)
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                try:
                    data = response.json()

                    if isinstance(data, dict) and 'data' in data:
                        items = data['data']
                        print(f"   ✅ SUCCESS! Found {len(items)} items")

                        if len(items) > 0:
                            print(f"   📝 Sample keys: {list(items[0].keys()) if items else 'No items'}")

                            # Check if these look like decryption policies
                            for item in items[:3]:  # Check first 3 items
                                if any(keyword in str(item).lower() for keyword in ['decrypt', 'ssl', 'tls', 'certificate']):
                                    print(f"   🎯 Found potential decryption policy: {item.get('name', 'Unnamed')}")

                        successful_calls.append({
                            'endpoint': endpoint,
                            'data': data,
                            'item_count': len(items)
                        })
                    else:
                        print(f"   ✅ SUCCESS! Non-standard format")
                        successful_calls.append({
                            'endpoint': endpoint,
                            'data': data,
                            'item_count': 'unknown'
                        })

                except json.JSONDecodeError:
                    print(f"   ✅ SUCCESS! Non-JSON response")
                    successful_calls.append({
                        'endpoint': endpoint,
                        'data': response.text,
                        'item_count': 'non-json'
                    })

            elif response.status_code == 400:
                print(f"   ⚠️  Bad request: {response.text[:100]}...")
            elif response.status_code == 403:
                print(f"   ❌ Access denied")
            elif response.status_code == 404:
                print(f"   ❌ Not found")
            else:
                print(f"   ❌ Status {response.status_code}: {response.text[:50]}...")

        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

    return successful_calls

def main():
    print("Prisma SASE Decryption Policies Search")
    print("=" * 50)

    bearer_token = load_bearer_token()
    if not bearer_token:
        sys.exit(1)

    # Search for decryption policies
    successful_calls = test_decryption_endpoints(bearer_token)

    print(f"\n" + "=" * 60)
    print(f"SUMMARY")
    print(f"=" * 60)

    if successful_calls:
        print(f"✅ Found {len(successful_calls)} working decryption-related endpoints:")

        decryption_policies = []

        for call in successful_calls:
            print(f"\n📍 {call['endpoint']}")
            print(f"   Items: {call['item_count']}")

            data = call['data']
            if isinstance(data, dict) and 'data' in data:
                items = data['data']

                # Filter for items that might be decryption policies
                potential_decryption = []
                for item in items:
                    item_str = str(item).lower()
                    if any(keyword in item_str for keyword in ['decrypt', 'ssl', 'tls', 'certificate']):
                        potential_decryption.append(item)

                if potential_decryption:
                    print(f"   🎯 Potential decryption policies: {len(potential_decryption)}")
                    decryption_policies.extend(potential_decryption)

                    for policy in potential_decryption[:5]:  # Show first 5
                        print(f"      • {policy.get('name', 'Unnamed')} (ID: {policy.get('id', 'N/A')})")

        if decryption_policies:
            print(f"\n🎉 Total potential decryption policies found: {len(decryption_policies)}")

            # Save decryption policies
            with open('found_decryption_policies.json', 'w') as f:
                json.dump(decryption_policies, f, indent=2)
            print(f"💾 Saved to found_decryption_policies.json")
        else:
            print(f"\n❌ No decryption policies found in accessible endpoints")

    else:
        print(f"❌ No working decryption-related endpoints found")

    # Save results
    results = {
        "timestamp": datetime.now().isoformat(),
        "successful_calls": successful_calls
    }

    with open('decryption_search_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Full results saved to decryption_search_results.json")

if __name__ == "__main__":
    main()
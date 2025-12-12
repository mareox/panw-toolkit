#!/usr/bin/env python3
"""
Script to test what Prisma SASE API endpoints we can access and get decryption policies
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

def test_sase_config_api(bearer_token):
    """Test SASE Configuration API endpoints"""

    headers = {
        'Authorization': f'Bearer {bearer_token}',
        'Content-Type': 'application/json'
    }

    # Test different SASE Config API endpoints
    endpoints_to_test = [
        # Decryption policies with folder parameter
        "https://api.sase.paloaltonetworks.com/sse/config/v1/decryption-policies?folder=Mobile%20Users",
        "https://api.sase.paloaltonetworks.com/sse/config/v1/decryption-policies?folder=Mobile Users",
        "https://api.sase.paloaltonetworks.com/sse/config/v1/decryption-policies?folder=Shared",
        "https://api.sase.paloaltonetworks.com/sse/config/v1/decryption-policies",

        # Try different API versions/paths
        "https://api.sase.paloaltonetworks.com/config/security/v1/decryption-policies",
        "https://api.sase.paloaltonetworks.com/config/security/v1/decryption-policies?folder=Mobile%20Users",

        # Try listing folders first
        "https://api.sase.paloaltonetworks.com/sse/config/v1/folders",

        # Try other policy types
        "https://api.sase.paloaltonetworks.com/sse/config/v1/security-rules",
        "https://api.sase.paloaltonetworks.com/sse/config/v1/security-rules?folder=Mobile%20Users",

        # Try base config endpoint
        "https://api.sase.paloaltonetworks.com/sse/config/v1/",
    ]

    successful_calls = []

    for endpoint in endpoints_to_test:
        print(f"\n🔍 Testing: {endpoint}")

        try:
            response = requests.get(endpoint, headers=headers, timeout=15)
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ SUCCESS! Found data: {len(str(data))} chars")

                    # Show structure
                    if isinstance(data, dict):
                        if 'data' in data:
                            items = data['data']
                            print(f"   📋 Found {len(items)} items in 'data' array")
                        else:
                            print(f"   📋 Response keys: {list(data.keys())}")

                    successful_calls.append({
                        'endpoint': endpoint,
                        'data': data
                    })

                    # Preview first few items if it's a list
                    if isinstance(data, dict) and 'data' in data and len(data['data']) > 0:
                        print(f"   📝 Sample item keys: {list(data['data'][0].keys()) if data['data'] else 'No items'}")

                except json.JSONDecodeError:
                    print(f"   ✅ SUCCESS! Non-JSON response: {response.text[:100]}")
                    successful_calls.append({
                        'endpoint': endpoint,
                        'data': response.text
                    })

            elif response.status_code == 403:
                print(f"   ❌ Access denied: {response.text[:100]}")
            elif response.status_code == 404:
                print(f"   ❌ Not found")
            elif response.status_code == 400:
                print(f"   ❌ Bad request: {response.text[:100]}")
            else:
                print(f"   ❌ Status {response.status_code}: {response.text[:100]}")

        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

    return successful_calls

def main():
    print("Prisma SASE API Access Test")
    print("=" * 50)

    bearer_token = load_bearer_token()
    if not bearer_token:
        sys.exit(1)

    # Test endpoints
    successful_calls = test_sase_config_api(bearer_token)

    print(f"\n" + "=" * 50)
    print(f"SUMMARY")
    print(f"=" * 50)

    if successful_calls:
        print(f"✅ {len(successful_calls)} successful API calls found:")

        for call in successful_calls:
            print(f"\n📍 {call['endpoint']}")
            data = call['data']

            if isinstance(data, dict):
                if 'data' in data and isinstance(data['data'], list):
                    policies = data['data']
                    print(f"   Found {len(policies)} policies")

                    # Look for Mobile Users policies
                    mobile_policies = [p for p in policies if 'folder' in p and 'Mobile Users' in str(p['folder'])]
                    print(f"   Mobile Users policies: {len(mobile_policies)}")

                    if mobile_policies:
                        print(f"   📋 Mobile Users Decryption Policies:")
                        for i, policy in enumerate(mobile_policies, 1):
                            print(f"      {i}. {policy.get('name', 'Unnamed')} (ID: {policy.get('id', 'N/A')})")
                            print(f"         Folder: {policy.get('folder', 'N/A')}")
                            print(f"         Disabled: {policy.get('disabled', 'N/A')}")

                        # Save Mobile Users policies
                        with open('mobile_users_decryption_policies.json', 'w') as f:
                            json.dump(mobile_policies, f, indent=2)
                        print(f"\n   💾 Mobile Users policies saved to mobile_users_decryption_policies.json")

                    # Show first few policies as example
                    if len(policies) > 0:
                        print(f"   📝 Sample policy structure:")
                        print(f"      {json.dumps(policies[0], indent=6)}")

    else:
        print(f"❌ No successful API calls found")

    # Save all results
    results = {
        "timestamp": datetime.now().isoformat(),
        "successful_calls": successful_calls
    }

    with open('sase_access_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Full results saved to sase_access_test_results.json")

if __name__ == "__main__":
    main()
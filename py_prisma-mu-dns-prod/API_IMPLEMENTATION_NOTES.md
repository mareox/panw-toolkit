# API Implementation Notes

## Important Notice

The `dns_config.py` file contains placeholder logic that needs to be adapted based on the actual Prisma SASE API structure for your specific deployment. This document provides guidance on how to find and implement the correct API endpoints.

## Finding the Correct API Endpoints

### Method 1: Use the Prisma Access Web UI with Browser DevTools

This is the most reliable method to discover the exact API structure:

1. **Open Browser DevTools** (F12 in Chrome/Firefox)
2. **Go to Network tab**
3. **Navigate to Prisma Access UI**: Settings > Mobile Users > Infrastructure Settings
4. **Look for DNS configuration section**
5. **Observe the API calls** made when viewing/editing DNS settings
6. **Note the endpoints**:
   - GET requests show the current structure
   - PUT/POST requests show the update format

**Example findings:**
```
GET /sse/config/v1/mobile-users-explicit-proxy/dns-settings
PUT /sse/config/v1/mobile-users-explicit-proxy/dns-settings
```

### Method 2: Use the Prisma SASE SDK Documentation

Check the SDK's built-in help:

```python
import prisma_sase

sdk = prisma_sase.API()
# Authenticate first
sdk.interactive.login_secret(...)

# List available endpoints
help(sdk.get)
help(sdk.post)

# Explore specific methods
print(dir(sdk.get))
```

### Method 3: Prisma SASE API Documentation

Visit: https://pan.dev/sase/api/

Look for:
- Mobile Users Configuration
- GlobalProtect Settings
- DNS Configuration
- Service Setup

## Expected API Structure

Based on Prisma Access documentation, the DNS configuration typically follows this structure:

### Internal Domain Resolution

```json
{
  "dns_rules": [
    {
      "name": "CustomDNS",
      "rule_type": "internal",
      "domains": [
        "*.internal.company.com",
        "*.corp.company.com"
      ],
      "dns_servers": {
        "primary": "10.0.0.1",
        "secondary": "10.0.0.2"
      }
    }
  ]
}
```

### Public DNS Configuration

```json
{
  "public_dns": {
    "primary": {
      "dns_type": "prisma_access_default"
    },
    "secondary": {
      "dns_type": "prisma_access_default"
    }
  }
}
```

## Updating dns_config.py

Once you've identified the correct API endpoints and structure, update these methods in `src/dns_config.py`:

### 1. get_dns_settings()

Replace the placeholder with the actual endpoint:

```python
def get_dns_settings(self) -> Dict[str, Any]:
    # Replace with actual endpoint discovered from browser DevTools
    response = self.sdk.get.mobile_users_dns_config()  # Example
    # OR
    response = self.sdk.rest_call(
        url="/sse/config/v1/mobile-users/dns-settings",
        method="GET"
    )
    return response
```

### 2. update_dns_config()

Update the API call to use the correct endpoint:

```python
def update_dns_config(...):
    # ... backup and prepare config ...

    # Replace with actual update endpoint
    response = self.sdk.post.mobile_users_dns_config(updated_config)
    # OR
    response = self.sdk.rest_call(
        url="/sse/config/v1/mobile-users/dns-settings",
        method="PUT",
        data=updated_config
    )
```

### 3. _process_dns_update()

Update the structure manipulation based on actual API format:

```python
def _process_dns_update(self, config, domains, rule_name):
    # Adjust based on actual API structure from DevTools

    # Example: If API uses 'dns_rules' array
    if 'dns_rules' not in config:
        config['dns_rules'] = []

    # Find or create the CustomDNS rule
    custom_rule = None
    for rule in config['dns_rules']:
        if rule.get('name') == rule_name:
            custom_rule = rule
            break

    if custom_rule:
        # Update existing rule
        custom_rule['domains'] = domains
    else:
        # Create new rule
        config['dns_rules'].append({
            'name': rule_name,
            'rule_type': 'internal',
            'domains': domains
        })

    # Update public DNS settings
    config['public_dns'] = {
        'primary': {'dns_type': 'prisma_access_default'},
        'secondary': {'dns_type': 'prisma_access_default'}
    }

    return config
```

## Testing Strategy

### Phase 1: Discovery (Browser DevTools)

1. Open Prisma Access UI
2. Navigate to Mobile Users DNS settings
3. Capture all API calls in Network tab
4. Document the exact JSON structure

### Phase 2: Read-Only Testing

```python
# Test reading current configuration
sdk = prisma_sase.API()
sdk.interactive.login_secret(...)

# Try different methods to find the right one
try:
    config = sdk.get.mobile_users_config()
    print(json.dumps(config, indent=2))
except:
    pass

try:
    config = sdk.get.servicesetup()
    print(json.dumps(config, indent=2))
except:
    pass
```

### Phase 3: Dry-Run Testing

1. Implement the correct endpoints
2. Run with `--dry-run` flag
3. Verify the config changes look correct
4. Compare with expected structure from UI

### Phase 4: Limited Testing

1. Test on a single test region first
2. Create manual backup in UI
3. Apply changes
4. Verify in UI
5. Rollback if needed

## Common SDK Methods

The Prisma SASE SDK typically provides these methods:

```python
# GET operations
sdk.get.prisma_access_configs()
sdk.get.servicesetup()
sdk.get.locations()
sdk.get.mobile_users()

# POST/PUT operations
sdk.post.servicesetup(data)
sdk.put.prisma_access_configs(data)

# Direct REST calls
sdk.rest_call(url="/path", method="GET|POST|PUT", data={})
```

## Region-Specific Configuration

If your deployment requires region-specific DNS configuration:

```python
def update_dns_per_region(self, regions, domains, rule_name):
    for region in regions:
        region_config = self.get_region_dns_config(region)
        updated_config = self._process_dns_update(
            region_config,
            domains,
            rule_name
        )
        self.apply_region_dns_config(region, updated_config)
```

## Validation

Before applying any changes, validate the structure:

```python
def validate_dns_structure(config):
    """Validate DNS config matches API requirements"""

    # Check required fields
    assert 'dns_rules' in config or 'internal_domains' in config
    assert 'public_dns' in config

    # Validate domain format
    for domain in domains:
        assert len(domain) > 0
        assert not any(c in domain for c in [' ', ',', ';'])

    return True
```

## Rollback Procedure

If something goes wrong:

1. **From Backup File:**
   ```python
   with open('backup/dns_config_backup_TIMESTAMP.json') as f:
       backup_config = json.load(f)

   sdk.post.servicesetup(backup_config)  # Restore
   ```

2. **From UI:**
   - Navigate to Mobile Users > Infrastructure Settings
   - Manually restore DNS configuration

## Next Steps

1. **Discover actual endpoints** using browser DevTools
2. **Update `src/dns_config.py`** with correct endpoints and structure
3. **Test read operations** first (GET calls only)
4. **Implement dry-run** testing to verify logic
5. **Test on non-production** environment if possible
6. **Apply to production** after validation

## Support Resources

- **Prisma SASE API Docs**: https://pan.dev/sase/api/
- **SDK Repository**: https://github.com/PaloAltoNetworks/prisma-sase-sdk-python
- **Prisma Access Docs**: https://docs.paloaltonetworks.com/prisma-access

## Example: Complete API Discovery Session

```python
#!/usr/bin/env python3
"""API Discovery Script"""

import prisma_sase
import json

# Authenticate
sdk = prisma_sase.API(controller="https://api.sase.paloaltonetworks.com")
sdk.interactive.login_secret(
    client_id="your-id",
    client_secret="your-secret",
    tsg_id="your-tsg"
)

# Try various endpoints to find DNS config
print("Testing various endpoints...\n")

endpoints = [
    ('get.prisma_access_configs', lambda: sdk.get.prisma_access_configs()),
    ('get.servicesetup', lambda: sdk.get.servicesetup()),
    ('get.mobile_users', lambda: sdk.get.mobile_users()),
    ('get.locations', lambda: sdk.get.locations()),
]

for name, func in endpoints:
    try:
        print(f"Trying {name}...")
        result = func()
        print(f"SUCCESS: {name}")
        print(json.dumps(result, indent=2))
        print("-" * 80)
    except Exception as e:
        print(f"FAILED: {name} - {str(e)}\n")

sdk.get.logout()
```

Run this script to discover which endpoints work with your Prisma Access deployment.

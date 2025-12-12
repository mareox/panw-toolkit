# Finding Mobile Users DNS API Using Browser DevTools

Since the Mobile Users CLIENT DNS configuration endpoint couldn't be discovered through API exploration, you need to capture the actual API calls from the Prisma Access UI.

## Step-by-Step Guide

### Step 1: Open Prisma Access UI

1. Open your browser (Chrome or Firefox recommended)
2. Log into Prisma Access at: https://apps.paloaltonetworks.com/
3. **Keep the browser window open** - don't navigate anywhere yet

### Step 2: Open Developer Tools

**Chrome/Edge:**
- Press `F12` OR
- Right-click → Inspect OR
- Menu → More Tools → Developer Tools

**Firefox:**
- Press `F12` OR
- Menu → Web Developer → Web Developer Tools

### Step 3: Setup Network Monitoring

1. Click on the **Network** tab
2. **Clear** any existing entries (trash/clear icon)
3. Make sure **"Preserve log"** is checked (so entries don't disappear)
4. Filter by **XHR** or **Fetch** (to see only API calls, not images/CSS)

### Step 4: Navigate to Mobile Users DNS Settings

In the Prisma Access UI, navigate to where you configure Mobile Users CLIENT DNS:

**Common paths:**
- **Workflows → Prisma Access Setup → Mobile Users → Infrastructure Settings**
- **Settings → Mobile Users → Infrastructure → DNS**
- **Manage → GlobalProtect → Infrastructure Settings → DNS**

**Look for sections related to:**
- Client DNS Configuration
- DNS Settings for Mobile Users
- Infrastructure DNS
- GlobalProtect DNS

### Step 5: Capture the API Calls

1. **Watch the Network tab** as the page loads
2. **Look for API calls** - they usually have URLs like:
   - `/sse/config/v1/...`
   - `/mt/config/v1/...`
   - `/config/...`
   - `/api/...`

3. **Click on each API call** to see details

### Step 6: Identify the DNS Configuration Endpoint

For each API call, look at:

**Request:**
- **URL** - This is the endpoint you need
- **Method** - Usually GET (retrieve) or PUT/POST (update)
- **Headers** - Note the Authorization header format

**Response:**
- **Body** - This shows the current DNS configuration
- Look for JSON containing:
  - DNS server settings
  - Domain lists
  - Client DNS rules

### Step 7: Document What You Find

**For GET requests (retrieving config):**
```
URL: https://api.sase.paloaltonetworks.com/sse/config/v1/...
Method: GET
Response: {
  "dns_settings": {
    "internal_domains": [...],
    "dns_servers": {...}
  }
}
```

**For PUT/POST requests (updating config):**
```
URL: https://api.sase.paloaltonetworks.com/sse/config/v1/...
Method: PUT or POST
Request Payload: {
  ... (the structure to send)
}
```

## What to Look For

### Example DNS Configuration Structure

You might see something like:

```json
{
  "dns_config": {
    "internal_domain_rules": [
      {
        "name": "CustomDNS",
        "domains": ["*.company.com", "internal.local"],
        "dns_servers": ["10.0.0.1", "10.0.0.2"]
      }
    ],
    "public_dns": {
      "primary": "prisma_access_default",
      "secondary": "prisma_access_default"
    }
  }
}
```

Or:

```json
{
  "mobile_users": {
    "infrastructure": {
      "dns_settings": {
        "rules": [...],
        "public_dns_type": "default"
      }
    }
  }
}
```

## Common Endpoint Patterns

Look for URLs containing:

- `/mobile-users`
- `/globalprotect`
- `/infrastructure`
- `/dns`
- `/client-settings`
- `/onboarding`

## Tips

1. **Try editing** the DNS config in the UI - this will trigger PUT/POST requests
2. **Check Preview tab** in DevTools to see formatted JSON
3. **Look for patterns** - multiple related endpoints often share a base path
4. **Note any query parameters** (e.g., `?folder=Mobile%20Users`)
5. **Watch for redirects** - the UI might call one endpoint that redirects to another

## Example Screenshot Points

When you find the right API call, you should see:

1. **Status**: 200 OK
2. **Content-Type**: application/json
3. **Response contains**: DNS configuration with domains and rules
4. **URL pattern**: Includes "mobile" or "globalprotect" or "dns"

## After You Find It

Once you've identified the correct endpoint:

1. **Copy the full URL**
2. **Note the HTTP method** (GET/PUT/POST)
3. **Save the JSON structure** (both request and response)
4. **Take screenshots** if helpful
5. **Test with curl** using your bearer token:

```bash
# Get your token first
python3 get_token.py

# Test the endpoint
export PRISMA_TOKEN="your-token-here"

curl -H "Authorization: Bearer $PRISMA_TOKEN" \
     -H "Content-Type: application/json" \
     "THE_URL_YOU_FOUND"
```

## Report Back

Once you find the endpoint, provide:

1. **Full URL**
2. **HTTP Method**
3. **Sample response JSON**
4. **Request payload structure** (if you captured a PUT/POST)

Then we can update `src/dns_config.py` with the correct endpoint!

---

## Alternative: Check Prisma Access Documentation

If Browser DevTools is challenging, you can also:

1. Visit: https://docs.paloaltonetworks.com/prisma-access
2. Search for: "Mobile Users DNS API"
3. Look in the API reference section
4. Find the specific endpoint for your deployment type

---

## Still Stuck?

If you can't find it with DevTools:

1. **Share a screenshot** of the Prisma Access UI page where you configure Mobile Users DNS
2. **Share the Network tab** after filtering to XHR/Fetch
3. I can help identify the correct API call from the screenshots

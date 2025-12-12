# Quick Guide: Find SCM Client DNS API Endpoint

## You Know Exactly Where It Is - Let's Capture the API Call

You said the config is at:
**https://stratacloudmanager.paloaltonetworks.com/workflows/mobile-users-gp/setup/infrastructure-settings**

Section: **Client DNS**
Regions: **worldwide, North america, US-Western**

---

## 5-Minute Steps:

### 1. Open Browser with DevTools

```bash
# Open in Chrome/Firefox
https://stratacloudmanager.paloaltonetworks.com/
```

**Press F12** to open Developer Tools

###2. Setup Network Monitoring

- Click **Network** tab
- Click the **🗑️ Clear** button to clear all entries
- ✅ Check **"Preserve log"** (so it doesn't clear when navigating)
- Filter by: **Fetch/XHR** (to see only API calls)

### 3. Navigate to Client DNS

In SCM, go to:
```
Workflows → Mobile Users - GP → Setup → Infrastructure Settings
```

Look for the **"Client DNS"** section with:
- worldwide
- North america
- US-Western

### 4. Trigger the API Call

**Click on one of the regions** (e.g., "worldwide")

This will load the DNS configuration and trigger an API call.

### 5. Find the API Call in Network Tab

Look for an API call that:
- Has status **200** (green)
- URL contains: **`/infrastructure`** or **`/dns`** or **`/client`**
- URL starts with: **`https://api.sase.paloaltonetworks.com/`**

### 6. Click on the API Call

When you click on it, you'll see:

**Headers tab:**
```
Request URL: https://api.sase.paloaltonetworks.com/sse/config/v1/SOMETHING
Request Method: GET
Status Code: 200
```

**Response tab:**
Shows the JSON configuration - this is what we need!

### 7. Copy the Information

**Copy these:**

1. **Full URL** (from Request URL)
   ```
   Example: https://api.sase.paloaltonetworks.com/sse/config/v1/infrastructure-settings?folder=Mobile%20Users&location=worldwide
   ```

2. **Response JSON** (from Response tab)
   - Click "Preview" or "Response"
   - Right-click → Copy object
   - Or just note the structure

---

## What to Look For in the Response

The response should contain something like:

```json
{
  "data": [
    {
      "id": "...",
      "name": "worldwide",
      "dns_settings": {
        "internal_domains": [...],
        "public_dns": "...",
        ...
      }
    }
  ]
}
```

Or:

```json
{
  "client_dns": {
    "internal_domain_rules": [...],
    "public_dns_settings": {...}
  }
}
```

---

## Quick Test

Once you have the URL, test it with your token:

```bash
# Generate token
cd /path/to/script
python3 get_token.py

# Copy the token
export PRISMA_TOKEN="paste-token-here"

# Test the endpoint you found
curl -H "Authorization: Bearer $PRISMA_TOKEN" \
     "THE_URL_YOU_COPIED_FROM_DEVTOOLS"
```

If it returns JSON with DNS configuration, **you found it!**

---

## Common SCM Patterns

The URL will likely look like one of these:

```
https://api.sase.paloaltonetworks.com/sse/config/v1/infrastructure-settings?folder=Mobile%20Users
https://api.sase.paloaltonetworks.com/sse/config/v1/infrastructure-settings?folder=Mobile%20Users&location=worldwide
https://api.sase.paloaltonetworks.com/sse/config/v1/mobile-users/client-dns?folder=Mobile%20Users
```

---

## After You Find It

Once you have the endpoint, provide me with:

1. **Full URL** (including any ?parameters)
2. **HTTP Method** (GET, PUT, POST)
3. **Sample Response JSON** (just copy/paste a small snippet)

Then I'll update the script to use the correct endpoint!

---

## Screenshots Welcome

If you want to share screenshots of:
- The Network tab with the API call highlighted
- The Response preview

That would make it even easier to help!

---

## Alternative: Ask the Person Who Updated It

You mentioned:
> "Last Updated: 2025-10-28 by msanchez@paloaltonetworks.com"

You could ask msanchez what endpoint they used, or check if there are any internal docs about the SCM API for Mobile Users Client DNS.

# Browser DevTools - Network Tab Guide

## Which Tab? → **NETWORK TAB**

When you press F12, you'll see multiple tabs:
- Elements
- Console
- Sources
- **Network** ← **THIS ONE!**
- Performance
- Memory
- etc.

---

## Step-by-Step Visual Guide

### Step 1: Open Developer Tools

Press **F12** (or right-click → Inspect)

You'll see tabs at the top:
```
Elements | Console | Sources | Network | Performance | ...
                                  ↑
                            CLICK HERE
```

### Step 2: Click on "Network" Tab

You'll see something like:

```
┌─────────────────────────────────────────────────────────────┐
│ Network Tab                                                 │
├─────────────────────────────────────────────────────────────┤
│ Filter: [ All | Fetch/XHR | JS | CSS | Img | Media ]       │
│          ↑                                                   │
│    Click "Fetch/XHR" to filter only API calls               │
├─────────────────────────────────────────────────────────────┤
│ Name                    | Status | Type | Size | Time       │
├─────────────────────────────────────────────────────────────┤
│ (API calls will appear here when you navigate)              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Step 3: Clear Old Entries

Click the **🚫 clear button** (circle with line through it) to remove old entries

### Step 4: Check "Preserve log"

Make sure the **"Preserve log"** checkbox is CHECKED ✅

This keeps the API calls visible even when the page changes.

### Step 5: Navigate to Client DNS Page

In the main browser window (not DevTools), navigate to:
```
Workflows → Mobile Users - GP → Setup → Infrastructure Settings
```

Find the **"Client DNS"** section.

### Step 6: Click on a Region

Click on **"worldwide"** or **"North america"** or **"US-Western"**

### Step 7: Watch the Network Tab

**Immediately**, you'll see new entries appear in the Network tab!

They'll look like:

```
┌──────────────────────────────────────────────────────────────┐
│ Name                              | Status | Type     | Size │
├──────────────────────────────────────────────────────────────┤
│ infrastructure-settings?folder... | 200    | fetch    | 2.3k │ ← THIS!
│ analytics                         | 200    | fetch    | 156  │
│ user-settings                     | 200    | fetch    | 892  │
└──────────────────────────────────────────────────────────────┘
```

Look for one that:
- **Status is 200** (shows as green or black "200")
- **Type is "fetch" or "xhr"**
- **Name contains** words like: infrastructure, dns, settings, client

### Step 8: Click on the API Call

Click on the entry that looks like it's the DNS configuration call.

When you click it, a **panel opens on the right** with tabs:
```
Headers | Preview | Response | Initiator | Timing
   ↑        ↑
 START    THEN
  HERE     HERE
```

### Step 9: Headers Tab - Get the URL

In the **Headers** tab, scroll to the top. You'll see:

```
General
  Request URL: https://api.sase.paloaltonetworks.com/sse/config/v1/infrastructure-settings?folder=Mobile%20Users&location=worldwide
  Request Method: GET
  Status Code: 200 OK
```

**Copy the entire "Request URL"** - this is what I need!

### Step 10: Preview Tab - See the Data

Click the **Preview** tab to see the formatted JSON response.

It will show you the structure like:
```json
{
  "data": [
    {
      "id": "...",
      "name": "worldwide",
      "folder": "Mobile Users",
      "dns_suffix": [...],
      ...
    }
  ]
}
```

This shows you what the current configuration looks like.

---

## What You're Looking For

### The Request URL should look like ONE of these patterns:

```
https://api.sase.paloaltonetworks.com/sse/config/v1/infrastructure-settings?folder=Mobile%20Users

https://api.sase.paloaltonetworks.com/sse/config/v1/infrastructure-settings?folder=Mobile%20Users&location=worldwide

https://api.sase.paloaltonetworks.com/sse/config/v1/mobile-users/infrastructure-settings

https://api.sase.paloaltonetworks.com/sse/config/v1/mobile-users-globalprotect/infrastructure
```

### The Response should contain DNS-related data:

Look for keys like:
- `dns_suffix`
- `dns_settings`
- `client_dns`
- `internal_domains`
- `domain_list`
- `public_dns`

---

## Example Screenshot Points

When you find it, you'll see:

**Network Tab Entry:**
```
Name: infrastructure-settings?folder=Mobile%20Users&location=worldwide
Status: 200
Type: fetch
Size: 2.3 KB
```

**Headers Tab:**
```
Request URL: https://api.sase.paloaltonetworks.com/sse/config/v1/infrastructure-settings?folder=Mobile%20Users&location=worldwide
Request Method: GET
Status Code: 200 OK
```

**Preview/Response Tab:**
```json
{
  "data": [
    {
      "id": "abc-123",
      "name": "worldwide",
      "dns_suffix": ["*.cummins.com", "*.internal.local"],
      ...
    }
  ]
}
```

---

## Quick Tips

### If you see TOO MANY entries in Network tab:

1. Click **"Fetch/XHR"** filter button (near the top)
   - This hides images, CSS, JavaScript files
   - Shows only API calls

2. Look for entries with **"200"** status
   - Green or black "200" = successful
   - Red "404" or "500" = ignore these

3. Look at the **Name** column
   - Look for: infrastructure, settings, dns, client, mobile

### If the Network tab is empty:

1. Make sure you **cleared** old entries first (🚫 button)
2. Make sure **"Preserve log"** is checked ✅
3. **Refresh the page** or **navigate again** to the Client DNS section
4. **Click on a region** (worldwide, North america, US-Western)

---

## What to Share With Me

Once you find it, just copy and paste:

### 1. The Request URL:
```
https://api.sase.paloaltonetworks.com/sse/config/v1/...
```

### 2. A small sample of the Response (from Preview or Response tab):
```json
{
  "data": [
    {
      "name": "worldwide",
      ...
    }
  ]
}
```

That's all I need to update the script!

---

## Still Confused?

If you're not sure which entry is the right one, you can:

1. **Copy ALL the Request URLs** you see that have Status 200
2. **Paste them all** in your response
3. I'll identify which one is the Client DNS configuration

---

## Alternative: Take a Screenshot

If it's easier, take a screenshot of:
1. The **Network tab** showing the list of API calls
2. The **Headers section** of a selected call showing the Request URL
3. The **Preview section** showing the JSON response

Then share those screenshots, and I can tell you exactly which endpoint to use!

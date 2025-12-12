# Prisma Access Mobile Users DNS Configuration Updater

Automated tool to update Prisma Access Mobile Users Client DNS configuration using the Strata Cloud Manager API.

---

## ✅ Status: Production Ready

This script is **fully implemented and tested**. No API customization required!

---

## What This Tool Does

This script automates DNS configuration tasks for Prisma Access Mobile Users:

1. **Adds Internal Domain Resolution Rule**
   - Rule name: "CustomDNS" (configurable)
   - Imports domains from a CSV file
   - Applies to ALL configured regions (worldwide, americas, ip-pool-group-23)

2. **Uses Mobile Agent Infrastructure Settings API**
   - Endpoint: `/sse/config/v1/mobile-agent/infrastructure-settings`
   - Updates DNS configuration for GlobalProtect clients
   - Preserves existing DNS rules (like "CumminsDNS")

3. **Flexible Region Selection** 🆕
   - Update ALL regions (default) or select specific regions
   - Choose individual IP pool groups (e.g., US-Eastern, Japan, Canada)
   - See [REGION_SELECTION_GUIDE.md](REGION_SELECTION_GUIDE.md) for detailed instructions

---

## 🔴 IMPORTANT: Changes Must Be Committed in SCM!

**After running this script successfully, you MUST commit the changes in Strata Cloud Manager for them to take effect!**

The script updates the configuration but does **NOT** automatically commit it. See [COMMIT_CHANGES_GUIDE.md](COMMIT_CHANGES_GUIDE.md) for detailed instructions.

---

## Prerequisites

- **Python 3.7+** installed
- **Prisma Access** instance with API access enabled
- **Service Account** with API credentials and appropriate permissions

---

## Quick Start (5 Minutes)

See [QUICKSTART.md](QUICKSTART.md) for the fastest way to get started.

---

## Detailed Setup Instructions

### Step 1: Initial Setup (5 minutes)

#### Option A: Automated Setup (Recommended)

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

**Windows:**
```cmd
setup.bat
```

This will:
- Create a Python virtual environment named `mudns`
- Install all required dependencies
- Create configuration file templates

#### Option B: Manual Setup

```bash
# Create virtual environment
python3 -m venv mudns

# Activate virtual environment
source mudns/bin/activate          # Linux/Mac
mudns\Scripts\activate.bat         # Windows

# Install dependencies
pip install -r requirements.txt

# Create config files
cp config/config.yaml.template config/config.yaml
cp config/domains.csv.example config/domains.csv
```

---

### Step 2: Get Prisma Access API Credentials (10 minutes)

#### 2.1 Create Service Account

1. Log into **Strata Cloud Manager**
   - URL: https://stratacloudmanager.paloaltonetworks.com/
2. Navigate to: **Settings → Identity & Access → Service Accounts**
3. Click **"Add Service Account"**
4. Configure:
   - **Name**: DNS Configuration Updater
   - **Permissions**:
     - Prisma Access Config: Read & Write
     - Mobile Agent Settings: Read & Write
5. Click **"Save"**
6. **Copy** the Client ID and Client Secret (save them securely)

#### 2.2 Get Tenant Service Group ID

1. Navigate to: **Settings → Service Setup → Tenant Service Group**
2. **Copy** your TSG ID

#### 2.3 Update Configuration File

Edit `config/config.yaml`:

```yaml
api:
  client_id: "your-client-id@1234567890.iam.panserviceaccount.com"
  client_secret: "your-client-secret-here"
  tsg_id: "1234567890"
```

**Test authentication:**
```bash
source mudns/bin/activate  # Activate virtual environment first!
python3 get_token.py
```

If successful, you'll see: `✓ Token obtained`

---

### Step 3: Prepare Your Domain List (5 minutes)

Edit `config/domains.csv` with your internal domains:

```csv
domain
*.internal.company.com
*.corp.company.com
intranet.company.com
*.dev.company.com
mail.corp.company.com
```

**Supported formats:**
- Exact domains: `intranet.company.com`
- Wildcard domains: `*.internal.company.com`
- Subdomains: `mail.corp.company.com`

**Rules:**
- One domain per line
- No spaces, commas, or special characters (except `*` and `.`)
- Optional header row

---

### Step 4: Test with Dry Run (2 minutes)

**Always test first!**

```bash
# Activate virtual environment
source mudns/bin/activate  # Linux/Mac
mudns\Scripts\activate.bat # Windows

# Run dry-run mode
python3 main.py --dry-run --rule-name CustomDNS -v
```

This will:
- Show you exactly what changes will be made
- Display all domains that will be added
- Show which regions will be updated
- **NOT apply any changes**

Review the output carefully!

---

### Step 5: Apply Changes (2 minutes)

Once you're satisfied with the dry-run preview:

```bash
python3 main.py --rule-name CustomDNS -v
```

**What happens:**
1. ✅ Authenticates to Prisma Access
2. ✅ Retrieves current DNS configuration
3. ✅ Creates automatic backup (in `backup/` directory)
4. ✅ Adds CustomDNS rule to all regions
5. ✅ Updates configuration via API
6. ⚠️ **Changes are STAGED, not yet active**

---

### Step 6: Commit Changes in SCM (5 minutes)

**🔴 CRITICAL: You must commit the changes!**

1. **Log into Strata Cloud Manager**
   ```
   https://stratacloudmanager.paloaltonetworks.com/
   ```

2. **Review Pending Changes**
   - Look for "Pending Changes" notification
   - Review the configuration diff

3. **Commit the Configuration**
   - Click "Commit" or "Push Config"
   - Add commit message: "Added CustomDNS rule with custom domains"
   - Wait for commit to complete (may take a few minutes)

4. **Verify Changes**
   - Navigate to: **Workflows → Mobile Users - GP → Setup → Infrastructure Settings**
   - Go to **Client DNS** section
   - Click on each region (worldwide, americas, ip-pool-group-23)
   - Verify CustomDNS rule appears with your domains

**For detailed commit instructions, see:** [COMMIT_CHANGES_GUIDE.md](COMMIT_CHANGES_GUIDE.md)

---

## Usage

### Basic Commands

```bash
# Activate virtual environment first
source mudns/bin/activate  # Linux/Mac
mudns\Scripts\activate.bat # Windows

# Preview changes (dry-run)
python3 main.py --dry-run -v

# Apply changes
python3 main.py -v

# Use custom rule name
python3 main.py --rule-name "MyCompanyDNS" -v

# Quiet mode (less output)
python3 main.py --rule-name CustomDNS
```

### Command-Line Options

```
--dry-run          Preview changes without applying them
--rule-name NAME   DNS rule name (default: CustomDNS)
                   - Creates new rule if it doesn't exist
                   - Updates existing rule if it exists (merges domains)
-v, --verbose      Enable verbose logging
--csv-file PATH    Custom path to domains CSV file
```

---

## Project Structure

```
python-script/
├── main.py                          # Main execution script
├── src/
│   ├── auth.py                      # OAuth2 authentication
│   ├── dns_config.py                # DNS configuration manager
│   ├── csv_handler.py               # CSV domain import
│   └── validator.py                 # Configuration validation
├── config/
│   ├── config.yaml                  # API credentials (user-provided)
│   ├── domains.csv                  # Domain list (user-provided)
│   ├── config.yaml.template         # Configuration template
│   └── domains.csv.example          # Example domain list
├── backup/                          # Automatic configuration backups
├── mudns/                           # Python virtual environment
├── README.md                        # This file
├── QUICKSTART.md                    # 5-minute quick start
├── COMMIT_CHANGES_GUIDE.md          # How to commit in SCM
├── PROJECT_SUMMARY.md               # Complete project documentation
├── setup.sh / setup.bat             # Automated setup scripts
└── requirements.txt                 # Python dependencies
```

---

## How It Works

### 1. Authentication

The script uses OAuth2 service account authentication:
- Obtains bearer token from Prisma Access
- Token is valid for 15 minutes
- Automatically handles Prisma Access-only deployments

### 2. Configuration Retrieval

Retrieves current Mobile Users infrastructure settings:
```
GET /sse/config/v1/mobile-agent/infrastructure-settings
```

Returns configuration for all regions including DNS rules.

### 3. DNS Rule Addition

For each region (worldwide, americas, ip-pool-group-23):
- Adds new "CustomDNS" rule with your domains
- **Preserves DNS servers from each region's existing configuration** (each region may have different DNS servers)
- Preserves all existing DNS rules (no changes to CumminsDNS, etc.)
- When updating existing rules, only appends domains - never modifies DNS IP addresses

### 4. Configuration Update

Updates configuration via API:
```
PUT /sse/config/v1/mobile-agent/infrastructure-settings?id={config_id}
```

Changes are **staged** but not committed.

### 5. Manual Commit Required

Changes must be manually committed in Strata Cloud Manager to become active.

---

## Safety Features

### Automatic Backups

Before any changes, a backup is created:
```
backup/dns_config_backup_YYYYMMDD_HHMMSS.json
```

### Dry-Run Mode

Test changes before applying:
```bash
python3 main.py --dry-run -v
```

### Validation

- Domain format validation
- Configuration structure validation
- Credential validation
- API response validation

### Detailed Logging

Verbose mode shows:
- Authentication steps
- API requests and responses
- Configuration changes
- Error details

---

## Troubleshooting

### Authentication Fails

**Problem**: `Authentication failed` or `Invalid credentials`

**Solution**:
1. Verify credentials in `config/config.yaml`
2. Check service account has correct permissions
3. Verify TSG ID is correct
4. Test with: `python3 get_token.py`

---

### Module Not Found Error

**Problem**: `ModuleNotFoundError: No module named 'prisma_sase'`

**Solution**:
```bash
# Activate virtual environment
source mudns/bin/activate  # Linux/Mac
mudns\Scripts\activate.bat # Windows

# Install dependencies
pip install -r requirements.txt
```

---

### Invalid Domains Error

**Problem**: `Invalid domain format` or `Domain validation failed`

**Solution**:
- Check CSV format: one domain per line
- Ensure no special characters (except `*` and `.`)
- Remove any commas, spaces, or quotes
- Verify domains are valid DNS names

---

### API Error 403 (Forbidden)

**Problem**: `403 - Access denied`

**Solution**:
- Service account needs "Mobile Agent Settings: Read & Write" permission
- Verify permissions in SCM: Settings → Identity & Access → Service Accounts

---

### Changes Not Appearing in UI

**Problem**: Script succeeded but changes don't show in SCM

**Solution**:
- **You must commit the changes!** See [COMMIT_CHANGES_GUIDE.md](COMMIT_CHANGES_GUIDE.md)
- Configuration is updated but not committed automatically
- Log into SCM and click "Commit" or "Push Config"

---

## FAQ

**Q: Will this affect existing DNS rules?**

A: No. The script adds a new rule ("CustomDNS") and preserves all existing rules like "CumminsDNS".

**Q: Can I run this multiple times?**

A: Yes. If the rule already exists, it will update the domain list (merge new domains with existing ones).

**Q: Can I use different rule names with `--rule-name`?**

A: Yes! The `--rule-name` option lets you create/update rules with custom names:
- If a rule with that name EXISTS → updates it (merges domains)
- If a rule with that name DOESN'T EXIST → creates a new rule with that name
- Example: `--rule-name "MyCompanyDNS"` creates a rule named "MyCompanyDNS"
- You can have multiple rules (CustomDNS, MyCompanyDNS, OfficeNetworks, etc.)

**Q: What if I want to remove domains?**

A: This script only adds domains. To remove, manually edit in SCM or modify the script.

**Q: Does this work with Panorama?**

A: No. This script is specifically for **Prisma Access managed by Strata Cloud Manager**, not on-premise Panorama.

**Q: Can I customize the DNS servers?**

A: The script uses DNS servers from your existing configuration. To use different servers, modify the code in `src/dns_config.py`.

**Q: What about Public DNS settings?**

A: The current implementation focuses on Internal DNS rules. Public DNS settings are not modified.

---

## Support

### Documentation

- [QUICKSTART.md](QUICKSTART.md) - 5-minute setup guide
- [COMMIT_CHANGES_GUIDE.md](COMMIT_CHANGES_GUIDE.md) - How to commit changes
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Complete project documentation

### External Resources

- Prisma SASE SDK: https://github.com/PaloAltoNetworks/prisma-sase-sdk-python
- SCM API Docs: https://pan.dev/scm/api/
- Prisma Access Docs: https://docs.paloaltonetworks.com/prisma-access

---

## License

This tool is provided as-is for Prisma Access customers. Use at your own risk.

---

## Version History

### v1.0 - 2025-10-29
- ✅ Initial production release
- ✅ Full implementation of Mobile Agent Infrastructure Settings API
- ✅ Support for all regions
- ✅ Automatic backups
- ✅ Dry-run mode
- ✅ Domain validation
- ✅ Comprehensive error handling

---

**Last Updated:** 2025-10-29
**Status:** Production Ready ✅

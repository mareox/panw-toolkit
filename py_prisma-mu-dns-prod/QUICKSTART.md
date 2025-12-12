# Quick Start Guide - Mobile Users DNS Updater

Get up and running in **5 minutes**!

---

## Step 1: Run Setup Script

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

**Windows:**
```cmd
setup.bat
```

This creates the `mudns` virtual environment and installs dependencies.

---

## Step 2: Configure Credentials

Edit `config/config.yaml`:

```yaml
api:
  client_id: "your-client-id@1234567890.iam.panserviceaccount.com"
  client_secret: "your-secret-here"
  tsg_id: "1234567890"
```

**Where to find these:**
- Log into Strata Cloud Manager: https://stratacloudmanager.paloaltonetworks.com/
- Navigate to: **Settings → Identity & Access → Service Accounts**
- Create a service account with **Mobile Agent Settings: Read & Write** permission

**Test authentication:**
```bash
source mudns/bin/activate  # Activate virtual environment
python3 get_token.py
```

---

## Step 3: Add Your Domains

Edit `config/domains.csv`:

```csv
domain
*.internal.company.com
*.corp.company.com
intranet.company.com
```

**Format:**
- One domain per line
- Wildcards supported: `*.domain.com`
- Optional header row

---

## Step 4: Test (Dry Run)

**ALWAYS test first!**

```bash
# Activate virtual environment
source mudns/bin/activate  # Linux/Mac
mudns\Scripts\activate.bat # Windows

# Run dry-run
python3 main.py --dry-run --rule-name CustomDNS -v
```

Review the output to verify changes look correct.

---

## Step 5: Apply Changes

```bash
python3 main.py --rule-name CustomDNS -v
```

**What happens:**
- ✅ Authenticates to Prisma Access
- ✅ Retrieves current configuration
- ✅ Creates automatic backup
- ✅ Adds CustomDNS rule with your domains to all regions
- ✅ Updates configuration via API
- ⚠️ **Changes are STAGED (not yet active)**

---

## 🔴 Step 6: COMMIT Changes (CRITICAL!)

**The script DOES NOT automatically commit changes!**

### You must manually commit in Strata Cloud Manager:

1. **Log into SCM**
   ```
   https://stratacloudmanager.paloaltonetworks.com/
   ```

2. **Review Pending Changes**
   - Look for "Pending Changes" notification
   - Review the diff

3. **Commit**
   - Click "Commit" or "Push Config"
   - Add message: "Added CustomDNS rule with custom domains"
   - Wait for commit to complete

4. **Verify**
   - Go to: **Workflows → Mobile Users - GP → Setup → Infrastructure Settings**
   - Section: **Client DNS**
   - Check all regions show CustomDNS rule

**For detailed commit instructions:** [COMMIT_CHANGES_GUIDE.md](COMMIT_CHANGES_GUIDE.md)

---

## What This Script Does

1. ✅ Adds DNS rule named "CustomDNS" with your internal domains
2. ✅ Applies to ALL Mobile Users regions (worldwide, americas, ip-pool-group-23)
3. ✅ Preserves existing DNS rules (CumminsDNS, etc.)
4. ✅ Creates automatic backups before changes
5. ✅ **Preserves each region's existing DNS servers** (each region may have different DNS IPs)

**Does NOT:**
- ❌ Modify public DNS settings
- ❌ Remove existing DNS rules
- ❌ Automatically commit changes (you must do this manually!)

---

## Common Commands

```bash
# Always activate virtual environment first!
source mudns/bin/activate  # Linux/Mac
mudns\Scripts\activate.bat # Windows

# Preview changes (recommended first)
python3 main.py --dry-run -v

# Apply changes
python3 main.py -v

# Use custom rule name
python3 main.py --rule-name "MyCompanyDNS" -v

# Quiet mode (less output)
python3 main.py --rule-name CustomDNS
```

---

## Command-Line Options

```
--dry-run          Preview changes without applying
--rule-name NAME   DNS rule name (default: CustomDNS)
                   - Creates new rule if it doesn't exist
                   - Updates existing rule if it exists
-v, --verbose      Enable verbose logging
--csv-file PATH    Custom CSV file path
```

---

## Troubleshooting

### ❌ Authentication Fails

**Problem**: `Authentication failed` or `Invalid credentials`

**Solution**:
- Verify credentials in `config/config.yaml`
- Ensure service account has correct permissions
- Test with: `python3 get_token.py`

---

### ❌ Module Not Found Error

**Problem**: `ModuleNotFoundError: No module named 'prisma_sase'`

**Solution**:
```bash
# Did you activate the virtual environment?
source mudns/bin/activate  # Linux/Mac
mudns\Scripts\activate.bat # Windows

# Then install dependencies
pip install -r requirements.txt
```

---

### ❌ Invalid Domains Error

**Problem**: `Invalid domain format` or `Domain validation failed`

**Solution**:
- Check CSV format: one domain per line
- No special characters (except `*` and `.`)
- No commas, spaces, or quotes
- Example: `*.internal.company.com`

---

### ❌ Changes Don't Appear in SCM UI

**Problem**: Script succeeded but I don't see changes in SCM

**Solution**:
- **You forgot to commit!** This is the most common issue.
- Log into SCM and look for "Pending Changes"
- Click "Commit" or "Push Config"
- See [COMMIT_CHANGES_GUIDE.md](COMMIT_CHANGES_GUIDE.md) for details

---

## Safety Features

✅ **Dry-run mode** - Always test first
✅ **Automatic backups** - Stored in `backup/` folder
✅ **Validation** - Checks everything before applying
✅ **Detailed logs** - See exactly what happens
✅ **Preserves existing rules** - Won't delete CumminsDNS, etc.

---

## Verification Steps

After committing changes in SCM:

1. Navigate to: **Workflows → Mobile Users - GP → Setup → Infrastructure Settings**
2. Go to **Client DNS** section
3. Click on each region:
   - worldwide
   - americas (North america)
   - ip-pool-group-23 (US-Western)
4. Verify each region shows:
   - ✅ CumminsDNS rule (unchanged)
   - ✅ CustomDNS rule (newly added with your 19 domains)

---

## Files Created

After running:
```
backup/dns_config_backup_YYYYMMDD_HHMMSS.json  # Backup of original config
```

---

## Need More Help?

- **Full Documentation**: [README.md](README.md)
- **Commit Guide**: [COMMIT_CHANGES_GUIDE.md](COMMIT_CHANGES_GUIDE.md)
- **Project Summary**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

---

## Quick Checklist

Before running:
- [ ] Virtual environment activated (`source mudns/bin/activate`)
- [ ] Credentials configured in `config/config.yaml`
- [ ] Domains added to `config/domains.csv`
- [ ] Tested with `--dry-run` first
- [ ] Ready to commit changes in SCM after script runs

After running:
- [ ] Script completed successfully (no errors)
- [ ] Backup file created in `backup/` directory
- [ ] Logged into SCM
- [ ] Reviewed pending changes
- [ ] **COMMITTED** changes (this activates them!)
- [ ] Verified CustomDNS appears in all regions

---

**Status:** Production Ready ✅
**Last Updated:** 2025-10-29

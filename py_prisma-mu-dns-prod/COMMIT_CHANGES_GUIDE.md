# How to Commit Changes in Strata Cloud Manager

## Important: Changes Must Be Committed!

After running the script successfully (without `--dry-run`), the DNS configuration changes are **staged** in Strata Cloud Manager but **NOT YET ACTIVE**.

You must **manually commit** the changes in SCM for them to take effect.

---

## Steps to Commit Changes

### 1. Log into Strata Cloud Manager

Open your browser and navigate to:
```
https://stratacloudmanager.paloaltonetworks.com/
```

Log in with your credentials.

### 2. Check for Pending Changes

You'll see a notification or indicator showing **pending changes** or **uncommitted configuration**.

Look for:
- A **notification badge** (usually in the top-right corner)
- A **"Push Config"** or **"Commit"** button
- A **configuration status** indicator

### 3. Review Pending Changes

Before committing:

1. Click on the **pending changes** indicator
2. Review the **configuration diff** to see what will be changed
3. Verify that the CustomDNS rule appears in all regions with your domains

### 4. Commit the Configuration

1. Click the **"Commit"** or **"Push Config"** button
2. Add a **commit message** (optional but recommended):
   ```
   Added CustomDNS rule with 19 custom domains to Mobile Users infrastructure settings
   ```
3. Click **"Commit"** or **"Push"** to apply the changes

### 5. Monitor the Commit Status

The commit process may take a few minutes:
- Monitor the commit status in SCM
- Wait for the commit to complete successfully
- Check for any errors or warnings

### 6. Verify Changes Are Active

After the commit completes:

1. Navigate to: **Workflows → Mobile Users - GP → Setup → Infrastructure Settings**
2. Go to the **Client DNS** section
3. Click on each region (worldwide, americas, ip-pool-group-23)
4. Verify that the **CustomDNS** rule appears with your 19 domains

---

## Troubleshooting

### If You Don't See Pending Changes

- The script may have failed to update the configuration
- Check the script output for errors
- Verify the script ran without `--dry-run` flag

### If Commit Fails

Common reasons:
- **Validation errors** in the configuration
- **Conflicting changes** from another admin
- **Insufficient permissions** on your account

Solutions:
- Review the error message in SCM
- Check the backup file created by the script (in `backup/` directory)
- Contact your Prisma Access administrator

### If Changes Don't Appear After Commit

- Wait 5-10 minutes for propagation
- Refresh your browser
- Clear browser cache
- Check if you're looking at the correct folder ("Mobile Users")

---

## Alternative: API-Based Commit

The changes can also be committed via API using the Configuration Operations API:

```bash
# Get your bearer token
export PRISMA_TOKEN="your-access-token-here"

# Commit pending changes
curl -X POST "https://api.sase.paloaltonetworks.com/sse/config/v1/config-versions:commit" \
  -H "Authorization: Bearer $PRISMA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "folders": ["Mobile Users"],
    "description": "Added CustomDNS rule with custom domains"
  }'
```

**Note:** This API endpoint may vary based on your SCM version. Consult the official Strata Cloud Manager API documentation at https://pan.dev/scm/api/

---

## Best Practices

### Before Committing

- ✅ Run the script in **dry-run mode** first to preview changes
- ✅ Review the **backup file** created before update
- ✅ Test during a **maintenance window** if possible
- ✅ Have a **rollback plan** ready

### After Committing

- ✅ Verify changes in SCM UI
- ✅ Test DNS resolution from a GlobalProtect client
- ✅ Monitor for any connectivity issues
- ✅ Document the change in your change management system

---

## Rollback

If you need to rollback the changes:

### Option 1: Manual Rollback in SCM

1. Go to **Configuration → Commits** (or similar)
2. Find the previous commit
3. Revert to that commit

### Option 2: Using the Backup File

The script creates a backup before making changes:
```
backup/dns_config_backup_<timestamp>.json
```

To restore from backup:
1. Locate the backup file
2. Manually restore the configuration through SCM API
3. Commit the reverted changes

---

## Summary

**Remember:**
1. ✅ Run script (without `--dry-run`)
2. ✅ Log into SCM
3. ✅ Review pending changes
4. ✅ **COMMIT** the changes
5. ✅ Verify changes are active

**Without committing, your changes will NOT take effect!**

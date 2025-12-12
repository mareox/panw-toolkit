# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Automated tool to update Prisma Access Mobile Users DNS configuration using the Strata Cloud Manager (SCM) API. This script manages internal domain resolution rules across 18 global regions, supporting bulk domain operations via CSV files.

**Status:** Production Ready ✅

**Python Requirement:** This project **requires Python 3.7 or higher**. Always use `python3` command (not `python`), as some systems default `python` to Python 2.x.

## Essential Commands

### Running the Script

Always use the virtual environment Python interpreter:

```bash
# Activate virtual environment (optional, but recommended)
source mudns/bin/activate  # Linux/Mac
mudns\Scripts\activate.bat # Windows

# Or use virtual environment directly
./mudns/bin/python3 main.py [options]
```

### Core Operations

```bash
# Preview changes without applying (ALWAYS do this first)
./mudns/bin/python3 main.py --dry-run -v

# List all available regions with friendly names
./mudns/bin/python3 main.py --list-regions

# Apply changes to ALL regions
./mudns/bin/python3 main.py -v

# Apply changes to specific regions
./mudns/bin/python3 main.py --regions ip-pool-group-1,ip-pool-group-31,ip-pool-group-2 -v

# View current DNS configuration
./mudns/bin/python3 list_dns_config.py

# Test authentication
python3 get_token.py

# Test Panorama Cloud API (uses panorama_region from config)
python3 test_panorama_api.py
```

### Setup Commands

```bash
# Initial setup (automated)
./setup.sh  # Linux/Mac
setup.bat   # Windows

# Manual setup
python3 -m venv mudns
source mudns/bin/activate
pip install -r requirements.txt
```

## Architecture

### Two-API System

The project interacts with **two separate Palo Alto Networks APIs**:

1. **Strata Cloud Manager (SCM) API** - Primary API
   - Base URL: `https://api.sase.paloaltonetworks.com`
   - Endpoint: `/sse/config/v1/mobile-agent/infrastructure-settings`
   - Auth: Standard OAuth2 `Authorization: Bearer <token>`
   - Purpose: Update Mobile Users DNS configuration
   - Used by: `src/dns_config.py` (all update operations)

2. **Panorama Cloud API** - Secondary API (read-only)
   - Base URL: `https://{panorama_region}.prod.panorama.paloaltonetworks.com`
   - Region configured in: `config/config.yaml` (panorama_region field)
   - Auth: **Non-standard** `x-auth-jwt: <token>` header (NOT `Authorization: Bearer`)
   - Purpose: View/validate GlobalProtect Portal configuration
   - Used by: `test_panorama_api.py`

**CRITICAL:** Panorama Cloud API requires the custom `x-auth-jwt` header, not the standard Bearer token format.

### Authentication Flow

OAuth2 Client Credentials flow handled by `src/auth.py`:
1. SDK authenticates with service account credentials (client_id, client_secret, tsg_id)
2. Token is stored in SDK session
3. Token is extracted and used for direct API calls
4. Token is valid for 15 minutes

**Note:** The prisma-sase SDK may return False for Prisma Access-only deployments (no SD-WAN), but OAuth2 authentication succeeds. This is normal - check for `operator.operator_id` or `_session` attributes.

### Configuration Data Flow

```
config/domains.csv              → CSVHandler.load_domains()
                                → Validate domains
config/config.yaml              → Load API credentials + panorama_region
config/region_mappings.yaml     → Load friendly region names (18 regions)
                                ↓
                         PrismaAuth.authenticate()
                                ↓
                    MobileUsersDNSConfig (initialized with SDK)
                                ↓
                    get_dns_settings() - Fetch current config
                                ↓
                    _process_dns_update() - Merge domains into regions
                                ↓
               Optional: Filter by regions parameter
                                ↓
                    backup_config() - Create backup (if not dry-run)
                                ↓
                    PUT request to SCM API (if not dry-run)
                                ↓
                    **Changes are staged, NOT committed**
                    (Manual commit required in SCM UI)
```

### Region Architecture

The script manages DNS rules across 18 global regions:
- **3 aggregate regions:** worldwide, emea, apac
- **15 specific IP pool groups:** ip-pool-group-1, ip-pool-group-2, ..., ip-pool-group-32

Each region has:
- Internal DNS match rules (list of rules, each with name + domain_list)
- Primary/Secondary DNS servers
- Public DNS configuration

**Region filtering:** Use `--regions` parameter to update specific regions instead of all 18.

**Friendly names:** Technical names (ip-pool-group-1) map to friendly names (US-Eastern) via `config/region_mappings.yaml`.

### DNS Rule Structure

```python
{
    "dns_servers": [
        {
            "name": "ip-pool-group-1",  # Technical region name
            "internal_dns_match": [
                {
                    "name": "CustomDNS",  # Rule name (configurable)
                    "primary": {"dns_server": "10.208.140.13"},
                    "secondary": {"dns_server": "10.213.13.13"},
                    "domain_list": ["*.example.com", "*.internal.company.com"]
                }
            ],
            "primary": "Prisma Access Default",
            "secondary": "Prisma Access Default"
        }
    ]
}
```

## Key Implementation Details

### Module Responsibilities

- **`main.py`**: Entry point, CLI argument parsing, orchestrates workflow, region filtering
- **`src/auth.py`**: OAuth2 authentication, token management, SDK initialization
- **`src/dns_config.py`**: Core DNS operations, API calls, region mapping, configuration updates
- **`src/csv_handler.py`**: CSV parsing, domain validation
- **`src/validator.py`**: Configuration validation
- **Helper scripts** (`list_dns_config.py`, `get_token.py`, etc.): Diagnostics and testing

### Configuration Files

- **`config/config.yaml`**: API credentials + panorama_region (required)
- **`config/domains.csv`**: Domain list to add (required)
- **`config/region_mappings.yaml`**: Technical → Friendly name mappings (optional, enhances output)

### Backup System

Every non-dry-run update creates automatic backup:
- Location: `backup/dns_config_backup_YYYYMMDD_HHMMSS.json`
- Contains: Full configuration snapshot before changes
- Used for: Rollback if needed

### Region Mapping System

Two functions in `src/dns_config.py` handle region names:
- `load_region_mappings()`: Loads from `config/region_mappings.yaml`
- `get_friendly_region_name(technical, mappings)`: Translates technical → friendly

Used in:
- `main.py` --list-regions command
- `dns_config.py` _show_changes_preview() for dry-run output

## Common Workflows

### Adding New Domains

1. Edit `config/domains.csv` with new domains
2. Run dry-run: `./mudns/bin/python3 main.py --dry-run -v`
3. Review output carefully
4. Apply: `./mudns/bin/python3 main.py -v`
5. **COMMIT in SCM UI** (changes are staged, not active)

### Updating Specific Regions

1. List regions: `./mudns/bin/python3 main.py --list-regions`
2. Choose regions (e.g., ip-pool-group-1, ip-pool-group-2)
3. Dry-run: `./mudns/bin/python3 main.py --dry-run --regions ip-pool-group-1,ip-pool-group-2`
4. Apply: `./mudns/bin/python3 main.py --regions ip-pool-group-1,ip-pool-group-2`
5. **COMMIT in SCM UI**

### Testing Changes

```bash
# Before changes: view current config
./mudns/bin/python3 list_dns_config.py > before.txt

# Apply changes with dry-run
./mudns/bin/python3 main.py --dry-run -v

# Apply changes (if satisfied)
./mudns/bin/python3 main.py -v

# After changes: view updated config
./mudns/bin/python3 list_dns_config.py > after.txt

# Compare
diff before.txt after.txt
```

## Critical Behaviors

### Dry-Run Mode (`--dry-run`)
- **Does NOT apply any changes**
- Creates no backup
- Shows preview of what would change
- Safe to run multiple times

### Rule Merging Logic
If DNS rule (e.g., "CustomDNS") already exists in a region:
- **Merges domains** (adds new, keeps existing)
- **Updates** the existing rule
- **Does not create duplicate rules**

If rule doesn't exist:
- **Creates new rule** with provided domains
- **Uses DNS servers from that specific region's existing rules** (preserves each region's unique DNS configuration)

### Region Filtering
- `--regions` parameter filters which regions get updated
- Comma-separated, no spaces: `ip-pool-group-1,ip-pool-group-2`
- Omitting `--regions` updates **ALL 18 regions**
- Validation ensures requested regions exist

### Changes Are Staged, Not Committed
After script success:
1. Configuration is **updated in API**
2. Changes are **STAGED** (pending)
3. **Manual commit required** in SCM UI
4. Until committed, changes are not active

See: `COMMIT_CHANGES_GUIDE.md`

## Troubleshooting

### Virtual Environment Issues
**Always use `python3` (not `python`) and preferably the virtual environment interpreter `./mudns/bin/python3`** to avoid version conflicts and import errors.

The project requires Python 3.7+ and will not work with Python 2.x. On some systems, `python` points to Python 2.x while `python3` points to Python 3.x.

If modules are missing:
```bash
./mudns/bin/python3 -m pip install --upgrade pip
./mudns/bin/python3 -m pip install -r requirements.txt
```

### Authentication Failures
1. Verify credentials in `config/config.yaml`
2. Test: `python3 get_token.py`
3. Check service account permissions in SCM
4. Ensure TSG ID is correct

### Panorama API 401 Errors
Panorama uses `x-auth-jwt` header, not `Authorization: Bearer`. Check `test_panorama_api.py` for correct header format (lines 55-62).

### Changes Not Appearing
You must **commit changes in SCM UI** after running the script. Configuration updates are staged but not committed automatically.

## Documentation References

- **README.md**: Complete user documentation
- **QUICKSTART.md**: 5-minute setup guide
- **REGION_SELECTION_GUIDE.md**: Region filtering documentation
- **COMMIT_CHANGES_GUIDE.md**: How to commit changes in SCM
- **PROJECT_STATUS.md**: Current project status, features, testing
- **SESSION_SUMMARY_2025-10-29.md**: Recent development session notes

## Important Constraints

1. **Always use `python3` command** - Never use `python` (may point to Python 2.x). Project requires Python 3.7+
2. **Never hardcode credentials** - Always read from `config/config.yaml`
3. **Always create backups** - Except during dry-run
4. **Respect region filtering** - Process only requested regions
5. **Use correct auth headers** - SCM uses Bearer, Panorama uses x-auth-jwt
6. **Preserve existing rules** - Merge domains, don't overwrite
7. **Validate before applying** - Use dry-run mode first
8. **Use virtual environment** - Prevents dependency conflicts (prefer `./mudns/bin/python3`)

# Implementation Checklist

Follow this checklist to successfully deploy the Prisma Access Mobile Users DNS updater.

## Phase 1: Setup (15 minutes)

- [ ] **Install Python 3.7+**
  - Check version: `python3 --version`
  - Install if needed from python.org

- [ ] **Run setup script**
  - Linux/Mac: `./setup.sh`
  - Windows: `setup.bat`

- [ ] **Verify installation**
  - Check virtual environment created: `ls mudns/`
  - Check dependencies installed: `pip list | grep prisma`

## Phase 2: Configure Credentials (10 minutes)

- [ ] **Create Service Account in Prisma Access**
  1. Go to: Settings > Identity & Access > Service Accounts
  2. Click "Add Service Account"
  3. Name: "DNS Configuration Updater"
  4. Scope: Select required permissions
  5. Copy Client ID and Client Secret

- [ ] **Get TSG ID**
  - Navigate to: Settings > Service Setup
  - Copy Tenant Service Group ID

- [ ] **Update config.yaml**
  ```bash
  cp config/config.yaml.template config/config.yaml
  nano config/config.yaml
  ```
  - Add Client ID
  - Add Client Secret
  - Add TSG ID

- [ ] **Test authentication**
  ```bash
  python discover_api.py
  ```
  - Should authenticate successfully
  - Review output for available endpoints

## Phase 3: API Discovery (30-60 minutes)

### Option A: Using discover_api.py

- [ ] **Run discovery script**
  ```bash
  python discover_api.py -o discovery_results.json
  ```

- [ ] **Review results**
  ```bash
  cat discovery_results.json | python -m json.tool | less
  ```

- [ ] **Identify DNS endpoints**
  - Look for DNS-related keys
  - Note the structure of configuration
  - Document endpoint names

### Option B: Using Browser DevTools (Recommended)

- [ ] **Open Prisma Access UI in browser**
  - Press F12 to open DevTools
  - Go to Network tab
  - Clear network log

- [ ] **Navigate to DNS settings**
  - Settings > Mobile Users > Infrastructure > DNS Settings
  - OR Settings > GlobalProtect > Infrastructure Settings

- [ ] **Capture API calls**
  - Watch Network tab for XHR/Fetch requests
  - Look for GET requests (current config)
  - Click Edit to trigger PUT/POST requests
  - Note the exact URLs and payloads

- [ ] **Document findings**
  - Endpoint URL: ____________________
  - HTTP Method: ____________________
  - Request structure: (copy JSON)
  - Response structure: (copy JSON)

## Phase 4: Code Customization (30-45 minutes)

- [ ] **Update src/dns_config.py**

- [ ] **Modify get_dns_settings() method**
  - Line ~45: Replace placeholder with actual endpoint
  - Test: Should return current DNS config

- [ ] **Modify update_dns_config() method**
  - Line ~120: Replace with actual update endpoint
  - Use PUT or POST as appropriate

- [ ] **Modify _process_dns_update() method**
  - Line ~140+: Update to match actual API structure
  - Ensure it creates correct JSON format

- [ ] **Test reading configuration**
  ```python
  # Quick test script
  python -c "
  from src.auth import PrismaAuth
  from src.dns_config import MobileUsersDNSConfig
  import yaml

  config = yaml.safe_load(open('config/config.yaml'))
  auth = PrismaAuth(**config['api'])
  sdk = auth.authenticate()

  dns = MobileUsersDNSConfig(sdk)
  current = dns.get_dns_settings()
  print(current)
  "
  ```

## Phase 5: Domain Configuration (10 minutes)

- [ ] **Create domains.csv**
  ```bash
  cp config/domains.csv.example config/domains.csv
  nano config/domains.csv
  ```

- [ ] **Add your internal domains**
  - One domain per line
  - Use wildcards where needed (*.internal.company.com)
  - Remove example domains

- [ ] **Validate domain format**
  ```python
  from src.csv_handler import CSVHandler
  domains = CSVHandler.load_domains('config/domains.csv')
  CSVHandler.validate_domains(domains)
  print(f"Loaded {len(domains)} valid domains")
  ```

## Phase 6: Testing (30 minutes)

- [ ] **Test with dry-run**
  ```bash
  python main.py --dry-run -v
  ```

- [ ] **Verify dry-run output**
  - Authentication successful?
  - Domains loaded correctly?
  - Configuration structure looks correct?
  - No errors thrown?

- [ ] **Review proposed changes**
  - CustomDNS rule will be created?
  - Correct number of domains?
  - Public DNS will change to Prisma Access Default?

- [ ] **Test on non-production (if available)**
  - Configure separate config.yaml for test environment
  - Run without dry-run flag
  - Verify in UI
  - Rollback if issues

## Phase 7: Production Deployment (30 minutes)

- [ ] **Create manual backup**
  - Document current DNS settings
  - Screenshot configuration in UI
  - Export configuration if possible

- [ ] **Schedule maintenance window**
  - Coordinate with stakeholders
  - Plan for potential rollback
  - Have support contacts ready

- [ ] **Run final dry-run**
  ```bash
  python main.py --dry-run -v --log-file pre_deployment_check.log
  ```

- [ ] **Apply changes**
  ```bash
  python main.py -v --log-file production_deployment.log
  ```

- [ ] **Verify in UI**
  - Login to Prisma Access UI
  - Navigate to DNS settings
  - Confirm CustomDNS rule exists
  - Verify all domains listed
  - Check Public DNS = Prisma Access Default

- [ ] **Test functionality**
  - Connect mobile user client
  - Test internal domain resolution
  - Verify public domain resolution works
  - Check DNS query logs if available

## Phase 8: Documentation & Handoff (15 minutes)

- [ ] **Document deployment**
  - Date and time deployed
  - Version of script used
  - Number of domains configured
  - Any issues encountered

- [ ] **Save logs and backups**
  ```bash
  # Copy to permanent location
  cp logs/production_deployment.log /path/to/archive/
  cp backup/dns_config_backup_*.json /path/to/archive/
  ```

- [ ] **Create runbook**
  - How to add new domains
  - How to modify configuration
  - How to rollback if needed
  - Support contacts

- [ ] **Train team members**
  - Show how to use the script
  - Explain dry-run testing
  - Demonstrate rollback procedure

## Rollback Procedure

If something goes wrong:

- [ ] **Stop immediately**
  ```bash
  # Ctrl+C if script is running
  ```

- [ ] **Restore from backup**
  ```python
  # Use latest backup file
  python -c "
  import json
  from src.auth import PrismaAuth
  from src.dns_config import MobileUsersDNSConfig
  import yaml

  config = yaml.safe_load(open('config/config.yaml'))
  auth = PrismaAuth(**config['api'])
  sdk = auth.authenticate()

  dns = MobileUsersDNSConfig(sdk)

  # Load backup
  with open('backup/dns_config_backup_TIMESTAMP.json') as f:
      backup = json.load(f)

  # Restore
  sdk.post.servicesetup(backup)  # Adjust endpoint as needed
  "
  ```

- [ ] **Verify rollback in UI**

- [ ] **Document incident**
  - What went wrong
  - Steps taken
  - Resolution

## Troubleshooting Reference

| Issue | Solution |
|-------|----------|
| Authentication fails | Verify credentials in config.yaml |
| Module not found | Run `pip install -r requirements.txt` |
| API endpoint not found | Review API_IMPLEMENTATION_NOTES.md |
| Invalid domain format | Check domains.csv for special characters |
| Configuration not updating | Check service account permissions |
| Changes not visible in UI | Wait 5-10 minutes for replication |

## Success Criteria

- [x] All regions show CustomDNS rule
- [x] All domains from CSV are listed in rule
- [x] Public DNS shows "Prisma Access Default"
- [x] Mobile users can resolve internal domains
- [x] Public domain resolution still works
- [x] No errors in logs
- [x] Backup created successfully

## Completion

- [ ] All checklist items completed
- [ ] Production deployment successful
- [ ] Documentation updated
- [ ] Team trained
- [ ] Backups archived

**Deployment Date:** _________________

**Deployed By:** _________________

**Verified By:** _________________

---

**Notes:**

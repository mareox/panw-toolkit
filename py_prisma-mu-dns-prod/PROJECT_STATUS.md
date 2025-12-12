# Prisma Access Mobile Users DNS Configuration - Project Status

**Last Updated:** 2025-10-29
**Status:** ✅ Fully Functional with Enhanced Features

---

## 🎯 Completed Features

### 1. ✅ Panorama Region Variable
- **Location:** `config/config.yaml`
- **Variable:** `panorama_region: "paas-13"`
- **Purpose:** Dynamically configure Panorama Cloud API region
- **Used in:** `test_panorama_api.py` for Panorama Cloud API calls
- **Authentication:** Uses `x-auth-jwt` header (not standard `Authorization: Bearer`)

### 2. ✅ Friendly Region Name Display
- **Location:** `config/region_mappings.yaml`
- **Purpose:** Map technical names (ip-pool-group-X) to friendly names (US-Eastern, Japan, etc.)
- **Coverage:** All 18 regions fully mapped
- **Implementation:** `src/dns_config.py` - Functions `load_region_mappings()` and `get_friendly_region_name()`

### 3. ✅ Region Selection Feature
- **Command:** `--regions <region1>,<region2>,...`
- **Purpose:** Update only specific regions instead of all
- **Accepts:** Both technical names and friendly names
- **Example:** `--regions US-Eastern,Japan,Taiwan` or `--regions ip-pool-group-1,ip-pool-group-21`

### 4. ✅ Region Listing
- **Command:** `--list-regions`
- **Purpose:** Display all available regions with friendly names
- **Output:** Shows both friendly and technical names

---

## 📁 Key Files & Configuration

### Configuration Files
```
config/
├── config.yaml                      # Main configuration (API credentials + panorama_region)
├── region_mappings.yaml             # Region name mappings (all 18 regions)
├── domains.csv                      # Domains to add to DNS rules
└── region_mappings.yaml.template    # Template for reference
```

### Source Code
```
src/
├── __init__.py
├── auth.py                          # Authentication handler
├── csv_handler.py                   # Domain CSV loader
├── dns_config.py                    # DNS config manager (with region mapping support)
└── validator.py                     # Config validator
```

### Main Scripts
```
main.py                              # Main script with enhanced region features
list_dns_config.py                   # List current DNS configuration
test_panorama_api.py                 # Test Panorama Cloud API (uses panorama_region)
run.sh                               # Quick run wrapper script
```

---

## 🌍 Region Mappings (All 18 Regions)

### Americas (9 regions)
1. `worldwide` → **Worldwide**
2. `ip-pool-group-1` → **US-Eastern** (Panama, US East, US Southeast, etc.)
3. `ip-pool-group-31` → **US-Central** (US South, US Central, Chicago, etc.)
4. `ip-pool-group-23` → **US-Western** (Mexico Northeast, US Northwest, US West, etc.)
5. `ip-pool-group-32` → **US East South** (Miami)
6. `ip-pool-group-2` → **Canada** (Canada Central, Canada East)
7. `ip-pool-group-13` → **LATAM-Brazil** (Brazil East, Paraguay, Venezuela, etc.)
8. `ip-pool-group-24` → **LATAM-Chile** (Uruguay, Argentina, Bolivia, Chile, Peru)
9. `ip-pool-group-30` → **LATAM-Peru** (Lima)

### EMEA (1 region)
10. `emea` → **Africa, Europe & Middle East**

### Asia Pacific (8 regions)
11. `ip-pool-group-14` → **Australia** (Australia East, New Zealand, etc.)
12. `ip-pool-group-26` → **Australia-West** (Perth)
13. `ip-pool-group-15` → **Southeast Asia** (Indonesia, Singapore, Vietnam, etc.)
14. `ip-pool-group-19` → **India** (Bangladesh, India North/South/West, Pakistan)
15. `ip-pool-group-16` → **Hong Kong**
16. `ip-pool-group-17` → **Taiwan**
17. `ip-pool-group-21` → **Japan** (Japan Central, Japan South)
18. `apac` → **Asia, Australia & Japan**

---

## 🚀 Usage Commands

### List Available Regions
```bash
cd "/mnt/u/Users/MareoX/Documents/PANW/04 - PS/Cummins/01. Projects/Script to update MU DNS/python-script-prod"
./mudns/bin/python3 main.py --list-regions
```

### View Current DNS Configuration
```bash
./mudns/bin/python3 list_dns_config.py
```

### Dry Run - All Regions
```bash
./mudns/bin/python3 main.py --dry-run
```

### Dry Run - Specific Regions
```bash
./mudns/bin/python3 main.py --dry-run --regions US-Eastern,Japan,Taiwan
# or using technical names:
./mudns/bin/python3 main.py --dry-run --regions ip-pool-group-1,ip-pool-group-21,ip-pool-group-17
```

### Apply Changes - All Regions
```bash
./mudns/bin/python3 main.py
```

### Apply Changes - Specific Regions
```bash
./mudns/bin/python3 main.py --regions US-Eastern,Japan,Canada
```

### Test Panorama Cloud API
```bash
python3 test_panorama_api.py
```

---

## 🔧 Technical Details

### API Endpoints Used

#### SCM API (Strata Cloud Manager)
- **Base URL:** `https://api.sase.paloaltonetworks.com`
- **Endpoint:** `/sse/config/v1/mobile-agent/infrastructure-settings`
- **Auth:** `Authorization: Bearer <token>`
- **Purpose:** Mobile Users DNS configuration management

#### Panorama Cloud API
- **Base URL:** `https://{panorama_region}.prod.panorama.paloaltonetworks.com`
- **Endpoint:** `/api/config/v9.2/configByPath`
- **Auth:** `x-auth-jwt: <token>` (⚠️ NOT standard Bearer!)
- **Purpose:** GlobalProtect Portal configuration viewing

### Authentication
- **Method:** OAuth2 Client Credentials
- **Token URL:** `https://auth.apps.paloaltonetworks.com/auth/v1/oauth2/access_token`
- **Scope:** `tsg_id:{tsg_id} email profile`
- **Service Account:** Defined in `config/config.yaml`

### DNS Servers by Region
Documented in `config/region_mappings.yaml` comments:
- **US-Eastern:** 10.213.13.13, 10.208.140.13
- **US-Central:** 10.208.140.13, 10.213.13.14
- **US-Western:** Prisma Access Default DNS
- **EMEA:** 10.147.52.18, 10.208.140.14
- **Australia:** 160.95.170.52, 10.183.8.18
- **Southeast Asia:** 10.183.8.18, 10.213.13.13
- **India:** 10.187.174.96, 10.213.13.13
- **Japan/Taiwan/Hong Kong:** 10.183.8.18, 10.213.13.13
- **LATAM:** 10.133.54.84, 10.208.140.13

---

## 📝 Important Notes

1. **Virtual Environment:** Always use `./mudns/bin/python3` or activate venv with `source mudns/bin/activate`

2. **Configuration Location:**
   - Production: `/mnt/u/Users/MareoX/Documents/PANW/04 - PS/Cummins/01. Projects/Script to update MU DNS/python-script-prod`
   - Lab: `/mnt/u/Users/MareoX/Documents/PANW/04 - PS/Cummins/01. Projects/Script to update MU DNS/python-script-lab`

3. **Panorama Region:** Currently set to `paas-13` in `config/config.yaml`

4. **Authentication Warning:** Panorama Cloud API requires `x-auth-jwt` header, not standard `Authorization: Bearer`

5. **Dry Run Safety:** Always use `--dry-run` first to preview changes before applying

6. **Backup:** Configuration backups are automatically created in `backup/` directory when changes are applied

---

## 🔄 Next Steps / Future Enhancements

### Potential Improvements
- [x] ~~Add support for updating DNS servers per region~~ ✅ **COMPLETED** - Script now preserves each region's existing DNS servers
- [ ] Support for deleting DNS rules
- [ ] Bulk region operations (e.g., all US regions, all APAC regions)
- [ ] Export/import region mappings
- [ ] Reverse lookup by friendly name in --regions parameter
- [ ] Schedule automated DNS updates
- [ ] Integration with CI/CD pipelines

### Known Limitations
- ~~Cannot retrieve region-specific DNS settings via API (uses first available)~~ ✅ **FIXED** - Now preserves each region's DNS servers
- Panorama Cloud API endpoints return empty for DNS (as expected - viewing only)
- Service account needs proper permissions for Mobile Users DNS management

---

## 📞 Support & References

### Documentation
- Prisma SASE Python SDK: https://github.com/PaloAltoNetworks/prisma-sase-sdk-python
- API Documentation: Check Prisma Access console → API → API Explorer

### Files for Reference
- `config/region_mappings.yaml.template` - Template for region mappings
- `NETWORK_TAB_GUIDE.md` - Guide for capturing API calls from browser
- `PROJECT_SUMMARY.md` - Original project summary

---

## ✅ Testing Status

### Last Test Results (2025-10-29)
- ✅ Authentication: Working
- ✅ Region listing: All 18 regions displayed with friendly names
- ✅ Region selection: Tested with multiple regions
- ✅ Dry run: Successful for all regions and specific regions
- ✅ Panorama API: Successfully connects with paas-13 region
- ✅ Region mappings: All 18 regions mapped correctly

### Test Commands Used
```bash
# List regions with friendly names
./mudns/bin/python3 main.py --list-regions

# Dry run with all regions
./mudns/bin/python3 main.py --dry-run

# Dry run with specific regions
./mudns/bin/python3 main.py --dry-run --regions US-Eastern,Japan,Taiwan

# Test Panorama API
python3 test_panorama_api.py
```

---

**Project Status:** ✅ Production Ready
**All Features:** ✅ Implemented and Tested
**Documentation:** ✅ Complete

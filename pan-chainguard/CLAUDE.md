# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

pan-chainguard is a Python application for managing root stores and intermediate certificate chains on PAN-OS firewalls. It solves two key problems:

1. **Out-of-date Root Stores**: PAN-OS root stores are only updated in major releases, causing SSL decryption errors when root CAs are missing
2. **Misconfigured Servers**: Many TLS servers don't return proper intermediate certificates, causing certificate chain validation failures

The solution: Create custom root stores from CCADB data (Mozilla, Apple, Chrome, Microsoft) and preload intermediate certificate chains to prevent SSL/TLS errors.

## Architecture

### Core Components

**Data Pipeline Architecture**:
- **CCADB CSV Processing** → **Certificate Filtering** → **Tree Building** → **PAN-OS Import**

The application builds certificate trees using the `treelib` library, where:
- Root certificates are top-level nodes
- Intermediate certificates are child nodes based on `Parent SHA-256 Fingerprint`
- The tree structure enables automated chain validation and preloading

**Key Modules**:
- `pan_chainguard/ccadb.py`: CCADB CSV parsing, certificate validation (revocation, date validity), trust bits evaluation
- `pan_chainguard/util.py`: Tree utilities, fingerprint I/O, certificate archive handling
- `pan_chainguard/mozilla.py`: Mozilla OneCRL (revocation list) integration
- `pan_chainguard/crtsh.py`: crt.sh API client for certificate downloads

### Main Scripts

**sprocket.py** - Root Store Creation
- Processes CCADB All Certificate Information CSV
- Applies policy filters (vendor sources, trust bits, union/intersection operations)
- Outputs root certificate fingerprints as CSV

**chain.py** - Intermediate Chain Discovery
- Input: Root fingerprints CSV + CCADB All Certificate Information CSV
- Builds certificate trees using treelib
- Traverses trees to find all intermediates for each root
- Validates certificates (not revoked, not expired, has SERVER_AUTHENTICATION trust bit)
- Special handling: EXCLUDE_INTERMEDIATES list for problematic roots
- Outputs intermediate fingerprints CSV and optional JSON tree

**link.py** - Certificate Download
- Downloads certificates from crt.sh using aiohttp (async/parallel downloads)
- Input: Fingerprints CSV (roots and/or intermediates)
- Output: tar.gz archive of PEM certificates

**guard.py** - PAN-OS Integration
- Uses pan-python (pan.xapi) for XML API communication
- Manages device certificates and trusted root CA configuration
- Supports both firewall and Panorama (with template/vsys targeting)
- Operations: import, delete, enable/disable trusted CAs, commit
- XPath generation varies by device type/template/vsys context
- Certificate naming: Uses first 26 chars of SHA-256 fingerprint

**chainring.py** - Tree Analysis & Reporting
- Reads JSON tree files
- Generates reports in multiple formats (text, HTML, RST, JSON)
- Certificate lookup by full or partial SHA-256 fingerprint
- Tests for certificate name collisions (26-char prefix conflicts)

**fling.py** - PAN-OS Certificate Export
- Exports existing PAN-OS trusted CAs to tar.gz archive
- Useful for backing up or migrating certificate configurations

## Common Development Commands

### Running Tests

Run all tests from repository root:
```bash
python3 -m unittest discover -v -s tests
```

Run a specific test:
```bash
python3 -m unittest discover -v -s tests -p test_ccadb_date.py
```

From the tests/ directory:
```bash
python3 -m unittest discover -v -t ..
```

### Typical Workflow

1. **Download CCADB data** (CSV files from ccadb.my.salesforce-sites.com)

2. **Create root store**:
```bash
bin/sprocket.py -c AllCertificateRecordsCSVFormatv4.csv \
  -f root-fingerprints.csv \
  --policy '{"sources":["mozilla"],"operation":"union"}'
```

3. **Determine intermediates**:
```bash
bin/chain.py -c AllCertificateRecordsCSVFormatv4.csv \
  -r root-fingerprints.csv \
  -i intermediate-fingerprints.csv \
  --tree cert-tree.json
```

4. **Download certificates**:
```bash
bin/link.py -f root-fingerprints.csv \
  -f intermediate-fingerprints.csv \
  -a certificates.tgz
```

5. **Deploy to PAN-OS**:
```bash
bin/guard.py --tag <panrc-tag> \
  --certs certificates.tgz \
  --type root --type intermediate \
  --update \
  --update-trusted \
  --commit
```

## Important Technical Details

### Certificate Validation Logic

Certificates are filtered/validated at multiple stages:
- **Revocation**: Checks CCADB 'Revocation Status' and 'Revoked But Currently in OneCRL' fields
- **Date validity**: Validates 'Valid From (GMT)' and 'Valid To (GMT)' against current UTC time
- **Trust bits**: For intermediates, requires SERVER_AUTHENTICATION in 'Derived Trust Bits'
- **Root status**: Checks vendor inclusion status in 'Status of Root Cert' field
- **OneCRL**: Mozilla's revocation list for additional intermediate validation

### Certificate Naming Convention

PAN-OS certificates are named using `NAME_PREFIX` + first 26 characters of uppercase SHA-256 fingerprint. The 26-character limit is a PAN-OS constraint. Use `chainring.py --test-collisions` to detect naming conflicts.

### PAN-OS XML API XPath Generation

The `Xpath` class in guard.py generates different XPaths based on:
- Device type (firewall vs Panorama)
- Template (Panorama only)
- Vsys (both firewall and Panorama)

Critical paths:
- `/config/shared/certificate` (firewall shared)
- `/config/shared/ssl-decrypt/trusted-root-CA` (firewall shared trusted roots)
- `/config/panorama/certificate` (Panorama)
- Template paths use `/config/devices/entry[@name='localhost.localdomain']/template/entry[@name='TEMPLATE']/...`

### FIPS-CC Mode Handling

Some certificates are excluded because they use unsupported algorithms in FIPS-CC mode (see `exclude_cert()` in guard.py). Import errors like "Unsupported digest or keys used in FIPS-CC mode" are caught and skipped.

### Policy System

Sprocket.py uses JSON policy for root selection:
```json
{
  "sources": ["mozilla", "chrome", "apple", "microsoft"],
  "operation": "union|intersection",
  "trust_bits": []
}
```

Sources can be combined via union (any vendor) or intersection (all vendors).

### Async/Await Usage

link.py uses asyncio with aiohttp for parallel certificate downloads from crt.sh. The application creates concurrent HTTP requests to maximize download throughput.

## Data Files

**Input files** (from CCADB):
- AllCertificateRecordsCSVFormatv4.csv: All root and intermediate certificates
- AllIncludedRootCertsCSV: Root certificate trust bit settings (optional)
- IntermediateCertsInOneCRLReportCSV: Mozilla OneCRL revocation data (optional)

**Working files**:
- Fingerprint CSV format: `type,sha256` where type is `root` or `intermediate`
- Certificate archives: tar.gz containing PEM files named `{sha256}.pem`
- Tree JSON: Serialized treelib tree structure for analysis

## Testing Approach

Tests use Python's unittest framework and focus on:
- CCADB date parsing and validation (test_ccadb_date.py)
- Certificate validation logic (test_ccadb_misc.py)
- Edge cases: expired certs, revoked certs, invalid dates

## PAN-OS Authentication

All PAN-OS scripts (guard.py, fling.py) require a `.panrc` file with API credentials. Use the `--tag` argument to specify the configuration entry. See pan-python documentation for .panrc format.

## Known Issues

- See TODO.rst for planned improvements
- EXCLUDE_INTERMEDIATES in chain.py (line 247) contains roots where intermediate processing is skipped
- Certificate import can intermittently return status code 7; retry if this occurs
- Template vsys targeting (--vsys with --template) does not work on Panorama (PAN-257229)

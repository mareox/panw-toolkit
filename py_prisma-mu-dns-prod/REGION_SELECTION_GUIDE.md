# Region Selection Guide

## 📍 How to Update Specific Regions / IP Pool Groups

This guide explains how to update DNS configuration for specific regions instead of all 18 global regions.

---

## 🎯 Quick Reference

### **List All Available Regions**
```bash
cd "/mnt/u/Users/MareoX/Documents/PANW/04 - PS/Cummins/01. Projects/Script to update MU DNS/python-script-prod"
./mudns/bin/python3 main.py --list-regions
```

**Output shows both friendly and technical names:**
```
1. Worldwide - worldwide
2. US-Eastern - ip-pool-group-1
3. US-Central - ip-pool-group-31
4. US-Western - ip-pool-group-23
5. Africa, Europe & Middle East - emea
...etc
```

---

## 🔧 Usage Commands

### **Method 1: Using Technical Names (ip-pool-group-X)**

**Dry Run (Preview Only):**
```bash
./mudns/bin/python3 main.py --dry-run --regions ip-pool-group-1,ip-pool-group-31,ip-pool-group-2
```

**Apply Changes:**
```bash
./mudns/bin/python3 main.py --regions ip-pool-group-1,ip-pool-group-31,ip-pool-group-2
```

### **Method 2: Using Friendly Names** (Also Supported)

**Dry Run:**
```bash
./mudns/bin/python3 main.py --dry-run --regions "US-Eastern,US-Central,Canada"
```

**Apply Changes:**
```bash
./mudns/bin/python3 main.py --regions "US-Eastern,US-Central,Canada"
```

---

## 📋 Complete Region Reference

### **Americas Regions**

| Friendly Name | Technical Name | Coverage |
|---------------|----------------|----------|
| Worldwide | `worldwide` | Global/All regions |
| US-Eastern | `ip-pool-group-1` | US East, US Southeast, Panama, Costa Rica, Ecuador, Guatemala, US Northeast, Mexico Central, Colombia |
| US-Central | `ip-pool-group-31` | US South, US Central, Chicago, US Midwest |
| US-Western | `ip-pool-group-23` | US Northwest, US West, Canada West, Mexico West, US Southwest, Mexico Northeast |
| US East South | `ip-pool-group-32` | US-Southeast (Miami) |
| Canada | `ip-pool-group-2` | Canada Central, Canada East |
| LATAM-Brazil | `ip-pool-group-13` | Brazil East, Paraguay, Brazil South, Brazil Central, Venezuela |
| LATAM-Chile | `ip-pool-group-24` | Uruguay, Argentina, Bolivia, Chile, Peru |
| LATAM-Peru | `ip-pool-group-30` | South America West (Lima) |

### **EMEA Regions**

| Friendly Name | Technical Name | Coverage |
|---------------|----------------|----------|
| Africa, Europe & Middle East | `emea` | All EMEA locations |

### **Asia Pacific Regions**

| Friendly Name | Technical Name | Coverage |
|---------------|----------------|----------|
| Asia, Australia & Japan | `apac` | All APAC locations (aggregate) |
| Japan | `ip-pool-group-21` | Japan Central, Japan South |
| Taiwan | `ip-pool-group-17` | Taiwan |
| Hong Kong | `ip-pool-group-16` | Hong Kong |
| India | `ip-pool-group-19` | Bangladesh, India North/West/South, Pakistan South/West |
| Southeast Asia | `ip-pool-group-15` | Indonesia, Singapore, Vietnam, Philippines, Pakistan West (II), Sri Lanka, Myanmar, Malaysia, Cambodia, India South Central, Thailand |
| Australia | `ip-pool-group-14` | New Zealand (Auckland), Australia East, Papua New Guinea, Australia Southeast, New Zealand, Australia South |
| Australia-West | `ip-pool-group-26` | Australia West (Perth) |

---

## 💡 Common Use Cases

### **Example 1: Update Only US Regions**
```bash
# Dry run first
./mudns/bin/python3 main.py --dry-run --regions ip-pool-group-1,ip-pool-group-31,ip-pool-group-23,ip-pool-group-32

# Then apply
./mudns/bin/python3 main.py --regions ip-pool-group-1,ip-pool-group-31,ip-pool-group-23,ip-pool-group-32
```

### **Example 2: Update Only APAC Regions**
```bash
# Dry run first
./mudns/bin/python3 main.py --dry-run --regions ip-pool-group-14,ip-pool-group-15,ip-pool-group-16,ip-pool-group-17,ip-pool-group-19,ip-pool-group-21,ip-pool-group-26

# Then apply
./mudns/bin/python3 main.py --regions ip-pool-group-14,ip-pool-group-15,ip-pool-group-16,ip-pool-group-17,ip-pool-group-19,ip-pool-group-21,ip-pool-group-26
```

### **Example 3: Update Single Region**
```bash
# Dry run for just Japan
./mudns/bin/python3 main.py --dry-run --regions ip-pool-group-21

# Apply to Japan only
./mudns/bin/python3 main.py --regions ip-pool-group-21
```

### **Example 4: Update North America (US + Canada)**
```bash
# Dry run first
./mudns/bin/python3 main.py --dry-run --regions ip-pool-group-1,ip-pool-group-31,ip-pool-group-23,ip-pool-group-32,ip-pool-group-2

# Then apply
./mudns/bin/python3 main.py --regions ip-pool-group-1,ip-pool-group-31,ip-pool-group-23,ip-pool-group-32,ip-pool-group-2
```

### **Example 5: Update ALL Regions (Default Behavior)**
```bash
# If --regions is NOT specified, it updates ALL 18 regions
./mudns/bin/python3 main.py --dry-run
./mudns/bin/python3 main.py
```

---

## 📝 Step-by-Step Workflow

### **Step 1: List Available Regions**
```bash
./mudns/bin/python3 main.py --list-regions
```
Review the output and identify which regions you want to update.

### **Step 2: Prepare Your Domains**
Edit `config/domains.csv` with the domains you want to add:
```csv
domain
*.example.com
*.internal.company.com
api.service.com
```

### **Step 3: Run Dry Run**
```bash
./mudns/bin/python3 main.py --dry-run --regions <region1>,<region2>,<region3>
```

**Example:**
```bash
./mudns/bin/python3 main.py --dry-run --regions ip-pool-group-1,ip-pool-group-31,ip-pool-group-2
```

**Review the output carefully!** It will show:
- Which regions will be updated
- What DNS rule will be created
- What domains will be added
- What DNS servers will be used

### **Step 4: Apply Changes (If Satisfied)**
```bash
./mudns/bin/python3 main.py --regions ip-pool-group-1,ip-pool-group-31,ip-pool-group-2
```

**The script will:**
- ✅ Create automatic backup in `backup/` directory
- ✅ Update only the specified regions
- ✅ Leave all other regions unchanged
- ✅ Display success confirmation

### **Step 5: Verify in Prisma Access Console**
1. Log into Prisma Access console
2. Go to: **Workflows → Prisma Access Setup → Mobile Users → Infrastructure Settings**
3. Click **Client DNS**
4. Select one of the updated regions from dropdown
5. Verify the new DNS rule appears

---

## ⚙️ Advanced Options

### **Combine with Other Parameters**

**Custom Rule Name:**
```bash
./mudns/bin/python3 main.py --regions ip-pool-group-1,ip-pool-group-2 --rule-name "MyCustomDNS"
```

**Different Domains File:**
```bash
./mudns/bin/python3 main.py --regions ip-pool-group-1,ip-pool-group-2 --domains /path/to/other-domains.csv
```

**Verbose Logging:**
```bash
./mudns/bin/python3 main.py --regions ip-pool-group-1,ip-pool-group-2 --verbose
```

**All Options Combined:**
```bash
./mudns/bin/python3 main.py \
  --regions ip-pool-group-1,ip-pool-group-31,ip-pool-group-2 \
  --domains config/domains.csv \
  --rule-name "CustomDNS" \
  --verbose \
  --dry-run
```

---

## 🔍 Troubleshooting

### **"None of the requested regions found"**
**Problem:** You specified a region that doesn't exist.

**Solution:** Run `--list-regions` to see exact region names:
```bash
./mudns/bin/python3 main.py --list-regions
```

### **"Requested regions not found: X, Y"**
**Problem:** Some regions in your list don't exist (typo or incorrect name).

**Solution:** Check the spelling. Use comma-separated values with no spaces around commas:
- ✅ Correct: `ip-pool-group-1,ip-pool-group-2`
- ❌ Wrong: `ip-pool-group-1, ip-pool-group-2` (spaces)
- ❌ Wrong: `ip-pool-group-1 ip-pool-group-2` (no comma)

### **Mixed Technical and Friendly Names**
**Currently:** Only technical names (ip-pool-group-X) are supported in the `--regions` parameter.

**Workaround:** Always use technical names like:
```bash
--regions ip-pool-group-1,ip-pool-group-31,ip-pool-group-2
```

---

## 📊 What Gets Updated vs. What Doesn't

### **When You Specify --regions:**

**✅ Updated:**
- Only the regions you specified
- Creates/updates DNS rule in those regions
- Adds domains to those regions

**❌ NOT Updated:**
- All other regions remain unchanged
- Existing DNS rules in other regions are untouched
- Global settings are preserved

**Example:**
```bash
# This command...
./mudns/bin/python3 main.py --regions ip-pool-group-1,ip-pool-group-2

# ...updates ONLY:
# - ip-pool-group-1 (US-Eastern)
# - ip-pool-group-2 (Canada)

# ...and DOES NOT touch:
# - worldwide
# - ip-pool-group-31
# - emea
# - apac
# - ip-pool-group-14, 15, 16, 17, 19, 21, 23, 24, 26, 30, 32
```

---

## 🎯 Quick Copy-Paste Commands

### **Common Region Combinations:**

**US Only (4 regions):**
```bash
./mudns/bin/python3 main.py --dry-run --regions ip-pool-group-1,ip-pool-group-31,ip-pool-group-23,ip-pool-group-32
```

**North America (5 regions):**
```bash
./mudns/bin/python3 main.py --dry-run --regions ip-pool-group-1,ip-pool-group-31,ip-pool-group-23,ip-pool-group-32,ip-pool-group-2
```

**APAC Only (7 regions):**
```bash
./mudns/bin/python3 main.py --dry-run --regions ip-pool-group-14,ip-pool-group-15,ip-pool-group-16,ip-pool-group-17,ip-pool-group-19,ip-pool-group-21,ip-pool-group-26
```

**LATAM Only (3 regions):**
```bash
./mudns/bin/python3 main.py --dry-run --regions ip-pool-group-13,ip-pool-group-24,ip-pool-group-30
```

**East Asia (3 regions):**
```bash
./mudns/bin/python3 main.py --dry-run --regions ip-pool-group-16,ip-pool-group-17,ip-pool-group-21
```

**All Regions (Default):**
```bash
./mudns/bin/python3 main.py --dry-run
# Note: No --regions parameter means ALL 18 regions
```

---

## ⚠️ Important Notes

1. **Always use `--dry-run` first** to preview changes
2. **Comma-separated, no spaces:** `region1,region2,region3`
3. **Use technical names:** `ip-pool-group-1` (not friendly names in --regions parameter)
4. **Backup is automatic:** Created in `backup/` directory
5. **No --regions = ALL regions:** If you omit `--regions`, it updates all 18 regions
6. **Changes are staged:** Remember to commit/push in Prisma Access console

---

## 📞 Need Help?

**List available regions:**
```bash
./mudns/bin/python3 main.py --list-regions
```

**Show all options:**
```bash
./mudns/bin/python3 main.py --help
```

**Check current DNS config:**
```bash
./mudns/bin/python3 list_dns_config.py
```

---

**Last Updated:** 2025-10-30
**Feature Added:** Region selection with `--regions` parameter

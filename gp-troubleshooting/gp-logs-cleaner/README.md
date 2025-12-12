# GlobalProtect Gateway Log Parser

A comprehensive Python tool for parsing, cleaning, and managing GlobalProtect VPN log files. This script can extract gateway information, remove large gateway lists to reduce file size, and filter logs by time windows.

## Features

- 🔍 **Extract Gateway Information** - Parse and export gateway details from logs
- 🧹 **Clean Log Files** - Remove large gateway lists to reduce file size (50-80% reduction)
- ⏰ **Time-Based Filtering** - Keep only logs from specific time periods
- 📊 **Multiple Export Formats** - CSV, JSON, TXT, or console output
- 🔒 **Safe Operations** - Automatic backup creation before modifications
- 🖥️ **Interactive Mode** - User-friendly guided interface
- ⚡ **Command Line Interface** - Powerful scripting capabilities

## Installation

### Requirements
- Python 3.6 or higher
- No external dependencies (uses only standard library)

### Setup
1. Download `gateway_parser.py` to your desired location
2. Make it executable (optional):
   ```bash
   chmod +x gateway_parser.py
   ```

## Quick Start

### Interactive Mode (Recommended for beginners)
```bash
python3 gateway_parser.py
```
The script will guide you through all options with prompts.

### Command Line Examples
```bash
# Extract gateways to text file
python3 gateway_parser.py logfile.txt -o gateways.txt

# Remove gateway lists (reduce file size)
python3 gateway_parser.py logfile.txt --remove-gateways

# Filter logs to last 24 hours
python3 gateway_parser.py logfile.txt --recent "1d" --filtered-log recent.txt

# Combine operations: extract, clean, and filter
python3 gateway_parser.py logfile.txt --remove-gateways --recent "2h" -o gateways.csv -f csv
```

## Usage Guide

### 1. Gateway Information Extraction

Extract and analyze gateway configurations from your logs.

#### Basic Extraction
```bash
# Extract to console
python3 gateway_parser.py logfile.txt

# Extract to text file
python3 gateway_parser.py logfile.txt -o gateways.txt -f txt

# Extract to CSV for spreadsheet analysis
python3 gateway_parser.py logfile.txt -o gateways.csv -f csv

# Extract to JSON for programming
python3 gateway_parser.py logfile.txt -o gateways.json -f json
```

#### Filtering Options
```bash
# Show only authenticated gateways
python3 gateway_parser.py logfile.txt --authenticated-only

# Show only manual gateways
python3 gateway_parser.py logfile.txt --manual-only

# Filter by minimum priority
python3 gateway_parser.py logfile.txt --min-priority 1

# Filter by region
python3 gateway_parser.py logfile.txt --region "US"

# Show summary statistics
python3 gateway_parser.py logfile.txt --summary
```

### 2. Log File Cleanup

Remove large gateway lists to significantly reduce log file size.

#### Basic Cleanup
```bash
# Remove gateways from original file (creates backup)
python3 gateway_parser.py logfile.txt --remove-gateways

# Save cleaned version to new file
python3 gateway_parser.py logfile.txt --remove-gateways --cleaned-log clean_logfile.txt

# Skip backup creation (use with caution)
python3 gateway_parser.py logfile.txt --remove-gateways --no-backup
```

#### Results
- **Before**: Large XML gateway-list with 50+ gateway entries
- **After**: Simple placeholder: `<gateway-list-removed comment="Gateway list removed to reduce log size"/>`
- **Size Reduction**: Typically 50-80% smaller files

### 3. Time-Based Log Filtering

Keep only logs from specific time periods to focus analysis.

#### Time Filtering Options

**Keep logs after specific time (remove older):**
```bash
python3 gateway_parser.py logfile.txt --start-time "07/31/25 10:00" --filtered-log recent.txt
```

**Keep logs before specific time (remove newer):**
```bash
python3 gateway_parser.py logfile.txt --end-time "07/31/25 15:00" --filtered-log older.txt
```

**Keep logs within time window:**
```bash
python3 gateway_parser.py logfile.txt --start-time "07/31/25 09:00" --end-time "07/31/25 11:00" --filtered-log window.txt
```

**Keep only recent logs:**
```bash
# Last 2 hours
python3 gateway_parser.py logfile.txt --recent "2h" --filtered-log last2hours.txt

# Last 3 days
python3 gateway_parser.py logfile.txt --recent "3d" --filtered-log last3days.txt

# Last 30 minutes
python3 gateway_parser.py logfile.txt --recent "30m" --filtered-log last30min.txt
```

#### Supported Time Formats
- `07/31/25 08:59:55` (MM/dd/yy HH:mm:ss)
- `07/31/25 08:59` (MM/dd/yy HH:mm)
- `2025-07-31 08:59:55` (YYYY-MM-dd HH:mm:ss)
- `2025-07-31 08:59` (YYYY-MM-dd HH:mm)
- `07/31/25` (MM/dd/yy - defaults to 00:00:00)
- `2025-07-31` (YYYY-MM-dd - defaults to 00:00:00)

#### Recent Time Formats
- `2h` - 2 hours
- `3d` - 3 days  
- `30m` - 30 minutes
- `1d` - 1 day

### 4. Combined Operations

Perform multiple operations in sequence for comprehensive log management.

```bash
# Extract gateways AND clean log file
python3 gateway_parser.py logfile.txt --remove-gateways -o gateways.txt --cleaned-log clean.txt

# Clean AND filter by time
python3 gateway_parser.py logfile.txt --remove-gateways --recent "1d" --cleaned-log clean.txt --filtered-log filtered.txt

# Complete workflow: extract, clean, filter
python3 gateway_parser.py logfile.txt \
  --remove-gateways \
  --start-time "07/31/25 08:00" \
  --end-time "07/31/25 12:00" \
  -o gateways.csv -f csv \
  --cleaned-log clean.txt \
  --filtered-log window.txt \
  --summary
```

## Interactive Mode Guide

Run without arguments for guided mode:
```bash
python3 gateway_parser.py
```

### Operation Options
1. **Extract gateway information only** - Parse and export gateway data
2. **Remove gateway list from log file** - Clean up log files
3. **Filter logs by time window** - Time-based log filtering
4. **Extract gateways AND clean log file** - Combined operations
5. **Extract gateways AND filter by time** - Combined operations
6. **Remove gateways AND filter by time** - Combined operations
7. **All operations** - Extract, remove gateways, and filter by time

### Interactive Features
- **File validation** - Checks if input files exist
- **Smart defaults** - Suggests reasonable output file names
- **Time range display** - Shows log file time span before filtering
- **Step-by-step guidance** - Clear prompts for each option
- **Format examples** - Shows time format examples when needed

## Command Line Reference

### Basic Arguments
```
python3 gateway_parser.py [input_file] [options]
```

### Gateway Extraction Options
| Option | Description | Example |
|--------|-------------|---------|
| `-o, --output FILE` | Output file path | `-o gateways.txt` |
| `-f, --format FORMAT` | Output format (txt/csv/json) | `-f csv` |
| `--authenticated-only` | Show only authenticated gateways | |
| `--manual-only` | Show only manual gateways | |
| `--min-priority N` | Minimum priority threshold | `--min-priority 1` |
| `--region REGION` | Filter by region | `--region "US"` |
| `--summary` | Show summary statistics | |

### Log Cleanup Options
| Option | Description | Example |
|--------|-------------|---------|
| `--remove-gateways` | Remove gateway list from log | |
| `--cleaned-log FILE` | Output path for cleaned log | `--cleaned-log clean.txt` |

### Time Filtering Options
| Option | Description | Example |
|--------|-------------|---------|
| `--filter-time` | Enable time filtering | |
| `--start-time TIME` | Start time for filtering | `--start-time "07/31/25 10:00"` |
| `--end-time TIME` | End time for filtering | `--end-time "07/31/25 15:00"` |
| `--recent DURATION` | Keep only recent logs | `--recent "2h"` |
| `--filtered-log FILE` | Output path for filtered log | `--filtered-log recent.txt` |

### General Options
| Option | Description | Example |
|--------|-------------|---------|
| `-i, --interactive` | Force interactive mode | |
| `--no-backup` | Skip backup creation | |

## Output Examples

### Gateway Information (Text Format)
```
GlobalProtect Gateway List
==================================================

Description: US East
Gateway: us-east-g-cumminsi.gpsnyyyyycy.gw.gpcloudservice.com
Priority: 1
Authenticated: yes
Manual: yes
Last HIP: 07/31/2025 08:53:33
------------------------------
Description: Ireland
Gateway: ie-cumminsi.gpsnyyyyycy.gw.gpcloudservice.com
Priority: 5
Authenticated: no
Manual: yes
------------------------------
```

### Summary Statistics
```
Gateway Summary:
Total gateways: 73
Authenticated: 1
Manual: 72
Priority distribution: {0: 54, 1: 9, 4: 1, 5: 9}

Top 10 Gateways by Priority:
 1. Ireland              (Priority: 5, Auth: ✗)
 2. Japan Central        (Priority: 5, Auth: ✗)
 3. South Korea          (Priority: 5, Auth: ✗)
 4. Netherlands Central  (Priority: 5, Auth: ✗)
 5. France North         (Priority: 5, Auth: ✗)
```

### Time Filtering Results
```
Time-based filtering complete:
Total log lines: 15,432
Lines kept: 3,241
Lines removed: 12,191 (79.0% reduction)
Start time: 07/31/25 10:00:00
End time: 07/31/25 12:00:00
Filtered log saved to: window_logs.txt
```

## File Safety

### Automatic Backups
The script automatically creates backups before modifying files:
- Format: `original_file.backup_YYYYMMDD_HHMMSS`
- Example: `logfile.txt.backup_20250804_143022`
- Skip with `--no-backup` flag (use with caution)

### File Validation
- Checks if input files exist before processing
- Validates output directory permissions
- Handles file encoding issues gracefully

## Troubleshooting

### Common Issues

**"No gateway-list found in log file"**
- The log file doesn't contain XML gateway information
- Check if you're using the correct log file
- Some log files may not have gateway data

**"Invalid time format"**
- Use supported time formats (see Time Formats section)
- Examples: `07/31/25 10:00` or `2025-07-31 10:00`
- Check that day/month values are valid

**"File not found"**
- Verify the file path is correct
- Use quotes around paths with spaces: `"path with spaces/file.txt"`
- Check file permissions

**"Permission denied"**
- Ensure you have read access to input files
- Check write permissions for output directory
- On Windows, close the file if it's open in another program

### Performance Tips

**Large Log Files (>100MB)**
- Use time filtering to reduce processing time
- Process in smaller chunks if memory issues occur
- Consider using SSD storage for better I/O performance

**Batch Processing**
- Use command line mode for processing multiple files
- Create shell scripts for repetitive tasks
- Consider parallel processing for multiple files

## Advanced Examples

### Batch Processing Script (Bash)
```bash
#!/bin/bash
# Process all log files in directory
for logfile in *.txt; do
    echo "Processing $logfile..."
    python3 gateway_parser.py "$logfile" \
        --remove-gateways \
        --recent "1d" \
        --cleaned-log "clean_$logfile" \
        --filtered-log "recent_$logfile" \
        -o "gateways_$logfile.csv" -f csv
done
```

### PowerShell Batch Processing
```powershell
# Process all log files in directory
Get-ChildItem *.txt | ForEach-Object {
    Write-Host "Processing $($_.Name)..."
    python gateway_parser.py $_.FullName `
        --remove-gateways `
        --recent "1d" `
        --cleaned-log "clean_$($_.Name)" `
        --filtered-log "recent_$($_.Name)" `
        -o "gateways_$($_.BaseName).csv" -f csv
}
```

### Log Analysis Workflow
```bash
# 1. Extract all gateway information for analysis
python3 gateway_parser.py full_log.txt -o all_gateways.csv -f csv --summary

# 2. Create time-filtered logs for incident investigation
python3 gateway_parser.py full_log.txt \
    --start-time "07/31/25 14:00" \
    --end-time "07/31/25 16:00" \
    --filtered-log incident_window.txt

# 3. Clean up original log for archival
python3 gateway_parser.py full_log.txt \
    --remove-gateways \
    --cleaned-log archived_log.txt

# 4. Keep only recent logs for monitoring
python3 gateway_parser.py full_log.txt \
    --recent "24h" \
    --filtered-log monitoring_log.txt
```

## FAQ

**Q: What types of log files does this work with?**
A: Designed for GlobalProtect VPN client logs that contain XML gateway-list sections. The script can parse any text file with GlobalProtect timestamp format.

**Q: Will this work on Windows and Mac?**
A: Yes, the script is cross-platform and works on Windows, Mac, and Linux with Python 3.6+.

**Q: How much space can I save by removing gateway lists?**
A: Typically 50-80% file size reduction, depending on how many gateways are configured. Files with 70+ gateways see the most dramatic reduction.

**Q: Can I undo the changes?**
A: Yes, the script creates automatic backups before modifying files (unless `--no-backup` is used). Restore from the backup file if needed.

**Q: What happens to non-log entries when time filtering?**
A: Lines without timestamps (like XML sections) are preserved regardless of time filters, ensuring log file integrity.

**Q: Can I chain multiple operations?**
A: Yes, you can extract gateways, remove gateway lists, and filter by time in a single command. Operations are performed in sequence.

**Q: Is there a limit to log file size?**
A: No hard limit, but very large files (>1GB) may take longer to process. Consider using time filtering for better performance with large files.

## Support

For issues, questions, or feature requests:
1. Check the troubleshooting section above
2. Verify you're using supported time formats
3. Test with a small sample log file first
4. Check Python version compatibility (3.6+)

## License

This script is provided as-is for log analysis and management purposes. Use responsibly and always maintain backups of important log files.
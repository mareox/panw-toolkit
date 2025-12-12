#!/usr/bin/env python3
"""
GlobalProtect Gateway Log Parser
Extracts and cleans gateway information from GlobalProtect logs
Can also remove gateway lists from log files to reduce file size
"""

import re
import xml.etree.ElementTree as ET
import json
import csv
import argparse
import os
import shutil
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class GatewayParser:
    def __init__(self):
        self.gateways = []
    
    def parse_log_file(self, file_path: str) -> List[Dict]:
        """Parse GlobalProtect log file and extract gateway information"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Find XML gateway-list section
            xml_match = re.search(r'<gateway-list.*?</gateway-list>', content, re.DOTALL)
            if not xml_match:
                print("No gateway-list found in log file")
                return []
            
            xml_content = xml_match.group(0)
            return self._parse_gateway_xml(xml_content)
            
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found")
            return []
        except Exception as e:
            print(f"Error parsing file: {e}")
            return []
    
    def _parse_gateway_xml(self, xml_content: str) -> List[Dict]:
        """Parse the gateway XML section"""
        try:
            root = ET.fromstring(xml_content)
            gateways = []
            
            for entry in root.findall('entry'):
                gateway_info = {}
                
                # Extract key fields
                gateway_info['gateway'] = self._get_text(entry, 'gateway')
                gateway_info['description'] = self._get_text(entry, 'description')
                gateway_info['priority'] = int(self._get_text(entry, 'priority', '0'))
                gateway_info['tunnel'] = self._get_text(entry, 'tunnel')
                gateway_info['manual'] = self._get_text(entry, 'manual')
                gateway_info['authenticated'] = self._get_text(entry, 'authenticated')
                gateway_info['internal'] = self._get_text(entry, 'internal')
                
                # Optional fields
                gateway_info['allow_tunnel'] = self._get_text(entry, 'allow-tunnel')
                gateway_info['last_hip_sent'] = self._get_text(entry, 'last_hip_sent')
                
                gateways.append(gateway_info)
            
            return sorted(gateways, key=lambda x: (x['priority'], x['description']))
            
        except ET.ParseError as e:
            print(f"XML parsing error: {e}")
            return []
    
    def _get_text(self, element: ET.Element, tag: str, default: str = '') -> str:
        """Safely get text from XML element"""
        child = element.find(tag)
        return child.text if child is not None and child.text else default
    
    def remove_gateway_list_from_log(self, input_file: str, output_file: str = None, create_backup: bool = True) -> bool:
        """Remove gateway list from log file and optionally create a cleaned version"""
        try:
            # Read the original file
            with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Create backup if requested
            if create_backup:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = f"{input_file}.backup_{timestamp}"
                shutil.copy2(input_file, backup_file)
                print(f"Backup created: {backup_file}")
            
            # Find and remove gateway-list section
            original_size = len(content)
            
            # Remove gateway-list XML block (replace with placeholder)
            content_cleaned = re.sub(r'<gateway-list.*?</gateway-list>', 
                                   '<gateway-list-removed comment="Gateway list removed to reduce log size"/>', 
                                   content, 
                                   flags=re.DOTALL)
            
            new_size = len(content_cleaned)
            removed_size = original_size - new_size
            
            # Determine output file
            if output_file is None:
                output_file = input_file
            
            # Write cleaned content
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content_cleaned)
            
            print(f"Gateway list removed from log file")
            print(f"Original size: {original_size:,} characters")
            print(f"New size: {new_size:,} characters") 
            print(f"Removed: {removed_size:,} characters ({removed_size/original_size*100:.1f}% reduction)")
            
            if output_file != input_file:
                print(f"Cleaned log saved to: {output_file}")
            else:
                print(f"Original log file updated: {input_file}")
            
            return True
            
        except Exception as e:
            print(f"Error removing gateway list: {e}")
            return False
    
    def parse_log_timestamp(self, log_line: str) -> Optional[datetime]:
        """Parse timestamp from GlobalProtect log line (PanGPS and PanGPA formats)"""
        # PanGPA timestamp format: P2104-T34307 09/24/2025 08:51:52:597
        pangpa_pattern = r'P\d+-T\d+ (\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}:\d{3})'
        match = re.search(pangpa_pattern, log_line)

        if match:
            timestamp_str = match.group(1)
            try:
                # Parse MM/dd/yyyy HH:mm:ss:SSS format
                dt = datetime.strptime(timestamp_str, '%m/%d/%Y %H:%M:%S:%f')
                # Convert microseconds (last 3 digits are milliseconds)
                return dt.replace(microsecond=dt.microsecond * 1000)
            except ValueError:
                try:
                    # Try without microseconds
                    dt = datetime.strptime(timestamp_str[:19], '%m/%d/%Y %H:%M:%S')
                    return dt
                except ValueError:
                    pass

        # PanGPS timestamp format: MM/dd/yy HH:mm:ss:SSS
        pangps_pattern = r'(\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}:\d{3})'
        match = re.search(pangps_pattern, log_line)

        if match:
            timestamp_str = match.group(1)
            try:
                # Parse MM/dd/yy HH:mm:ss:SSS format
                dt = datetime.strptime(timestamp_str, '%m/%d/%y %H:%M:%S:%f')
                # Convert microseconds (last 3 digits are milliseconds)
                return dt.replace(microsecond=dt.microsecond * 1000)
            except ValueError:
                try:
                    # Try without microseconds
                    dt = datetime.strptime(timestamp_str[:17], '%m/%d/%y %H:%M:%S')
                    return dt
                except ValueError:
                    pass

        return None
    
    def filter_logs_by_time(self, input_file: str, start_time: Optional[datetime] = None, 
                           end_time: Optional[datetime] = None, output_file: str = None, 
                           create_backup: bool = True) -> bool:
        """Filter log entries by time window"""
        try:
            # Read the original file
            with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            # Create backup if requested
            if create_backup:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = f"{input_file}.backup_{timestamp}"
                with open(backup_file, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                print(f"Backup created: {backup_file}")
            
            filtered_lines = []
            filtered_count = 0
            total_count = len(lines)
            
            for line in lines:
                log_time = self.parse_log_timestamp(line)
                
                # If we can't parse timestamp, keep the line (non-log entries like XML)
                if log_time is None:
                    filtered_lines.append(line)
                    continue
                
                # Apply time filters
                keep_line = True
                
                if start_time and log_time < start_time:
                    keep_line = False
                
                if end_time and log_time > end_time:
                    keep_line = False
                
                if keep_line:
                    filtered_lines.append(line)
                else:
                    filtered_count += 1
            
            # Determine output file
            if output_file is None:
                output_file = input_file
            
            # Write filtered content
            with open(output_file, 'w', encoding='utf-8') as f:
                f.writelines(filtered_lines)
            
            kept_count = total_count - filtered_count
            
            print(f"Time-based filtering complete:")
            print(f"Total log lines: {total_count:,}")
            print(f"Lines kept: {kept_count:,}")
            print(f"Lines removed: {filtered_count:,} ({filtered_count/total_count*100:.1f}%)")
            
            if start_time:
                print(f"Start time: {start_time.strftime('%m/%d/%y %H:%M:%S')}")
            if end_time:
                print(f"End time: {end_time.strftime('%m/%d/%y %H:%M:%S')}")
            
            if output_file != input_file:
                print(f"Filtered log saved to: {output_file}")
            else:
                print(f"Original log file updated: {input_file}")
            
            return True
            
        except Exception as e:
            print(f"Error filtering logs by time: {e}")
            return False
    
    def get_log_time_range(self, input_file: str) -> Tuple[Optional[datetime], Optional[datetime]]:
        """Get the time range of logs in the file"""
        try:
            with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            first_time = None
            last_time = None
            
            for line in lines:
                log_time = self.parse_log_timestamp(line)
                if log_time:
                    if first_time is None:
                        first_time = log_time
                    last_time = log_time
            
            return first_time, last_time
            
        except Exception as e:
            print(f"Error getting log time range: {e}")
            return None, None
    
    def filter_gateways(self, gateways: List[Dict], **filters) -> List[Dict]:
        """Filter gateways based on criteria"""
        filtered = gateways
        
        if filters.get('authenticated_only'):
            filtered = [g for g in filtered if g['authenticated'] == 'yes']
        
        if filters.get('manual_only'):
            filtered = [g for g in filtered if g['manual'] == 'yes']
        
        if filters.get('min_priority') is not None:
            filtered = [g for g in filtered if g['priority'] >= filters['min_priority']]
        
        if filters.get('region'):
            region = filters['region'].lower()
            filtered = [g for g in filtered if region in g['description'].lower()]
        
        return filtered
    
    def export_to_csv(self, gateways: List[Dict], output_file: str):
        """Export gateways to CSV format"""
        if not gateways:
            print("No gateways to export")
            return
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=gateways[0].keys())
            writer.writeheader()
            writer.writerows(gateways)
        print(f"Exported {len(gateways)} gateways to {output_file}")
    
    def export_to_json(self, gateways: List[Dict], output_file: str):
        """Export gateways to JSON format"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(gateways, f, indent=2, ensure_ascii=False)
        print(f"Exported {len(gateways)} gateways to {output_file}")
    
    def export_to_text(self, gateways: List[Dict], output_file: str):
        """Export gateways to clean text format"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("GlobalProtect Gateway List\n")
            f.write("=" * 50 + "\n\n")
            
            for gateway in gateways:
                f.write(f"Description: {gateway['description']}\n")
                f.write(f"Gateway: {gateway['gateway']}\n")
                f.write(f"Priority: {gateway['priority']}\n")
                f.write(f"Authenticated: {gateway['authenticated']}\n")
                f.write(f"Manual: {gateway['manual']}\n")
                if gateway['last_hip_sent']:
                    f.write(f"Last HIP: {gateway['last_hip_sent']}\n")
                f.write("-" * 30 + "\n")
        
        print(f"Exported {len(gateways)} gateways to {output_file}")
    
    def print_summary(self, gateways: List[Dict]):
        """Print summary statistics"""
        if not gateways:
            print("No gateways found")
            return
        
        total = len(gateways)
        authenticated = len([g for g in gateways if g['authenticated'] == 'yes'])
        manual = len([g for g in gateways if g['manual'] == 'yes'])
        priorities = {}
        
        for gateway in gateways:
            priority = gateway['priority']
            priorities[priority] = priorities.get(priority, 0) + 1
        
        print(f"\nGateway Summary:")
        print(f"Total gateways: {total}")
        print(f"Authenticated: {authenticated}")
        print(f"Manual: {manual}")
        print(f"Priority distribution: {dict(sorted(priorities.items()))}")
        
        print(f"\nTop 10 Gateways by Priority:")
        sorted_gateways = sorted(gateways, key=lambda x: x['priority'], reverse=True)
        for i, gateway in enumerate(sorted_gateways[:10], 1):
            auth_status = "✓" if gateway['authenticated'] == 'yes' else "✗"
            print(f"{i:2d}. {gateway['description']:<20} (Priority: {gateway['priority']}, Auth: {auth_status})")


def get_input_file() -> str:
    """Prompt user for input file path"""
    while True:
        file_path = input("\nEnter the path to your GlobalProtect log file: ").strip()
        if not file_path:
            print("Please enter a valid file path.")
            continue
        
        # Handle quoted paths
        file_path = file_path.strip('"').strip("'")
        
        if os.path.exists(file_path):
            return file_path
        else:
            print(f"File not found: {file_path}")
            retry = input("Would you like to try again? (y/n): ").lower()
            if retry != 'y':
                exit(1)


def get_operation_mode() -> str:
    """Prompt user for operation mode"""
    print("\n" + "="*50)
    print("OPERATION MODE")
    print("="*50)
    print("\nWhat would you like to do?")
    print("1. Extract gateway information only")
    print("2. Remove gateway list from log file")
    print("3. Filter logs by time window")
    print("4. Extract gateways AND clean log file")
    print("5. Extract gateways AND filter by time")
    print("6. Remove gateways AND filter by time")
    print("7. All operations - Extract, remove gateways, and filter by time")
    
    while True:
        choice = input("\nSelect operation (1-7): ").strip()
        if choice == '1':
            return 'extract'
        elif choice == '2':
            return 'remove'
        elif choice == '3':
            return 'time_filter'
        elif choice == '4':
            return 'extract_and_remove'
        elif choice == '5':
            return 'extract_and_time'
        elif choice == '6':
            return 'remove_and_time'
        elif choice == '7':
            return 'all'
        else:
            print("Please enter 1-7")


def get_removal_options() -> Dict:
    """Get options for gateway list removal"""
    print("\n" + "="*50)
    print("REMOVAL OPTIONS")
    print("="*50)
    
    # Backup option
    create_backup = input("\nCreate backup before modifying file? (y/n): ").lower() == 'y'
    
    # Output file option
    use_separate_file = input("Save cleaned log to separate file? (y/n): ").lower() == 'y'
    
    output_file = None
    if use_separate_file:
        output_file = input("Enter cleaned log file path (or press Enter for 'cleaned_log.txt'): ").strip()
        if not output_file:
            output_file = 'cleaned_log.txt'
        output_file = output_file.strip('"').strip("'")
    
    return {
        'create_backup': create_backup,
        'output_file': output_file
    }


def parse_time_input(time_str: str) -> Optional[datetime]:
    """Parse user time input in various formats"""
    if not time_str.strip():
        return None
    
    time_str = time_str.strip()
    
    # Try different formats
    formats = [
        '%m/%d/%y %H:%M:%S',      # 07/31/25 08:59:55
        '%m/%d/%y %H:%M',         # 07/31/25 08:59
        '%m/%d/%Y %H:%M:%S',      # 07/31/2025 08:59:55
        '%m/%d/%Y %H:%M',         # 07/31/2025 08:59
        '%Y-%m-%d %H:%M:%S',      # 2025-07-31 08:59:55
        '%Y-%m-%d %H:%M',         # 2025-07-31 08:59
        '%Y-%m-%d',               # 2025-07-31
        '%m/%d/%y',               # 07/31/25
        '%m/%d/%Y',               # 07/31/2025
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(time_str, fmt)
        except ValueError:
            continue
    
    return None


def get_time_filter_options(gp_parser: 'GatewayParser', input_file: str) -> Dict:
    """Get options for time-based filtering"""
    print("\n" + "="*50)
    print("TIME FILTERING OPTIONS")
    print("="*50)
    
    # Show current log time range
    first_time, last_time = gp_parser.get_log_time_range(input_file)
    if first_time and last_time:
        print(f"\nLog file time range:")
        print(f"First entry: {first_time.strftime('%m/%d/%y %H:%M:%S')}")
        print(f"Last entry:  {last_time.strftime('%m/%d/%y %H:%M:%S')}")
        duration = last_time - first_time
        print(f"Duration: {duration}")
    
    print("\nTime filtering options:")
    print("1. Keep logs after a specific time (remove older)")
    print("2. Keep logs before a specific time (remove newer)")
    print("3. Keep logs within a specific time window")
    print("4. Keep only recent logs (last X hours/days)")
    
    while True:
        choice = input("\nSelect time filter (1-4): ").strip()
        if choice in ['1', '2', '3', '4']:
            break
        print("Please enter 1, 2, 3, or 4")
    
    start_time = None
    end_time = None
    
    print("\nTime format examples:")
    print("• 07/31/25 08:59:55")
    print("• 2025-07-31 08:59")
    print("• 07/31/25")
    
    if choice == '1':  # Keep after
        while True:
            time_str = input("\nEnter start time (keep logs after this time): ").strip()
            start_time = parse_time_input(time_str)
            if start_time:
                break
            print("Invalid time format. Please try again.")
    
    elif choice == '2':  # Keep before
        while True:
            time_str = input("\nEnter end time (keep logs before this time): ").strip()
            end_time = parse_time_input(time_str)
            if end_time:
                break
            print("Invalid time format. Please try again.")
    
    elif choice == '3':  # Keep within window
        while True:
            time_str = input("\nEnter start time (beginning of window): ").strip()
            start_time = parse_time_input(time_str)
            if start_time:
                break
            print("Invalid time format. Please try again.")
        
        while True:
            time_str = input("Enter end time (end of window): ").strip()
            end_time = parse_time_input(time_str)
            if end_time and end_time > start_time:
                break
            if end_time and end_time <= start_time:
                print("End time must be after start time.")
            else:
                print("Invalid time format. Please try again.")
    
    elif choice == '4':  # Keep recent
        print("\nKeep recent logs:")
        print("Enter duration (e.g., '2h' for 2 hours, '3d' for 3 days)")
        
        while True:
            duration_str = input("Duration: ").strip().lower()
            try:
                if duration_str.endswith('h'):
                    hours = int(duration_str[:-1])
                    start_time = datetime.now() - timedelta(hours=hours)
                elif duration_str.endswith('d'):
                    days = int(duration_str[:-1])
                    start_time = datetime.now() - timedelta(days=days)
                elif duration_str.endswith('m'):
                    minutes = int(duration_str[:-1])
                    start_time = datetime.now() - timedelta(minutes=minutes)
                else:
                    raise ValueError("Invalid format")
                break
            except ValueError:
                print("Invalid format. Use format like '2h', '3d', '30m'")
    
    # Output file options
    use_separate_file = input("\nSave filtered log to separate file? (y/n): ").lower() == 'y'
    
    output_file = None
    if use_separate_file:
        output_file = input("Enter filtered log file path (or press Enter for 'filtered_log.txt'): ").strip()
        if not output_file:
            output_file = 'filtered_log.txt'
        output_file = output_file.strip('"').strip("'")
    
    # Backup option
    create_backup = input("Create backup before filtering? (y/n): ").lower() == 'y'
    
    return {
        'start_time': start_time,
        'end_time': end_time,
        'output_file': output_file,
        'create_backup': create_backup
    }


def get_output_preferences() -> Dict:
    """Prompt user for output preferences"""
    print("\n" + "="*50)
    print("GATEWAY EXPORT OPTIONS")
    print("="*50)
    
    # Output format selection
    print("\nAvailable output formats:")
    print("1. Text file (.txt) - Human readable format")
    print("2. CSV file (.csv) - Spreadsheet compatible")
    print("3. JSON file (.json) - Structured data format")
    print("4. Console only - Display results on screen")
    
    while True:
        choice = input("\nSelect output format (1-4): ").strip()
        if choice == '1':
            format_type = 'txt'
            break
        elif choice == '2':
            format_type = 'csv'
            break
        elif choice == '3':
            format_type = 'json'
            break
        elif choice == '4':
            format_type = 'console'
            break
        else:
            print("Please enter 1, 2, 3, or 4")
    
    # Get output file path if not console
    output_file = None
    if format_type != 'console':
        while True:
            default_name = f"gateway_export.{format_type}"
            output_file = input(f"\nEnter output file path (or press Enter for '{default_name}'): ").strip()
            
            if not output_file:
                output_file = default_name
            
            # Handle quoted paths
            output_file = output_file.strip('"').strip("'")
            
            # Check if directory exists
            output_dir = os.path.dirname(output_file) if os.path.dirname(output_file) else '.'
            if os.path.exists(output_dir):
                break
            else:
                print(f"Directory does not exist: {output_dir}")
    
    return {'format': format_type, 'file': output_file}


def get_filter_options() -> Dict:
    """Prompt user for filtering options"""
    print("\n" + "="*50)
    print("FILTER OPTIONS (Optional)")
    print("="*50)
    
    filters = {}
    
    # Authenticated only
    auth_only = input("\nShow only authenticated gateways? (y/n): ").lower()
    filters['authenticated_only'] = auth_only == 'y'
    
    # Manual only
    manual_only = input("Show only manual gateways? (y/n): ").lower()
    filters['manual_only'] = manual_only == 'y'
    
    # Minimum priority
    min_priority = input("Enter minimum priority (or press Enter to skip): ").strip()
    if min_priority.isdigit():
        filters['min_priority'] = int(min_priority)
    
    # Region filter
    region = input("Filter by region (or press Enter to skip): ").strip()
    if region:
        filters['region'] = region
    
    # Summary option
    show_summary = input("Show summary statistics? (y/n): ").lower()
    filters['show_summary'] = show_summary == 'y'
    
    return filters


def interactive_mode():
    """Run the parser in interactive mode"""
    print("="*60)
    print("GLOBALPROTECT GATEWAY LOG PARSER")
    print("="*60)
    print("This tool can:")
    print("• Extract gateway information from logs")
    print("• Remove gateway lists to reduce log file size") 
    print("• Filter logs by time window")
    print("• Export data in multiple formats")
    
    # Get input file
    input_file = get_input_file()
    
    # Get operation mode
    operation = get_operation_mode()
    
    # Initialize parser
    gp_parser = GatewayParser()
    
    # Handle different operations
    extract_ops = ['extract', 'extract_and_remove', 'extract_and_time', 'all']
    remove_ops = ['remove', 'extract_and_remove', 'remove_and_time', 'all']
    time_ops = ['time_filter', 'extract_and_time', 'remove_and_time', 'all']
    
    # Gateway extraction
    if operation in extract_ops:
        output_prefs = get_output_preferences()
        filters = get_filter_options()
        
        print("\n" + "="*50)
        print("EXTRACTING GATEWAYS...")
        print("="*50)
        
        print(f"Parsing log file: {input_file}")
        gateways = gp_parser.parse_log_file(input_file)
        
        if gateways:
            filtered_gateways = gp_parser.filter_gateways(gateways, **filters)
            
            print(f"Found {len(gateways)} total gateways")
            if len(filtered_gateways) != len(gateways):
                print(f"After filtering: {len(filtered_gateways)} gateways")
            
            # Show summary if requested
            if filters.get('show_summary'):
                gp_parser.print_summary(filtered_gateways)
            
            # Export or display results
            if output_prefs['format'] == 'console':
                print(f"\nGateway List:")
                print("-" * 50)
                for gateway in filtered_gateways:
                    auth_status = "✓" if gateway['authenticated'] == 'yes' else "✗"
                    print(f"{gateway['description']:<25} | Priority: {gateway['priority']:2d} | Auth: {auth_status}")
            else:
                if output_prefs['format'] == 'csv':
                    gp_parser.export_to_csv(filtered_gateways, output_prefs['file'])
                elif output_prefs['format'] == 'json':
                    gp_parser.export_to_json(filtered_gateways, output_prefs['file'])
                else:  # txt
                    gp_parser.export_to_text(filtered_gateways, output_prefs['file'])
        else:
            print("No gateway information found in the log file.")
    
    # Gateway removal
    if operation in remove_ops:
        removal_opts = get_removal_options()
        
        print("\n" + "="*50)
        print("REMOVING GATEWAY LIST...")
        print("="*50)
        
        success = gp_parser.remove_gateway_list_from_log(
            input_file, 
            removal_opts['output_file'], 
            removal_opts['create_backup']
        )
        
        if not success:
            print("Failed to remove gateway list from log file.")
        else:
            # Update input_file for subsequent operations if we created a new file
            if removal_opts['output_file']:
                input_file = removal_opts['output_file']
    
    # Time-based filtering
    if operation in time_ops:
        time_opts = get_time_filter_options(gp_parser, input_file)
        
        print("\n" + "="*50)
        print("FILTERING LOGS BY TIME...")
        print("="*50)
        
        success = gp_parser.filter_logs_by_time(
            input_file,
            time_opts['start_time'],
            time_opts['end_time'],
            time_opts['output_file'],
            time_opts['create_backup']
        )
        
        if not success:
            print("Failed to filter logs by time.")
    
    print("\nProcessing complete!")


def main():
    parser = argparse.ArgumentParser(description='Parse GlobalProtect gateway logs')
    parser.add_argument('input_file', nargs='?', help='Path to the log file (optional for interactive mode)')
    parser.add_argument('-i', '--interactive', action='store_true',
                       help='Run in interactive mode with prompts')
    parser.add_argument('-o', '--output', help='Output file path')
    parser.add_argument('-f', '--format', choices=['csv', 'json', 'txt'], 
                       default='txt', help='Output format (default: txt)')
    parser.add_argument('--remove-gateways', action='store_true',
                       help='Remove gateway list from log file')
    parser.add_argument('--cleaned-log', help='Output path for cleaned log file')
    parser.add_argument('--filter-time', action='store_true',
                       help='Filter logs by time window')
    parser.add_argument('--start-time', help='Start time for filtering (MM/dd/yy HH:MM:SS)')
    parser.add_argument('--end-time', help='End time for filtering (MM/dd/yy HH:MM:SS)')
    parser.add_argument('--recent', help='Keep only recent logs (e.g., "2h", "3d")')
    parser.add_argument('--filtered-log', help='Output path for time-filtered log file')
    parser.add_argument('--no-backup', action='store_true',
                       help='Do not create backup when modifying files')
    parser.add_argument('--authenticated-only', action='store_true',
                       help='Show only authenticated gateways')
    parser.add_argument('--manual-only', action='store_true',
                       help='Show only manual gateways')
    parser.add_argument('--min-priority', type=int,
                       help='Minimum priority threshold')
    parser.add_argument('--region', help='Filter by region (case-insensitive)')
    parser.add_argument('--summary', action='store_true',
                       help='Show summary statistics')
    
    args = parser.parse_args()
    
    # If no input file provided or interactive flag used, run interactive mode
    if not args.input_file or args.interactive:
        interactive_mode()
        return
    
    # Create parser instance
    gp_parser = GatewayParser()
    current_file = args.input_file
    
    # Handle gateway removal
    if args.remove_gateways:
        print(f"Removing gateway list from: {current_file}")
        success = gp_parser.remove_gateway_list_from_log(
            current_file, 
            args.cleaned_log, 
            not args.no_backup
        )
        if not success:
            return
        
        # Update current file if we created a cleaned version
        if args.cleaned_log:
            current_file = args.cleaned_log
    
    # Handle time filtering
    if args.filter_time or args.start_time or args.end_time or args.recent:
        start_time = None
        end_time = None
        
        # Parse time arguments
        if args.start_time:
            start_time = parse_time_input(args.start_time)
            if not start_time:
                print(f"Invalid start time format: {args.start_time}")
                return
        
        if args.end_time:
            end_time = parse_time_input(args.end_time)
            if not end_time:
                print(f"Invalid end time format: {args.end_time}")
                return
        
        if args.recent:
            try:
                recent_str = args.recent.lower()
                if recent_str.endswith('h'):
                    hours = int(recent_str[:-1])
                    start_time = datetime.now() - timedelta(hours=hours)
                elif recent_str.endswith('d'):
                    days = int(recent_str[:-1])
                    start_time = datetime.now() - timedelta(days=days)
                elif recent_str.endswith('m'):
                    minutes = int(recent_str[:-1])
                    start_time = datetime.now() - timedelta(minutes=minutes)
                else:
                    print(f"Invalid recent format: {args.recent}. Use format like '2h', '3d', '30m'")
                    return
            except ValueError:
                print(f"Invalid recent format: {args.recent}")
                return
        
        # Filter logs by time
        print(f"Filtering logs by time from: {current_file}")
        success = gp_parser.filter_logs_by_time(
            current_file,
            start_time,
            end_time,
            args.filtered_log,
            not args.no_backup
        )
        if not success:
            return
        
        # Update current file if we created a filtered version
        if args.filtered_log:
            current_file = args.filtered_log
        
        # If only filtering by time and no gateway extraction, exit here
        if not args.output:
            return
    
    # Parse the log file for gateway extraction
    print(f"Parsing log file: {current_file}")
    gateways = gp_parser.parse_log_file(current_file)
    
    if not gateways:
        return
    
    # Apply filters
    filters = {
        'authenticated_only': args.authenticated_only,
        'manual_only': args.manual_only,
        'min_priority': args.min_priority,
        'region': args.region
    }
    
    filtered_gateways = gp_parser.filter_gateways(gateways, **filters)
    
    # Show summary if requested
    if args.summary:
        gp_parser.print_summary(filtered_gateways)
    
    # Export results
    if args.output:
        if args.format == 'csv':
            gp_parser.export_to_csv(filtered_gateways, args.output)
        elif args.format == 'json':
            gp_parser.export_to_json(filtered_gateways, args.output)
        else:
            gp_parser.export_to_text(filtered_gateways, args.output)
    else:
        # Print to console
        print(f"\nFound {len(filtered_gateways)} gateways:")
        for gateway in filtered_gateways:
            auth_status = "✓" if gateway['authenticated'] == 'yes' else "✗"
            print(f"{gateway['description']:<25} | Priority: {gateway['priority']:2d} | Auth: {auth_status}")


if __name__ == "__main__":
    main()
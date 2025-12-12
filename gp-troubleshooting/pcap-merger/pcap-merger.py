#!/usr/bin/env python3
"""
PCAP File Merge and Processing Script
This script merges multiple PCAP files, removes duplicates, and creates a summary text file.
Requirements: mergecap, editcap, and tshark (Wireshark tools) must be installed.
"""

import os
import subprocess
import sys
from pathlib import Path


def check_tools():
    """Check if required tools are installed."""
    tools = ['mergecap', 'editcap', 'tshark']
    missing_tools = []
    tool_paths = {}
    
    # Check if tools are in PATH first
    for tool in tools:
        try:
            subprocess.run([tool, '-v'], capture_output=True, check=True)
            tool_paths[tool] = tool  # Use tool name if in PATH
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing_tools.append(tool)
    
    # On Linux, check common installation paths
    if missing_tools and (sys.platform == 'linux' or sys.platform == 'linux2'):
        common_paths = [
            '/usr/bin',
            '/usr/sbin',
            '/usr/local/bin',
            '/usr/local/sbin',
            '/snap/bin'
        ]
        
        print("Tools not found in PATH. Checking common installation directories...")
        
        for tool in missing_tools[:]:  # Create a copy to iterate over
            for path in common_paths:
                tool_path = os.path.join(path, tool)
                if os.path.exists(tool_path):
                    tool_paths[tool] = tool_path
                    missing_tools.remove(tool)
                    print(f"  Found {tool} at: {tool_path}")
                    break
    
    # On Windows, check common Wireshark installation paths
    elif missing_tools and sys.platform == 'win32':
        common_paths = [
            r"C:\Program Files\Wireshark",
            r"C:\Program Files (x86)\Wireshark",
            r"D:\Program Files\Wireshark",
            r"D:\Program Files (x86)\Wireshark"
        ]
        
        print("Tools not found in PATH. Checking common Wireshark installation directories...")
        
        for path in common_paths:
            if os.path.exists(path):
                print(f"Found Wireshark installation at: {path}")
                # Check if all tools exist in this directory
                all_found = True
                temp_paths = {}
                for tool in tools:
                    tool_exe = os.path.join(path, f"{tool}.exe")
                    if os.path.exists(tool_exe):
                        temp_paths[tool] = tool_exe
                    else:
                        all_found = False
                        break
                
                if all_found:
                    tool_paths = temp_paths
                    missing_tools = []
                    print(f"✓ Using Wireshark tools from: {path}")
                    break
    
    if missing_tools:
        print(f"\nError: The following tools are not installed or not in PATH: {', '.join(missing_tools)}")
        print("\n" + "="*60)
        print("Installation Instructions:")
        print("="*60)
        
        # Provide OS-specific installation instructions
        if sys.platform == 'win32':
            print("\nWindows:")
            print("  1. Download Wireshark from https://www.wireshark.org/download.html")
            print("  2. Run the installer and make sure to select 'Install tshark'")
            print("  3. Add Wireshark installation directory to PATH (usually C:\\Program Files\\Wireshark\\)")
            
        elif sys.platform == 'linux' or sys.platform == 'linux2':
            print("\nLinux:")
            
            # Try to detect the distribution
            distro_commands = {
                'debian': "sudo apt-get update && sudo apt-get install -y tshark wireshark-common",
                'ubuntu': "sudo apt-get update && sudo apt-get install -y tshark wireshark-common",
                'fedora': "sudo dnf install -y wireshark-cli",
                'centos': "sudo yum install -y wireshark",
                'rhel': "sudo yum install -y wireshark",
                'arch': "sudo pacman -S wireshark-cli",
                'manjaro': "sudo pacman -S wireshark-cli",
                'opensuse': "sudo zypper install -y wireshark",
                'alpine': "sudo apk add wireshark-tools"
            }
            
            # Try to detect the distribution
            detected_distro = None
            if os.path.exists('/etc/os-release'):
                try:
                    with open('/etc/os-release', 'r') as f:
                        os_release = f.read().lower()
                        for distro in distro_commands:
                            if distro in os_release:
                                detected_distro = distro
                                break
                except:
                    pass
            
            if detected_distro:
                print(f"  Detected {detected_distro.capitalize()}. Run:")
                print(f"  $ {distro_commands[detected_distro]}")
            else:
                print("  For Debian/Ubuntu:")
                print("  $ sudo apt-get update && sudo apt-get install -y tshark wireshark-common")
                print("\n  For RHEL/CentOS/Fedora:")
                print("  $ sudo yum install -y wireshark  # or")
                print("  $ sudo dnf install -y wireshark-cli")
                print("\n  For Arch Linux:")
                print("  $ sudo pacman -S wireshark-cli")
                print("\n  For openSUSE:")
                print("  $ sudo zypper install -y wireshark")
                print("\n  For Alpine Linux:")
                print("  $ sudo apk add wireshark-tools")
            
            print("\n  Note: During tshark installation, you may be asked about allowing")
            print("  non-superusers to capture packets. Select 'Yes' if you want to")
            print("  run captures without sudo.")
            
        elif sys.platform == 'darwin':
            print("\nmacOS:")
            print("  Using Homebrew:")
            print("  $ brew install wireshark")
            print("\n  Using MacPorts:")
            print("  $ sudo port install wireshark3 +cli")
            print("\n  Or download the .dmg from https://www.wireshark.org/download.html")
            
        else:
            print(f"\nUnknown platform: {sys.platform}")
            print("Please install Wireshark/tshark for your operating system.")
        
        print("="*60)
        sys.exit(1)
    
    print("✓ All required tools are available.\n")
    return tool_paths


def get_pcap_files():
    """Prompt user for PCAP files to merge."""
    pcap_files = []
    print("Enter PCAP file paths to merge (one per line).")
    print("Press Enter on an empty line when done:")
    
    while True:
        file_path = input(f"PCAP file {len(pcap_files) + 1}: ").strip()
        
        if not file_path:
            if len(pcap_files) < 2:
                print("Please provide at least 2 PCAP files to merge.")
                continue
            break
        
        # Expand user home directory if present
        file_path = os.path.expanduser(file_path)
        
        if not os.path.isfile(file_path):
            print(f"  ⚠ File not found: {file_path}")
            continue
        
        if not file_path.lower().endswith(('.pcap', '.pcapng', '.cap')):
            print(f"  ⚠ Warning: {file_path} doesn't have a typical PCAP extension")
            use_anyway = input("  Use this file anyway? (y/n): ").lower()
            if use_anyway != 'y':
                continue
        
        pcap_files.append(file_path)
        print(f"  ✓ Added: {file_path}")
    
    return pcap_files


def get_output_filename():
    """Prompt user for the merged output filename."""
    while True:
        filename = input("\nEnter the name for the merged PCAP file (without extension): ").strip()
        
        if not filename:
            print("Please provide a filename.")
            continue
        
        # Remove extension if user provided one
        filename = os.path.splitext(filename)[0]
        
        # Check if file already exists
        if os.path.exists(f"{filename}.pcap"):
            overwrite = input(f"File '{filename}.pcap' already exists. Overwrite? (y/n): ").lower()
            if overwrite != 'y':
                continue
        
        return filename


def run_command(cmd, description):
    """Run a shell command and handle errors."""
    print(f"\n{description}...")
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        if result.stdout:
            print(result.stdout)
        print(f"✓ {description} completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error during {description.lower()}:")
        print(f"  {e.stderr}")
        return False


def main():
    """Main function to orchestrate the PCAP processing workflow."""
    print("=" * 60)
    print("PCAP File Merge and Processing Tool")
    print("=" * 60)
    
    # Check if required tools are installed and get their paths
    tool_paths = check_tools()
    
    # Get input files
    pcap_files = get_pcap_files()
    print(f"\nSelected {len(pcap_files)} files for merging.")
    
    # Get output filename
    base_filename = get_output_filename()
    
    # Define output filenames
    merged_file = f"{base_filename}.pcap"
    dedup_file = f"{base_filename}-d.pcap"
    summary_file = f"{base_filename}-d.txt"
    
    print("\n" + "=" * 60)
    print("Processing Steps:")
    print(f"1. Merge files → {merged_file}")
    print(f"2. Remove duplicates → {dedup_file}")
    print(f"3. Create summary → {summary_file}")
    print("=" * 60)
    
    # Step 1: Merge PCAP files
    merge_cmd = [tool_paths['mergecap'], '-w', merged_file] + pcap_files
    if not run_command(merge_cmd, "Step 1: Merging PCAP files"):
        print("\nProcess aborted due to merge error.")
        return
    
    # Get file size for merged file
    merged_size = os.path.getsize(merged_file) / (1024 * 1024)  # Convert to MB
    print(f"  Merged file size: {merged_size:.2f} MB")
    
    # Step 2: Remove duplicates with editcap
    dedup_cmd = [tool_paths['editcap'], '-d', merged_file, dedup_file]
    if not run_command(dedup_cmd, "Step 2: Removing duplicates"):
        print("\nProcess aborted due to deduplication error.")
        return
    
    # Get file size for deduplicated file
    dedup_size = os.path.getsize(dedup_file) / (1024 * 1024)  # Convert to MB
    print(f"  Deduplicated file size: {dedup_size:.2f} MB")
    print(f"  Size reduction: {merged_size - dedup_size:.2f} MB ({((merged_size - dedup_size) / merged_size * 100):.1f}%)")
    
    # Step 3: Create summary with tshark
    summary_cmd = [tool_paths['tshark'], '-r', dedup_file]
    print(f"\nStep 3: Creating summary file...")
    print(f"Running: {' '.join(summary_cmd)} > {summary_file}")
    
    try:
        with open(summary_file, 'w') as f:
            result = subprocess.run(summary_cmd, stdout=f, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                print(f"✗ Error creating summary:")
                print(f"  {result.stderr}")
                return
        print(f"✓ Step 3: Creating summary file completed successfully.")
        
        # Get line count for summary file
        with open(summary_file, 'r') as f:
            line_count = sum(1 for _ in f)
        print(f"  Summary contains {line_count} packets")
        
    except Exception as e:
        print(f"✗ Error writing summary file: {e}")
        return
    
    # Final summary
    print("\n" + "=" * 60)
    print("✓ Process completed successfully!")
    print(f"\nOutput files created:")
    print(f"  1. Merged PCAP: {merged_file} ({merged_size:.2f} MB)")
    print(f"  2. Deduplicated PCAP: {dedup_file} ({dedup_size:.2f} MB)")
    print(f"  3. Summary text: {summary_file} ({line_count} packets)")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
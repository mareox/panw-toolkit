#!/bin/bash
# Quick run script for Prisma Access DNS Updater

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Change to script directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "mudns" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv mudns
    source mudns/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    source mudns/bin/activate
fi

# Check if config exists
if [ ! -f "config/config.yaml" ]; then
    echo -e "${RED}✗ config/config.yaml not found${NC}"
    echo "Please copy config/config.yaml.template to config/config.yaml and add your credentials"
    exit 1
fi

# Check if domains.csv exists
if [ ! -f "config/domains.csv" ]; then
    echo -e "${RED}✗ config/domains.csv not found${NC}"
    echo "Please copy config/domains.csv.example to config/domains.csv and add your domains"
    exit 1
fi

# Run the script with all arguments passed to this script
python3 main.py "$@"

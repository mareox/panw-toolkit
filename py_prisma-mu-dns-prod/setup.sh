#!/bin/bash

# Setup script for Prisma Access Mobile Users DNS Updater

echo "=========================================="
echo "Prisma Access MU DNS Updater - Setup"
echo "=========================================="
echo ""

# Check Python version
echo "[1/5] Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Create virtual environment
echo ""
echo "[2/5] Creating virtual environment..."
python3 -m venv mudns

# Activate virtual environment
echo ""
echo "[3/5] Activating virtual environment..."
source mudns/bin/activate

# Install dependencies
echo ""
echo "[4/5] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup configuration files
echo ""
echo "[5/5] Setting up configuration files..."

if [ ! -f "config/config.yaml" ]; then
    cp config/config.yaml.template config/config.yaml
    echo "Created config/config.yaml from template"
    echo "⚠️  Please edit config/config.yaml with your API credentials"
else
    echo "config/config.yaml already exists, skipping..."
fi

if [ ! -f "config/domains.csv" ]; then
    cp config/domains.csv.example config/domains.csv
    echo "Created config/domains.csv from example"
    echo "⚠️  Please edit config/domains.csv with your internal domains"
else
    echo "config/domains.csv already exists, skipping..."
fi

# Create directories
mkdir -p logs backup

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit config/config.yaml with your Prisma Access credentials"
echo "2. Edit config/domains.csv with your internal domains"
echo "3. Run a dry-run test:"
echo "   python main.py --dry-run -v"
echo "4. Apply changes:"
echo "   python main.py"
echo ""
echo "To activate the virtual environment in the future:"
echo "   source mudns/bin/activate"
echo ""

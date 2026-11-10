#!/bin/bash
set -e

echo "=== Cat Weight Loss App - AWS Lightsail Setup ==="

# Update system
echo "Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install dependencies
echo "Installing dependencies..."
sudo apt install -y python3-pip python3-venv nginx git nodejs npm

# Clone repository (if not already present)
cd /home/ubuntu
if [ ! -d "cat_weightloss" ]; then
    echo "Cloning repository..."
    git clone https://github.com/hangy1/Cat-weight-loss-plan.git cat_weightloss
fi

cd cat_weightloss

# Setup Python virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Build frontend
echo "Building frontend..."
cd frontend
npm install
npm run build
cd ..

# Setup systemd service
echo "Setting up systemd service..."
sudo cp deploy/catfood.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable catfood
sudo systemctl start catfood

# Setup nginx
echo "Setting up nginx..."
sudo cp deploy/nginx.conf /etc/nginx/sites-available/catfood
sudo ln -sf /etc/nginx/sites-available/catfood /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# Check services
echo ""
echo "=== Deployment Complete! ==="
echo "Checking service status..."
sudo systemctl status catfood --no-pager
echo ""
echo "Your app should now be running!"
echo "Access it at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"

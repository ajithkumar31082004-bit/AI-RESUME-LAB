#!/bin/bash
# ==============================================================================
# AI RESUME LAB — Ubuntu EC2 Automated Server Setup Script
# Run as root or with sudo on a fresh Ubuntu 22.04 / 24.04 LTS instance
# ==============================================================================

set -e

echo "🚀 Starting AI Resume Lab EC2 Provisioning..."

# 1. Update OS packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# 2. Install Python, Nginx, Git, build tools
echo "📦 Installing Python, Nginx, and dependencies..."
sudo apt install -y python3 python3-pip python3-venv nginx git curl ufw

# 3. Create deployment directories
APP_DIR="/home/ubuntu/ai-resume-lab"
mkdir -p "$APP_DIR"
sudo mkdir -p /var/log/gunicorn
sudo chown -R ubuntu:www-data /var/log/gunicorn

# 4. Setup Python Virtual Environment
echo "🐍 Setting up Python virtual environment..."
cd "$APP_DIR/backend" || exit
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 5. Create storage directories
mkdir -p uploads db
chmod 775 uploads db

# 6. Setup Systemd Service
echo "⚙️ Configuring Gunicorn systemd service..."
sudo cp "$APP_DIR/deploy/ai-resume-lab.service" /etc/systemd/system/ai-resume-lab.service
sudo systemctl daemon-reload
sudo systemctl enable ai-resume-lab
sudo systemctl restart ai-resume-lab

# 7. Configure Nginx
echo "🌐 Configuring Nginx reverse proxy..."
sudo cp "$APP_DIR/deploy/nginx.conf" /etc/nginx/sites-available/ai-resume-lab
sudo ln -sf /etc/nginx/sites-available/ai-resume-lab /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# 8. Firewall setup
echo "🔒 Configuring UFW Firewall..."
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

echo "✅ EC2 Backend Setup Complete!"
echo "📍 Test backend health: curl http://localhost/health"

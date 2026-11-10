# AWS Lightsail Deployment Guide

## Cost: $3.50/month (FREE for first 3 months)

This guide will help you deploy your Cat Weight Loss app to AWS Lightsail - the cheapest AWS hosting option.

## Prerequisites

- AWS account
- GitHub repository with your code pushed

## Step 1: Create Lightsail Instance

1. Go to [AWS Lightsail Console](https://lightsail.aws.amazon.com/)
2. Click **"Create instance"**
3. Select:
   - **Platform**: Linux/Unix
   - **Blueprint**: OS Only → Ubuntu 22.04 LTS
   - **Instance plan**: $3.50/month (512 MB RAM, 1 vCPU, 20 GB SSD)
4. Name your instance: `cat-weightloss`
5. Click **"Create instance"**

## Step 2: Configure Networking

1. On the instance page, go to **"Networking"** tab
2. Under **"IPv4 Firewall"**, ensure these ports are open:
   - SSH (22) - Already open by default
   - HTTP (80) - Click **"Add rule"** if not present
   - HTTPS (443) - Optional, for SSL later

## Step 3: Connect and Deploy

1. Click **"Connect using SSH"** on your instance page
2. Once connected, run these commands:

```bash
# Clone your repository
git clone https://github.com/hangy1/Cat-weight-loss-plan.git cat_weightloss
cd cat_weightloss

# Make setup script executable
chmod +x deploy/setup.sh

# Run automated setup
./deploy/setup.sh
```

The setup script will:
- Install all dependencies (Python, Node.js, nginx)
- Set up Python virtual environment
- Install backend dependencies
- Build the frontend
- Configure systemd service for FastAPI
- Configure nginx as reverse proxy
- Start all services

## Step 4: Access Your App

After deployment completes, your app will be available at:
```
http://YOUR_INSTANCE_PUBLIC_IP
```

Find your public IP:
- In Lightsail console, on your instance page
- Or run: `curl http://169.254.169.254/latest/meta-data/public-ipv4`

## Managing Your App

### View backend logs:
```bash
sudo journalctl -u catfood -f
```

### Restart backend:
```bash
sudo systemctl restart catfood
```

### Restart nginx:
```bash
sudo systemctl restart nginx
```

### Update your app:
```bash
cd /home/ubuntu/cat_weightloss
git pull
source .venv/bin/activate
pip install -r requirements.txt
cd frontend
npm install
npm run build
cd ..
sudo systemctl restart catfood
```

## Database Location

SQLite database is stored at:
```
/home/ubuntu/cat_weightloss/data/catfood.db
```

## Backup Your Database

```bash
# Create backup
cp /home/ubuntu/cat_weightloss/data/catfood.db ~/catfood_backup_$(date +%Y%m%d).db

# Download to your local machine using Lightsail console
# Go to instance → "Connect" → "Download" or use SFTP
```

## Optional: Add Custom Domain

1. In Lightsail, go to **"Networking"** → **"Create static IP"**
2. Attach it to your instance
3. In your domain registrar, add an A record pointing to the static IP
4. Update nginx config to use your domain name

## Optional: Add SSL Certificate (Free)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate (replace with your domain)
sudo certbot --nginx -d yourdomain.com

# Auto-renewal is configured automatically
```

## Troubleshooting

### Backend not starting:
```bash
sudo systemctl status catfood
sudo journalctl -u catfood -n 50
```

### Nginx errors:
```bash
sudo nginx -t
sudo journalctl -u nginx -n 50
```

### Can't access app:
1. Check Lightsail firewall has port 80 open
2. Check services are running:
   ```bash
   sudo systemctl status catfood
   sudo systemctl status nginx
   ```

## Cost Optimization

- **First 3 months**: FREE (one-time Lightsail offer)
- **After 3 months**: $3.50/month
- **Data transfer**: 1 TB included
- No hidden charges with Lightsail fixed pricing

## Upgrading Instance

If you need more resources later:
1. Create snapshot of current instance
2. Create new instance from snapshot with higher plan
3. Costs: $5/month (1 GB RAM), $10/month (2 GB RAM), etc.

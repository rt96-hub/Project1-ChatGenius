# EC2 Setup Guide for Docker and Auth0

This guide assumes you have:
- An EC2 instance running
- Docker and docker-compose installed
- A working docker-compose.yml with three containers: frontend, backend, and database
- Auth0 account and configuration

## 1. Installing Required Software

```bash
# Update package list
sudo apt update

# Install nginx and certbot
sudo apt install nginx certbot python3-certbot-nginx
```

## 2. Configure Nginx

Create a new Nginx configuration file:
```bash
sudo nano /etc/nginx/sites-available/your-app
```

Add the following configuration (replace `YOUR_IP` with your EC2's public IP):
```nginx
server {
    listen 80;
    server_name YOUR_IP.nip.io;
    
    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site and test the configuration:
```bash
sudo ln -s /etc/nginx/sites-available/your-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 3. Set Up SSL Certificate

Get an SSL certificate using Let's Encrypt:
```bash
sudo certbot --nginx -d YOUR_IP.nip.io
```

This will automatically modify your Nginx configuration to handle HTTPS.

## 4. Configure Security Groups

In the AWS Console:
1. Go to EC2 > Security Groups
2. Select your instance's security group
3. Add inbound rules:
   - HTTP (Port 80)
   - HTTPS (Port 443)
   - SSH (Port 22)
   - Any custom ports your application needs

## 5. Update Auth0 Configuration

In your Auth0 dashboard:
1. Go to Applications > Your Application
2. Add the following URLs:
   ```
   Allowed Callback URLs:
   https://YOUR_IP.nip.io
   http://localhost:3000  (for local development)

   Allowed Logout URLs:
   https://YOUR_IP.nip.io
   http://localhost:3000

   Allowed Web Origins:
   https://YOUR_IP.nip.io
   http://localhost:3000
   ```

## 6. Update Environment Variables

Update your frontend's environment variables (`.env` or `.env.production`):
```
NEXT_PUBLIC_API_URL=https://YOUR_IP.nip.io/api
NEXT_PUBLIC_AUTH0_DOMAIN=your-auth0-domain.auth0.com
NEXT_PUBLIC_AUTH0_CLIENT_ID=your-client-id
```

## 7. Start Your Application

Run your Docker containers:
```bash
docker-compose up -d
```

## Verifying the Setup

1. Visit `https://YOUR_IP.nip.io` in your browser
2. Verify that the SSL certificate is valid (look for the lock icon)
3. Test the Auth0 login flow
4. Test API calls to ensure the backend is accessible

## Troubleshooting

1. If the site isn't accessible:
   - Check if nginx is running: `sudo systemctl status nginx`
   - Check nginx error logs: `sudo tail -f /var/log/nginx/error.log`
   - Verify security group settings

2. If Auth0 isn't working:
   - Check browser console for errors
   - Verify all URLs in Auth0 dashboard are correct
   - Ensure environment variables are properly set

3. If SSL certificate isn't working:
   - Check certbot logs: `sudo certbot certificates`
   - Verify DNS resolution: `ping YOUR_IP.nip.io`

## Notes

- This setup is intended for demonstration purposes
- nip.io is not recommended for production use
- For production, consider using:
  - A proper domain name
  - AWS Route 53
  - AWS Certificate Manager
  - Load balancer for better security and performance

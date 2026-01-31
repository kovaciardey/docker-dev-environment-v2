# Symfony 6.4 Development Environment

A Docker-based development environment for Symfony 6.4 API projects with Nginx, PHP-FPM, MySQL, and phpMyAdmin. Fully OS-agnostic and designed for WSL/Linux environments.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Available Commands](#available-commands)
- [Configuration](#configuration)
- [Accessing Services](#accessing-services)
- [Common Tasks](#common-tasks)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)

---

## Features

- **Containerized Development** - No host OS dependencies
- **Python CLI Wrapper** - Simple commands for all Docker operations
- **Nginx + PHP-FPM** - Professional web server architecture
- **MySQL 8.0** - Persistent database with custom configuration
- **phpMyAdmin** - Web-based database management
- **Dozzle** - Real-time Docker log viewer with web UI
- **User ID Mapping** - Automatic permission handling (no root-owned files)
- **Bash Aliases** - Quick shortcuts for common commands
- **Hot Reload** - Code changes reflect immediately

---

## Prerequisites

- **Docker** (20.10 or higher)
- **Docker Compose** (v2.0 or higher)
- **Python 3.7+**
- **Git**
- **WSL 2** (for Windows users) or Linux environment

### Verify Prerequisites
```bash
docker --version
docker compose version
python3 --version
git --version
```

---

## Quick Start

### 1. Clone This Repository
```bash
git clone <your-dev-environment-repo>
cd dev-environment
```

### 2. Make dev.py Executable
```bash
chmod +x dev.py
```

### 3. Initialize Environment
```bash
./dev.py init
```

This will:
- Create `.env` file from `.env.example`
- Auto-detect your user ID and group ID
- Prompt for your Symfony project GitHub URL
- Clone your Symfony repository
- Build Docker containers (may take 5-10 minutes)
- Start all containers
- Run `composer install`
- Install bash aliases

### 4. Access Your Application

- **Symfony API**: http://localhost:8080
- **phpMyAdmin**: http://localhost:8081
- **Dozzle (Logs)**: http://localhost:8082

### 5. Reload Your Shell
```bash
source ~/.bashrc
```

Now you can use short aliases like `dev`, `dcomposer`, `dsymfony`, etc.

---

## Architecture
```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ :8080
       ▼
┌─────────────────┐
│ Nginx Container │  Serves static files
│   (Alpine)      │  Proxies PHP via FastCGI
└────────┬────────┘
         │ :9000
         ▼
┌──────────────────┐
│ PHP-FPM Container│  Executes PHP code
│   (PHP 8.2)      │  Symfony 6.4
└────────┬─────────┘
         │ :3306
         ▼
┌──────────────────┐
│ MySQL Container  │  Persistent database
│   (MySQL 8.0)    │
└──────────────────┘
         ▲
         │ :8081
┌──────────────────┐
│  phpMyAdmin      │  Web UI for MySQL
└──────────────────┘
```

**Volume Mounts:**
- `./projects/symfony-api` → `/var/www/html` (mounted in both Nginx and PHP-FPM)
- `./logs/nginx` → Container logs (for debugging)
- `mysql-data` → Persistent database volume

**Network:**
- All containers communicate via `symfony-network` bridge

---

## Available Commands

### Container Lifecycle
```bash
dev init              # Initialize environment (first-time setup)
dev up                # Start containers (use --build to rebuild)
dev start             # Start all containers
dev stop              # Stop all containers
dev restart           # Restart all containers
dev down              # Stop and remove containers (data preserved)
dev rebuild           # Rebuild containers from scratch
dev status            # Show container status
dev nuke              # Complete Docker reset (use --force to skip prompt)
```

### Development Commands
```bash
dev composer [cmd]    # Run Composer commands
dev symfony [cmd]     # Run Symfony console commands
dev setup-symfony     # Run Symfony database setup (create DB, migrations, fixtures)
dev shell [service]   # Open interactive shell (default: php)
dev mysql             # Open MySQL CLI
dev logs [service]    # View logs (use -f to follow)
```

### Utility Commands
```bash
dev aliases           # Install/reinstall bash aliases
```

### Bash Aliases (After Running `dev aliases`)
```bash
dev                   # Main command
dcomposer             # Alias for 'dev composer'
dsymfony              # Alias for 'dev symfony'
dshell                # Alias for 'dev shell'
dmysql                # Alias for 'dev mysql'
dlogs                 # Alias for 'dev logs'
dstatus               # Alias for 'dev status'
dstart                # Alias for 'dev start'
dstop                 # Alias for 'dev stop'
drestart              # Alias for 'dev restart'
```

---

## Configuration

### Environment Variables (.env)

The `.env` file is created automatically during `dev init`. You can customize:
```env
# Symfony
APP_ENV=dev
APP_SECRET=your-secret-key

# MySQL
MYSQL_ROOT_PASSWORD=root
MYSQL_DATABASE=symfony
MYSQL_USER=symfony
MYSQL_PASSWORD=symfony
MYSQL_PORT=3306

# Ports (change if you have conflicts)
NGINX_PORT=8080
PHPMYADMIN_PORT=8081
DOZZLE_PORT=8082

# User ID Mapping (auto-detected)
USER_ID=1000
GROUP_ID=1000

# GitHub Repository
GITHUB_REPO=https://github.com/yourusername/symfony-api.git
GITHUB_BRANCH=main
```

### Changing Ports

If ports 8080, 8081, 8082, or 3306 are already in use:

1. Edit `.env` and change the port numbers
2. Restart containers: `dev restart`

---

## Accessing Services

### Symfony Application
```
http://localhost:8080
```

### phpMyAdmin
```
http://localhost:8081

Username: root
Password: root
```

### Dozzle (Docker Log Viewer)
```
http://localhost:8082

View real-time logs from all containers in a web interface.
No authentication required (local development only).
```

### MySQL (External Client)
```
Host: localhost
Port: 3306
Database: symfony
Username: symfony
Password: symfony
```

### Containers (Shell Access)
```bash
dev shell php         # PHP-FPM container (default)
dev shell nginx       # Nginx container
dev shell mysql       # MySQL container
```

---

## Common Tasks

### Installing Composer Dependencies
```bash
dev composer install
# or
dcomposer install
```

### Running Symfony Commands
```bash
dev symfony cache:clear
dev symfony doctrine:migrations:migrate
dev symfony make:entity User

# or using alias
dsymfony cache:clear
```

### Setting Up Symfony Database
```bash
# Automated setup (creates DB, runs migrations, loads fixtures)
dev setup-symfony

# Or manually step by step:
dev symfony doctrine:database:create
dev symfony doctrine:migrations:migrate
dev symfony doctrine:fixtures:load
```

### Creating Database Migrations
```bash
dev symfony make:migration
dev symfony doctrine:migrations:migrate
```

### Viewing Logs
```bash
# All logs
dev logs

# Specific service
dev logs nginx
dev logs php

# Follow logs in real-time
dev logs -f
dev logs -f php
```

### Running Tests
```bash
dev composer test
# or
dev shell
php bin/phpunit
```

### Clearing Symfony Cache
```bash
dev symfony cache:clear
# or
dshell
php bin/console cache:clear
```

### Importing Database Dump
```bash
# Via MySQL CLI
dev mysql < /path/to/dump.sql

# Via phpMyAdmin
# Go to http://localhost:8081 and use Import tab
```

### Exporting Database
```bash
dev shell mysql
mysqldump -usymfony -psymfony symfony > /var/www/html/backup.sql
exit

# File will be in: ./projects/symfony-api/backup.sql
```

---

## Troubleshooting

### Containers Won't Start

**Check if ports are in use:**
```bash
sudo lsof -i :8080
sudo lsof -i :3306
sudo lsof -i :8081
sudo lsof -i :8082
```

**Solution:** Change ports in `.env` and restart

### Permission Denied Errors

**Symptom:** Can't write to cache, logs, or var directory

**Cause:** USER_ID/GROUP_ID mismatch

**Solution:**
```bash
dev down
# Edit .env and set your correct USER_ID and GROUP_ID
# Find yours with: id -u (USER_ID) and id -g (GROUP_ID)
dev rebuild
```

### "Connection Refused" When Accessing MySQL

**Check if MySQL container is running:**
```bash
dev status
```

**Check MySQL logs:**
```bash
dev logs mysql
```

**Solution:** Restart containers
```bash
dev restart
```

### Composer Install Fails

**Check PHP container logs:**
```bash
dev logs php
```

**Try manual install:**
```bash
dev shell
composer install -vvv
```

### Nginx 502 Bad Gateway

**Cause:** PHP-FPM container is not running or not accessible

**Solution:**
```bash
dev status  # Check if php container is running
dev restart php
dev logs php  # Check for errors
```

### Code Changes Not Reflecting

**For PHP code:** Changes should appear immediately (OPcache is disabled in dev)

**For Symfony config/routes:**
```bash
dev symfony cache:clear
```

**For Twig templates:** Changes appear immediately in dev mode

### Docker Build Fails

**Clear Docker cache and rebuild:**
```bash
dev down
docker system prune -a  # WARNING: Removes all unused images
dev rebuild
```

### Complete Docker Reset

**Nuclear option - removes everything:**
```bash
dev nuke  # Will prompt for confirmation

# Or skip confirmation:
dev nuke --force
```

This removes:
* All project containers (running and stopped)
* All project images
* All project volumes (INCLUDING DATABASE DATA)
* All build cache

Note: Your Symfony code will NOT be deleted, but you will lose all database data.

### Can't Connect to Database from Symfony

**Check DATABASE_URL in .env:**
```env
DATABASE_URL=mysql://symfony:symfony@mysql:3306/symfony?serverVersion=8.0
```

**Test connection:**
```bash
dev symfony doctrine:query:sql "SELECT 1"
```

---

## Project Structure
```
dev-environment/
├── docker/
│   ├── symfony/
│   │   └── Dockerfile           # PHP-FPM container
│   ├── nginx/
│   │   ├── Dockerfile           # Nginx container
│   │   └── default.conf         # Nginx configuration
│   └── mysql/
│       └── my.cnf               # MySQL custom config
├── projects/
│   └── symfony-api/             # Your Symfony project (cloned)
├── logs/
│   └── nginx/                   # Nginx access/error logs
├── docker-compose.yml           # Orchestrates all services
├── dev.py                       # Python CLI wrapper
├── aliases                      # Bash aliases template
├── .env                         # Environment variables (created by init)
├── .env.example                 # Environment template
└── README.md                    # This file
```

---

## Updating the Environment

### Pull Latest Changes
```bash
git pull origin main
dev rebuild

# Or use the up command with rebuild:
dev up --build
```

### Update Symfony Dependencies
```bash
dev composer update
```

### Update Docker Images
```bash
dev down
docker compose pull
dev start
```

---

## Advanced Usage

### Running Custom Commands in Containers
```bash
# PHP container
docker exec -it symfony-php [command]

# Nginx container
docker exec -it symfony-nginx [command]

# MySQL container
docker exec -it symfony-mysql [command]
```

### Customizing PHP Configuration

Edit `docker/symfony/Dockerfile` and add to the custom.ini section, then:
```bash
dev rebuild
```

### Customizing Nginx Configuration

Edit `docker/nginx/default.conf`, then:
```bash
dev rebuild
```

### Adding New Docker Services

1. Edit `docker-compose.yml`
2. Add service configuration
3. Run `dev rebuild`

---

## Additional Resources

- [Symfony Documentation](https://symfony.com/doc/current/index.html)
- [Docker Documentation](https://docs.docker.com/)
- [Doctrine ORM Documentation](https://www.doctrine-project.org/projects/doctrine-orm/en/current/index.html)
- [Nginx Documentation](https://nginx.org/en/docs/)

---

## License

MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## Support

For issues or questions:
- Create an issue in this repository
- Contact: [your-email@example.com]

---
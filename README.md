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
- **Traefik Reverse Proxy** - Domain-based routing with automatic service discovery
- **Nginx + PHP-FPM** - Professional web server architecture for Symfony backend
- **Vue3 + Vue CLI** - Modern frontend development with hot module replacement
- **MySQL 8.4 (LTS)** - Persistent database with custom configuration
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

### 3. Setup Local DNS

Add the following entries to your hosts file:

**On Linux/WSL:**
```bash
sudo nano /etc/hosts
```

**On Windows:**
Edit `C:\Windows\System32\drivers\etc\hosts` (requires Administrator)

Add these lines:
```
127.0.0.1 ape-management.andrei.dev.uk
127.0.0.1 ape-management.api.andrei.dev.uk
127.0.0.1 phpmyadmin.andrei.dev.uk
127.0.0.1 dozzle.andrei.dev.uk
127.0.0.1 traefik.andrei.dev.uk
```

### 4. Initialize Environment
```bash
./dev.py init
```

This will:
- Create `.env` file from `.env.example`
- Auto-detect your user ID and group ID
- Build Docker containers (may take 5-10 minutes)
- Start all containers
- Install bash aliases

### 5. Setup Your Projects

After initialization, clone and setup your projects using the setup commands:

```bash
# Setup Symfony API project (clone + composer + database + migrations + fixtures)
./dev.py setup symfony

# Setup Vue Frontend project (clone + npm install)
./dev.py setup vue
```

These commands will:
- Prompt for repository URL if not configured in `.env`
- Clone the project from Git
- Install dependencies
- Run project-specific setup steps

### 6. Access Your Application

- **Vue Frontend**: http://ape-management.andrei.dev.uk
- **Symfony API**: http://ape-management.api.andrei.dev.uk
- **phpMyAdmin**: http://phpmyadmin.andrei.dev.uk
- **Dozzle (Logs)**: http://dozzle.andrei.dev.uk
- **Traefik Dashboard**: http://traefik.andrei.dev.uk

### 7. Reload Your Shell
```bash
source ~/.bashrc
```

Now you can use short aliases like `dev`, `dcomposer`, `dsymfony`, `dsetup`, etc.

---

## Architecture
```
Browser
   │ :80 (the only web port published on the host)
   ▼
Traefik (v3.6)  ── routes each request by domain name
   │
   ├─ ape-management.andrei.dev.uk      → Vue dev server :8080   (Node 24, Vue CLI, hot reload)
   │
   ├─ ape-management.api.andrei.dev.uk  → Nginx :80              (serves static files)
   │                                        │ :9000 FastCGI
   │                                        ▼
   │                                      PHP-FPM                (PHP 8.4, Symfony 6.4)
   │                                        │ :3306
   │                                        ▼
   │                                      MySQL 8.4              (also published on host :3306)
   │                                        ▲
   ├─ phpmyadmin.andrei.dev.uk          → phpMyAdmin :80 ────────┘
   │
   ├─ dozzle.andrei.dev.uk              → Dozzle :8080           (live container logs)
   │
   └─ traefik.andrei.dev.uk             → Traefik dashboard
```
Ports after `→` are inside the Docker network; only Traefik's `:80` and MySQL's `:3306` are reachable from the host.

**Volume Mounts:**
- `./projects/symfony-api` → `/var/www/html` (mounted in both Nginx and PHP-FPM)
- `./projects/ape-management-frontend` → `/app` (Vue)
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
dev up --pull         # Rebuild with newer base images first (e.g. a new PHP patch release)
dev start             # Start all containers
dev stop              # Stop all containers
dev restart           # Restart all containers
dev down              # Stop and remove containers (data preserved)
dev rebuild           # Rebuild containers from scratch (no layer cache, newer base images)
dev status            # Show container status
dev nuke              # Complete Docker reset (use --force to skip prompt)
```

### Project Setup Commands
```bash
dev setup symfony     # Clone/reset Symfony project and run full setup
dev setup vue         # Clone/reset Vue project and run npm install
dev setup <name> --force # Skip confirmation prompts when resetting
```

### Development Commands
```bash
dev composer [args]   # Run Composer commands
dev symfony [args]    # Run Symfony console commands (php bin/console)
dev npm [args]        # Run NPM commands (Vue container)
dev php [args]        # Run php in the PHP container
dev phpunit [args]    # Run PHPUnit (vendor/bin/phpunit; no arguments = all tests)
dev phpstan [args]    # Run PHPStan (vendor/bin/phpstan)
dev setup-symfony     # Run Symfony database setup (create DB, migrations, fixtures)
dev shell [service]   # Open interactive shell (default: php, as the symfony user)
dev shell php --root  # Open a root shell (for system tasks like apt-get or chown)
dev mysql             # Open MySQL CLI (as root, on the ape-management database)
dev logs [service]    # View logs (use -f to follow)
```

### How the Wrappers Pass Arguments

`composer`, `symfony`, `npm`, `php`, `phpunit` and `phpstan` pass everything after the command name to the tool unchanged:
```bash
dev composer update --lock                            # dashes are fine, no "--" needed
dev composer --help                                   # Composer's help (dev --help shows dev.py's)
dev symfony dbal:run-sql "SELECT 'hello world'"       # quoted arguments stay one argument
dev symfony list | head                               # output can be piped
dev mysql < backups/<file>.sql                        # input can be piped (mysql and shell too)
echo "SELECT 1;" | dev mysql
```

- **Environment variables:** `-e NAME=value` right after the command name is read by dev.py and passed to `docker exec -e` (repeatable):
  ```bash
  dev symfony -e TRUSTED_PROXIES=127.0.0.1 lint:container --env=prod
  ```
  dev.py only reads `-e NAME=value` (and an optional `--`) at the front. A `-e` without `NAME=` goes to the tool, so Symfony's own `-e prod` (short for `--env=prod`) still works.
- **`--`** right after the command name is accepted and dropped (`dev composer -- update --lock`), so old habits still work.
- **Terminal:** a TTY (`docker exec -t`) is only used when both input and output are a terminal, so piping and redirects work.
- **Output:** dev.py's own header and "Running:" line go to stderr, so only the tool's output goes into a pipe or file.
- **User:** the PHP commands run as the `symfony` user (same UID/GID as you on the host), so files they create (`vendor/`, `var/`, generated code) belong to you, not root. `npm` runs as the Vue container's default user, which is also your UID.
- **Exit code:** the tool's success or failure is passed on (`dev phpunit && echo ok`).

### Database Commands
```bash
dev db-dump [db]      # Dump a database to backups/ (default: ape-management)
dev db-reset          # Delete the MySQL data volume and start an empty server (use --force to skip prompt)
```
These have no short aliases on purpose: `db-reset` is destructive and both are used occasionally.

### Utility Commands
```bash
dev aliases           # Install/reinstall bash aliases
```

### Bash Aliases (After Running `dev aliases`)
```bash
dev                   # Main command
dcomposer             # Alias for 'dev composer'
dsymfony              # Alias for 'dev symfony'
dnpm                  # Alias for 'dev npm'
dphp                  # Alias for 'dev php'
dphpunit              # Alias for 'dev phpunit'
dphpstan              # Alias for 'dev phpstan'
dshell                # Alias for 'dev shell'
dmysql                # Alias for 'dev mysql'
dlogs                 # Alias for 'dev logs'
dstatus               # Alias for 'dev status'
dstart                # Alias for 'dev start'
dstop                 # Alias for 'dev stop'
drestart              # Alias for 'dev restart'
dsetup                # Alias for 'dev setup'
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

# User ID Mapping (auto-detected)
USER_ID=1000
GROUP_ID=1000

# Project Repositories (for dev setup commands)
SYMFONY_REPO=https://github.com/yourusername/symfony-api.git
VUE_REPO=https://github.com/yourusername/vue-frontend.git
```

### Projects Configuration (projects.yml)

The `projects.yml` file defines available projects for the setup command:
```yaml
projects:
  symfony:
    name: "Symfony API"
    repo_env_var: SYMFONY_REPO
    directory: projects/symfony-api
    repo_subdir: app
    container: symfony-php
    exec_user: symfony
    compose_service: php
    related_services:
      - nginx
    setup_steps:
      - "composer install --no-interaction"
      - "php bin/console doctrine:database:create --if-not-exists"
      - "php bin/console doctrine:migrations:migrate --no-interaction"
      - "php bin/console doctrine:fixtures:load --no-interaction"

  vue:
    name: "Vue Frontend"
    repo_env_var: VUE_REPO
    directory: projects/ape-management-frontend
    repo_subdir: app
    container: symfony-vue
    compose_service: vue
    setup_steps:
      - "npm install"
```

| Key | Meaning |
|---|---|
| `name` | Display name in dev.py's output |
| `repo_env_var` | `.env` variable holding the Git URL (prompted for if missing or a placeholder) |
| `directory` | Mount point that is bind-mounted into the container (kept on reset) |
| `repo_subdir` | Folder inside `directory` that the repo is cloned into (deleted and re-cloned by `dev setup`; default `app`) |
| `container` | Container the `setup_steps` run in |
| `exec_user` | Optional: user the `setup_steps` run as (default: the image's user, root for `symfony-php`) |
| `compose_service` | Compose service of the container, stopped/started around the re-clone (default: the project key) |
| `related_services` | Other services stopped/started with it (e.g. Nginx serves the same files) |
| `setup_steps` | Commands run in order via `docker exec` by `dev setup <project>` and `dev setup-symfony` |

You can add more projects by following this structure.

### Custom Domains

All services are accessed via custom domains configured in your hosts file:
- **Vue Frontend**: ape-management.andrei.dev.uk
- **Symfony API**: ape-management.api.andrei.dev.uk
- **phpMyAdmin**: phpmyadmin.andrei.dev.uk
- **Dozzle**: dozzle.andrei.dev.uk
- **Traefik Dashboard**: traefik.andrei.dev.uk

Traefik automatically routes traffic to the correct container based on the domain name.

---

## Accessing Services

All services are accessible via custom domains through Traefik reverse proxy.

### Symfony Application
```
http://ape-management.api.andrei.dev.uk
```

### phpMyAdmin
```
http://phpmyadmin.andrei.dev.uk

Username: root
Password: root
```

### Dozzle (Docker Log Viewer)
```
http://dozzle.andrei.dev.uk

View real-time logs from all containers in a web interface.
No authentication required (local development only).
```

### Traefik Dashboard
```
http://traefik.andrei.dev.uk

Monitor routing rules, active services, and health status.
No authentication required (local development only).
```

### Vue3 Frontend Application
```
http://ape-management.andrei.dev.uk

Vue3 development server with Vue CLI.
Hot module replacement (HMR) enabled - changes reflect instantly.
```

Note: Place your Vue3 project in `projects/ape-management-frontend/` directory.

### MySQL (External Client)
```
Host: localhost
Port: 3306
Database: ape-management
Username: root
Password: root
```

### Containers (Shell Access)
```bash
dev shell php         # PHP-FPM container (default), as the symfony user
dev shell php --root  # PHP-FPM container as root (--root works for any service)
dev shell nginx       # Nginx container
dev shell mysql       # MySQL container
dev shell vue         # Vue container
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

### Setting Up or Resetting Projects

**Complete project setup (clone + dependencies + setup):**
```bash
# Setup Symfony (clone, composer install, database, migrations, fixtures)
dev setup symfony

# Setup Vue (clone, npm install)
dev setup vue

# Reset project (delete and re-clone) - prompts for confirmation
dev setup symfony

# Reset without confirmation
dev setup symfony --force
```

**Note:** These commands will prompt you for the repository URL if not configured in `.env`, or if the URL appears to be a placeholder value.

### Setting Up Symfony Database Only

If you already have the project cloned and just need database setup:
```bash
# Automated setup (creates DB, runs migrations, loads fixtures)
dev setup-symfony

# Or manually step by step:
dev symfony doctrine:database:create
dev symfony doctrine:migrations:migrate
dev symfony doctrine:fixtures:load
```

### Setting Up Vue3 Frontend Manually

If you need to manually setup Vue instead of using `dev setup vue`:

**Option 1: Create a new Vue3 project with Vue CLI**
```bash
cd projects/ape-management-frontend
vue create .
```

**Option 2: Clone an existing Vue3 project**
```bash
cd projects/ape-management-frontend
git clone <your-vue-repo-url> .
```

**Important:** For Vue CLI projects, ensure your `vue.config.js` includes:
```javascript
const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    host: '0.0.0.0',
    port: 8080,
    allowedHosts: 'all',
    client: {
      webSocketURL: 'auto://0.0.0.0:0/ws'
    }
  },
  configureWebpack: {
    watchOptions: {
      poll: true
    }
  }
})
```

After setting up, restart the container:
```bash
dev restart
```

Access at http://ape-management.andrei.dev.uk

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
dev composer test            # All tests (the API's "test" script)
dev phpunit                  # Same, calling PHPUnit directly
dev phpunit --filter Bill    # Only tests matching a name
dev composer test:db         # (Re)create the test database first, if needed
dev composer ci              # Full CI checks: validate, audit, lints, PHPStan, tests
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
dev mysql < backups/<file>.sql

# Via phpMyAdmin
# Go to http://phpmyadmin.andrei.dev.uk and use the Import tab
```

Dumps made with `dev db-dump` include `CREATE DATABASE` and `USE`, so no database name is needed on import.

### Exporting Database
```bash
dev db-dump                  # Dumps ape-management
dev db-dump <database>       # Dumps another database

# File will be in: ./backups/<database>-YYYYmmdd-HHMMSS.sql
```

Dev dumps write one `INSERT` per row with column names (`--skip-extended-insert --complete-insert`) so they are easy to read and diff.

### Resetting the Database

Wipes all MySQL data and starts an empty server, then rebuilds the schema and fixtures:
```bash
dev db-dump        # Optional: back up first
dev db-reset       # Type RESET to confirm
dev setup-symfony  # Create DB, run migrations, load fixtures
```

This is also how to move to a new MySQL major/minor version: change the image tag in `docker-compose.yml`, then run the steps above.

---

## Troubleshooting

### Containers Won't Start

**Check if port 80 is in use:**
```bash
sudo lsof -i :80
sudo lsof -i :3306
```

**Solution:** Stop the service using port 80 or change Traefik's port in docker-compose.yml

### Domain Not Working

**Check hosts file:**
Ensure your hosts file contains:
```
127.0.0.1 ape-management.andrei.dev.uk
127.0.0.1 ape-management.api.andrei.dev.uk
127.0.0.1 phpmyadmin.andrei.dev.uk
127.0.0.1 dozzle.andrei.dev.uk
127.0.0.1 traefik.andrei.dev.uk
```

**Check Traefik:**
```bash
dev logs traefik
```

**View routing rules:**
Visit http://traefik.andrei.dev.uk to see active routes

### Permission Denied Errors

**Symptom:** Can't write to cache, logs, or var directory

**Cause 1:** USER_ID/GROUP_ID mismatch

**Solution:**
```bash
dev down
# Edit .env and set your correct USER_ID and GROUP_ID
# Find yours with: id -u (USER_ID) and id -g (GROUP_ID)
dev rebuild
```

**Cause 2:** root-owned files, created by something that ran as root in the PHP container (e.g. raw `docker exec` without `-u symfony`, or a `dev shell php --root` session). The dev wrappers run as `symfony`, which can't write into root's files.

**Check and fix:**
```bash
find projects/symfony-api/app -uid 0 | wc -l          # how many root-owned files (should be 0)
docker exec -u root symfony-php chown -R symfony:symfony vendor var   # no sudo needed
# or on the host: sudo chown -R 1000:1000 projects/symfony-api/app/vendor projects/symfony-api/app/var
```
Files inside the container but outside the project (e.g. PHPStan's `/tmp/phpstan` cache) can be removed with `docker exec -u root symfony-php rm -rf /tmp/phpstan`; a recreated container starts with a fresh `/tmp` anyway.

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

**Try a verbose install:**
```bash
dev composer install -vvv
```

### Nginx 502 Bad Gateway

**Cause:** PHP-FPM container is not running or not accessible

**Solution:**
```bash
dev status  # Check if php container is running
dev restart
dev logs php  # Check for errors
```

### Code Changes Not Reflecting

**For PHP code:** Changes should appear immediately (OPcache is enabled but re-checks file timestamps on every request: `validate_timestamps=1`, `revalidate_freq=0`)

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

**Check the `DB_*` variables in the API's `.env.dev`** (`projects/symfony-api/app/.env.dev`):
```env
DB_NAME="ape-management"
DB_HOST="mysql"
DB_PORT="3306"
DB_USERNAME="root"
DB_PASSWORD="root"
```

The MySQL version is set in `config/packages/doctrine.yaml` (`server_version: '8.4.0'`), not in an env var.

**Test connection:**
```bash
dev symfony dbal:run-sql "SELECT 1"
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
│   ├── vue/
│   │   └── Dockerfile           # Vue3 container
│   └── mysql/
│       └── my.cnf               # MySQL custom config
├── projects/                    # gitignored; each project is its own Git repo
│   ├── symfony-api/             # Mount point (-> /var/www/html)
│   │   └── app/                 # Symfony API repo (cloned via dev setup symfony)
│   └── ape-management-frontend/ # Mount point (-> /app)
│       └── app/                 # Vue3 repo (cloned via dev setup vue)
├── backups/                     # Database dumps from dev db-dump (gitignored)
├── logs/
│   └── nginx/                   # Nginx access/error logs
├── docker-compose.yml           # Orchestrates all services
├── dev.py                       # Python CLI wrapper
├── projects.yml                 # Project configuration for setup command
├── aliases                      # Bash aliases template
├── .env                         # Environment variables (created by init)
├── .env.example                 # Environment template
├── .dockerignore                # Not used by the current builds (each image builds from docker/<service>/)
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
docker compose pull   # No wrapper; downloads newer images for the current tags (mysql, phpmyadmin, traefik, dozzle)
dev up                # Recreates only the containers whose image changed
dev up --pull         # Images built from docker/*/Dockerfile: pull newer base images (FROM / COPY --from), rebuild, recreate
```

Compose only pulls an image when it is missing locally, so floating tags like `mysql:8.4` or `php:8.4-fpm` stay on the cached patch release until you pull. `--pull` and `--no-cache` are different: `--pull` checks for a newer base image; `--no-cache` reruns every build step but still uses the cached base image (`dev rebuild` uses both).

The Vue image is pinned to an exact Node version (`node:24.22.1-alpine`) that matches the front's prod image, because the npm bundled with Node writes `package-lock.json`. Bump both together. Patch releases within the same tag keep the existing data volume; a major/minor change (e.g. 8.4 → 9.x) should go through [Resetting the Database](#resetting-the-database).

---

## Advanced Usage

### Running Custom Commands in Containers
```bash
# PHP container (-u symfony, otherwise it runs as root and new files become root-owned)
docker exec -it -u symfony symfony-php [command]

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
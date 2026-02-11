#!/usr/bin/env python3
"""
Development Environment CLI
Wrapper for Docker Compose operations for Symfony development
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import shutil
import yaml

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_success(msg):
    """Print success message in green"""
    print(f"{Colors.OKGREEN}+ {msg}{Colors.ENDC}")

def print_error(msg):
    """Print error message in red"""
    print(f"{Colors.FAIL}x {msg}{Colors.ENDC}", file=sys.stderr)

def print_info(msg):
    """Print info message in cyan"""
    print(f"{Colors.OKCYAN}* {msg}{Colors.ENDC}")

def print_warning(msg):
    """Print warning message in yellow"""
    print(f"{Colors.WARNING}! {msg}{Colors.ENDC}")

def print_header(msg):
    """Print section header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{msg:^60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def run_command(cmd, check=True, capture_output=False, cwd=None):
    """Run a shell command and return result"""
    try:
        if capture_output:
            result = subprocess.run(
                cmd, 
                shell=True, 
                check=check, 
                capture_output=True, 
                text=True,
                cwd=cwd
            )
            return result.stdout.strip()
        else:
            result = subprocess.run(cmd, shell=True, check=check, cwd=cwd)
            return result.returncode == 0
    except subprocess.CalledProcessError as e:
        if capture_output and e.stderr:
            print_error(e.stderr)
        return False if capture_output else False

def get_project_root():
    """Get the project root directory (where dev.py is located)"""
    return Path(__file__).parent.absolute()

def check_docker():
    """Check if Docker is installed and running"""
    if not shutil.which("docker"):
        print_error("Docker is not installed!")
        print_info("Please install Docker: https://docs.docker.com/get-docker/")
        return False
    
    # Check if Docker daemon is running
    result = run_command("docker ps", check=False, capture_output=True)
    if result is False:
        print_error("Docker daemon is not running!")
        print_info("Please start Docker and try again.")
        return False
    
    return True

def check_docker_compose():
    """Check if Docker Compose is available"""
    # Try docker compose (new syntax)
    if run_command("docker compose version", check=False, capture_output=True):
        return "docker compose"
    # Try docker-compose (old syntax)
    elif shutil.which("docker-compose"):
        return "docker-compose"
    else:
        print_error("Docker Compose is not available!")
        return None

def load_env_file(project_root):
    """
    Load and parse .env file
    Returns dictionary of environment variables
    """
    env_file = project_root / '.env'
    env_vars = {}

    if not env_file.exists():
        return env_vars

    try:
        with open(env_file, 'r') as f:
            for line in f:
                # Strip whitespace
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue

                # Parse KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()

                    # Remove surrounding quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    env_vars[key] = value
    except Exception as e:
        print_warning(f"Error reading .env file: {e}")

    return env_vars

def is_placeholder_value(value):
    """
    Check if an environment variable value is a placeholder
    Returns True if the value appears to be a placeholder that needs replacement
    """
    if not value:
        return True

    placeholder_indicators = [
        'yourusername',
        'your-username',
        'placeholder',
        'example.com',
        'changeme',
        'change-me',
    ]

    value_lower = value.lower()
    return any(indicator in value_lower for indicator in placeholder_indicators)

def load_projects_config(project_root):
    """
    Load and parse projects.yml configuration file
    Returns dictionary of project configurations
    """
    config_file = project_root / 'projects.yml'

    if not config_file.exists():
        print_error("projects.yml not found in project root")
        print_info("Please ensure projects.yml exists with project configuration")
        return None

    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)

        if not config or 'projects' not in config:
            print_error("Invalid projects.yml format - missing 'projects' key")
            return None

        return config['projects']

    except yaml.YAMLError as e:
        print_error(f"Error parsing projects.yml: {e}")
        return None
    except Exception as e:
        print_error(f"Error reading projects.yml: {e}")
        return None

def create_parser():
    """Create and configure argument parser"""
    parser = argparse.ArgumentParser(
        description='Development Environment CLI for Symfony',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s init                    # Initialize the environment
  %(prog)s start                   # Start all containers
  %(prog)s setup symfony           # Clone/reset Symfony project and run setup
  %(prog)s setup vue               # Clone/reset Vue project and run setup
  %(prog)s setup symfony --force   # Reset without confirmation prompts
  %(prog)s composer install        # Run composer install
  %(prog)s npm install             # Run npm install in Vue container
  %(prog)s setup-symfony           # Setup Symfony database
  %(prog)s symfony cache:clear     # Clear Symfony cache
  %(prog)s shell php               # Open shell in PHP container
  %(prog)s shell vue               # Open shell in Vue container
  %(prog)s logs nginx              # View Nginx logs
  %(prog)s up --build              # Start containers with rebuild
  %(prog)s nuke                    # Complete Docker cleanup
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # init command
    subparsers.add_parser('init', help='Initialize development environment')
    
    # Container lifecycle commands
    subparsers.add_parser('start', help='Start all containers')
    subparsers.add_parser('stop', help='Stop all containers')
    subparsers.add_parser('restart', help='Restart all containers')
    subparsers.add_parser('down', help='Stop and remove containers')
    subparsers.add_parser('rebuild', help='Rebuild containers from scratch')
    
    # composer command
    composer_parser = subparsers.add_parser('composer', help='Run Composer commands')
    composer_parser.add_argument('composer_args', nargs='*', help='Composer arguments')

    # symfony command
    symfony_parser = subparsers.add_parser('symfony', help='Run Symfony console commands')
    symfony_parser.add_argument('symfony_args', nargs='*', help='Symfony console arguments')

    # npm command
    npm_parser = subparsers.add_parser('npm', help='Run NPM commands')
    npm_parser.add_argument('npm_args', nargs='*', help='NPM arguments')
    
    # shell command
    shell_parser = subparsers.add_parser('shell', help='Open shell in container')
    shell_parser.add_argument('service', nargs='?', default='php', 
                             help='Service name (default: php)')
    
    # mysql command
    subparsers.add_parser('mysql', help='Open MySQL CLI')
    
    # logs command
    logs_parser = subparsers.add_parser('logs', help='View container logs')
    logs_parser.add_argument('service', nargs='?', default='', 
                            help='Service name (default: all services)')
    logs_parser.add_argument('-f', '--follow', action='store_true',
                            help='Follow log output')
    
    # status command
    subparsers.add_parser('status', help='Show container status')
    
    # aliases command
    subparsers.add_parser('aliases', help='Install bash aliases')

    # setup command
    setup_parser = subparsers.add_parser('setup', help='Clone/reset and setup a project')
    setup_parser.add_argument('project', help='Project name (symfony, vue)')
    setup_parser.add_argument('--force', action='store_true',
                             help='Skip confirmation prompts')

    # setup-symfony command
    subparsers.add_parser('setup-symfony', help='Run Symfony database setup (create DB, migrations, fixtures)')

    # nuke command
    nuke_parser = subparsers.add_parser('nuke', help='Complete Docker reset - remove all containers, images, volumes')
    nuke_parser.add_argument('--force', action='store_true',
                            help='Skip confirmation prompt')

    # up command
    up_parser = subparsers.add_parser('up', help='Start containers with optional rebuild')
    up_parser.add_argument('--build', action='store_true',
                      help='Rebuild containers before starting')
    
    return parser

def cmd_start(compose_cmd, project_root):
    """Start all containers"""
    print_header("Starting Containers")
    if run_command(f"{compose_cmd} start", cwd=project_root):
        print_success("All containers started successfully!")
        print_info("Access Vue Frontend at: http://ape-management.andrei.dev.uk")
        print_info("Access Symfony API at: http://ape-management.api.andrei.dev.uk")
        print_info("Access phpMyAdmin at: http://phpmyadmin.andrei.dev.uk")
        print_info("Access Dozzle (Logs) at: http://dozzle.andrei.dev.uk")
        print_info("Access Traefik Dashboard at: http://traefik.andrei.dev.uk")
        return True
    else:
        print_error("Failed to start containers")
        return False

def cmd_stop(compose_cmd, project_root):
    """Stop all containers"""
    print_header("Stopping Containers")
    if run_command(f"{compose_cmd} stop", cwd=project_root):
        print_success("All containers stopped successfully!")
        return True
    else:
        print_error("Failed to stop containers")
        return False

def cmd_restart(compose_cmd, project_root):
    """Restart all containers"""
    print_header("Restarting Containers")
    if run_command(f"{compose_cmd} restart", cwd=project_root):
        print_success("All containers restarted successfully!")
        return True
    else:
        print_error("Failed to restart containers")
        return False

def cmd_down(compose_cmd, project_root):
    """Stop and remove containers"""
    print_header("Stopping and Removing Containers")
    print_warning("This will stop and remove all containers (data volumes will be preserved)")
    confirm = input("Continue? (y/N): ").strip().lower()
    
    if confirm != 'y':
        print_info("Operation cancelled")
        return False
    
    if run_command(f"{compose_cmd} down", cwd=project_root):
        print_success("Containers stopped and removed successfully!")
        return True
    else:
        print_error("Failed to remove containers")
        return False

def cmd_rebuild(compose_cmd, project_root):
    """Rebuild containers from scratch"""
    print_header("Rebuilding Containers")
    print_warning("This will rebuild all containers from scratch (may take several minutes)")
    confirm = input("Continue? (y/N): ").strip().lower()
    
    if confirm != 'y':
        print_info("Operation cancelled")
        return False
    
    print_info("Stopping containers...")
    run_command(f"{compose_cmd} down", cwd=project_root)
    
    print_info("Building containers (this may take a while)...")
    if not run_command(f"{compose_cmd} build --no-cache", cwd=project_root):
        print_error("Failed to build containers")
        return False
    
    print_info("Starting containers...")
    if run_command(f"{compose_cmd} up -d", cwd=project_root):
        print_success("Containers rebuilt and started successfully!")
        return True
    else:
        print_error("Failed to start containers")
        return False

def cmd_status(compose_cmd, project_root):
    """Show container status"""
    print_header("Container Status")
    run_command(f"{compose_cmd} ps", cwd=project_root)
    return True

def cmd_logs(compose_cmd, project_root, service='', follow=False):
    """View container logs"""
    print_header(f"Container Logs: {service if service else 'All Services'}")
    
    follow_flag = '-f' if follow else ''
    cmd = f"{compose_cmd} logs {follow_flag} {service}".strip()
    
    print_info(f"Running: {cmd}")
    print_info("Press Ctrl+C to exit\n")
    
    try:
        run_command(cmd, cwd=project_root, check=False)
    except KeyboardInterrupt:
        print_info("\nLog viewing stopped")
    
    return True

def cmd_composer(compose_cmd, project_root, composer_args):
    """Run Composer commands inside PHP container"""
    print_header("Running Composer")
    
    # Join composer arguments
    args_str = ' '.join(composer_args) if composer_args else ''
    
    if not args_str:
        print_error("No composer command specified")
        print_info("Example: dev composer install")
        return False
    
    cmd = f"docker exec -it symfony-php composer {args_str}"
    print_info(f"Running: {cmd}\n")

    return run_command(cmd, check=False)

def cmd_symfony(compose_cmd, project_root, symfony_args):
    """Run Symfony console commands inside PHP container"""
    print_header("Running Symfony Console")

    # Join symfony arguments
    args_str = ' '.join(symfony_args) if symfony_args else ''

    if not args_str:
        print_error("No Symfony command specified")
        print_info("Example: dev symfony cache:clear")
        return False

    cmd = f"docker exec -it symfony-php php bin/console {args_str}"
    print_info(f"Running: {cmd}\n")

    return run_command(cmd, check=False)

def cmd_npm(compose_cmd, project_root, npm_args):
    """Run NPM commands inside Vue container"""
    print_header("Running NPM")

    # Join npm arguments
    args_str = ' '.join(npm_args) if npm_args else ''

    if not args_str:
        print_error("No NPM command specified")
        print_info("Example: dev npm install")
        return False

    cmd = f"docker exec -it symfony-vue npm {args_str}"
    print_info(f"Running: {cmd}\n")

    return run_command(cmd, check=False)

def cmd_shell(compose_cmd, project_root, service='php'):
    """Open interactive shell in container"""
    print_header(f"Opening Shell: {service}")

    container_name = f"symfony-{service}"

    # Check if container exists and is running
    check_cmd = f"docker ps --filter name={container_name} --format '{{{{.Names}}}}'"
    result = run_command(check_cmd, capture_output=True)

    if not result or container_name not in result:
        print_error(f"Container '{container_name}' is not running")
        print_info("Available services: php, nginx, mysql, vue")
        print_info("Start containers with: dev start")
        return False

    # Determine shell to use (bash for most, sh for alpine-based images)
    shell = 'sh' if service in ['nginx', 'vue'] else 'bash'

    cmd = f"docker exec -it {container_name} {shell}"
    print_info(f"Running: {cmd}")
    print_info("Type 'exit' to leave the shell\n")

    return run_command(cmd, check=False)

def cmd_mysql(compose_cmd, project_root):
    """Open MySQL CLI inside MySQL container"""
    print_header("Opening MySQL CLI")
    
    # Check if MySQL container is running
    check_cmd = "docker ps --filter name=symfony-mysql --format '{{.Names}}'"
    result = run_command(check_cmd, capture_output=True)
    
    if not result or 'symfony-mysql' not in result:
        print_error("MySQL container is not running")
        print_info("Start containers with: dev start")
        return False
    
    # Get MySQL credentials from .env file
    env_file = project_root / '.env'
    mysql_user = 'symfony'
    mysql_password = 'symfony'
    mysql_database = 'symfony'
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('MYSQL_USER='):
                    mysql_user = line.split('=', 1)[1]
                elif line.startswith('MYSQL_PASSWORD='):
                    mysql_password = line.split('=', 1)[1]
                elif line.startswith('MYSQL_DATABASE='):
                    mysql_database = line.split('=', 1)[1]
    
    cmd = f"docker exec -it symfony-mysql mysql -u{mysql_user} -p{mysql_password} {mysql_database}"
    print_info(f"Connecting to database: {mysql_database}")
    print_info("Type 'exit' to leave MySQL CLI\n")

    return run_command(cmd, check=False)

def cmd_init(compose_cmd, project_root):
    """Initialize the development environment"""
    print_header("Initializing Development Environment")
    
    # Step 1: Check if already initialized
    symfony_project = project_root / 'projects' / 'symfony-api'
    if symfony_project.exists() and any(symfony_project.iterdir()):
        print_warning("Project directory already exists!")
        confirm = input("Reinitialize? This will NOT delete existing code. (y/N): ").strip().lower()
        if confirm != 'y':
            print_info("Initialization cancelled")
            return False
    
    # Step 2: Check for .env file
    env_file = project_root / '.env'
    env_example = project_root / '.env.example'
    
    if not env_file.exists():
        if not env_example.exists():
            print_error(".env.example file not found!")
            return False
        
        print_info("Creating .env file from .env.example...")
        shutil.copy(env_example, env_file)
        print_success(".env file created")
    else:
        print_info(".env file already exists")
    
    # Step 3: Auto-detect and set USER_ID and GROUP_ID
    print_info("Detecting user and group IDs...")
    user_id = os.getuid()
    group_id = os.getgid()
    print_success(f"Detected USER_ID={user_id}, GROUP_ID={group_id}")
    
    # Update .env file with USER_ID and GROUP_ID
    with open(env_file, 'r') as f:
        env_content = f.read()
    
    # Check if USER_ID and GROUP_ID are already set
    if 'USER_ID=' not in env_content:
        with open(env_file, 'a') as f:
            f.write(f'\n# Auto-detected user IDs\n')
            f.write(f'USER_ID={user_id}\n')
            f.write(f'GROUP_ID={group_id}\n')
        print_success("Added USER_ID and GROUP_ID to .env")
    else:
        print_info("USER_ID and GROUP_ID already set in .env")
    
    # Step 4: Get GitHub repository URL
    github_repo = None
    
    # Try to read from .env
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('GITHUB_REPO='):
                github_repo = line.split('=', 1)[1]
                break
    
    # Ask user if not found or if it's the example URL
    if not github_repo or 'yourusername' in github_repo:
        print_info("\nEnter your Symfony project GitHub repository URL")
        github_repo = input("GitHub URL (or press Enter to skip cloning): ").strip()
    
    # Step 5: Clone Symfony repository if URL provided
    if github_repo and not symfony_project.exists():
        print_info(f"\nCloning Symfony repository: {github_repo}")
        symfony_project.parent.mkdir(parents=True, exist_ok=True)

        clone_cmd = f"git clone {github_repo} {symfony_project}"
        if not run_command(clone_cmd, cwd=project_root):
            print_error("Failed to clone repository")
            print_info("You can manually clone later into: projects/symfony-api")
        else:
            print_success("Symfony repository cloned successfully")
    elif symfony_project.exists():
        print_info("Symfony project directory already exists, skipping clone")
    else:
        print_warning("No Symfony repository URL provided")
        print_info("You can manually clone your project into: projects/symfony-api")
        # Create empty directory
        symfony_project.mkdir(parents=True, exist_ok=True)

    # Step 5b: Ask for Vue repository
    vue_project = project_root / 'projects' / 'ape-management-frontend'

    if not vue_project.exists() or not any(vue_project.iterdir() if vue_project.exists() else []):
        print_info("\nEnter your Vue project GitHub repository URL")
        vue_repo = input("Vue GitHub URL (or press Enter to skip): ").strip()

        if vue_repo:
            print_info(f"Cloning Vue repository: {vue_repo}")
            vue_project.parent.mkdir(parents=True, exist_ok=True)

            clone_cmd = f"git clone {vue_repo} {vue_project}"
            if not run_command(clone_cmd, cwd=project_root):
                print_error("Failed to clone Vue repository")
                print_info("You can manually clone later into: projects/ape-management-frontend")
            else:
                print_success("Vue repository cloned successfully")
        else:
            print_info("No Vue repository URL provided")
            print_info("You can manually clone your Vue project into: projects/ape-management-frontend")
            # Create empty directory
            vue_project.mkdir(parents=True, exist_ok=True)
    else:
        print_info("Vue project directory already exists, skipping clone")

    # Step 6: Build Docker containers
    print_info("\nBuilding Docker containers (this may take several minutes)...")
    if not run_command(f"{compose_cmd} build", cwd=project_root):
        print_error("Failed to build containers")
        return False
    print_success("Containers built successfully")
    
    # Step 7: Start containers
    print_info("\nStarting containers...")
    if not run_command(f"{compose_cmd} up -d", cwd=project_root):
        print_error("Failed to start containers")
        return False
    print_success("Containers started successfully")
    
    # Step 8: Wait for containers to be ready
    print_info("\nWaiting for containers to be ready...")
    import time
    time.sleep(5)  # Give containers time to fully start
    
    # Step 9: Run composer install if composer.json exists
    composer_json = symfony_project / 'composer.json'
    if composer_json.exists():
        print_info("\nRunning composer install...")
        if run_command("docker exec symfony-php composer install", check=False):
            print_success("Composer dependencies installed")
        else:
            print_warning("Composer install failed or was skipped")
            print_info("You can run it manually with: dev composer install")
    else:
        print_info("\nNo composer.json found, skipping composer install")
    
    # Step 10: Install bash aliases
    print_info("\nInstalling bash aliases...")
    if cmd_aliases(project_root, from_init=True):
        print_success("Bash aliases installed")
    else:
        print_warning("Failed to install bash aliases")
        print_info("You can install them manually with: dev aliases")
    
    # Step 11: Success message
    print_header("Initialization Complete!")
    print_success("Development environment is ready!")
    print_info("\nAccess your application:")
    print(f"  * Vue Frontend: {Colors.OKBLUE}http://ape-management.andrei.dev.uk{Colors.ENDC}")
    print(f"  * Symfony API: {Colors.OKBLUE}http://ape-management.api.andrei.dev.uk{Colors.ENDC}")
    print(f"  * phpMyAdmin: {Colors.OKBLUE}http://phpmyadmin.andrei.dev.uk{Colors.ENDC}")
    print(f"  * Dozzle (Logs): {Colors.OKBLUE}http://dozzle.andrei.dev.uk{Colors.ENDC}")
    print(f"  * Traefik Dashboard: {Colors.OKBLUE}http://traefik.andrei.dev.uk{Colors.ENDC}")
    print_info("\nNext steps:")
    print("  * dev setup symfony   - Clone and setup Symfony API project")
    print("  * dev setup vue       - Clone and setup Vue Frontend project")
    print_info("\nUseful commands:")
    print("  * dev status          - View container status")
    print("  * dev logs -f         - Follow all logs")
    print("  * dev composer [cmd]  - Run Composer commands")
    print("  * dev symfony [cmd]   - Run Symfony console")
    print("  * dev npm [cmd]       - Run NPM commands")
    print("  * dev shell [service] - Open shell in container (php, vue, nginx, mysql)")
    print("  * dev mysql           - Open MySQL CLI")
    print_info("\nReload your shell or run: source ~/.bashrc")
    
    return True

def cmd_aliases(project_root, from_init=False):
    """
    Install bash aliases to ~/.bash_aliases
    The aliases file in the project root is the single source of truth.

    Args:
        project_root: Path to project root
        from_init: True if called during init command, False if called manually
    """
    print_header("Installing Bash Aliases")

    # Path to aliases file in project
    aliases_file = project_root / 'aliases'

    if not aliases_file.exists():
        print_error("aliases file not found in project root!")
        print_info("Please create the 'aliases' file first")
        return False

    # Path to user's .bash_aliases
    home_dir = Path.home()
    bash_aliases = home_dir / '.bash_aliases'
    bashrc = home_dir / '.bashrc'

    # Read the aliases content from source file
    with open(aliases_file, 'r') as f:
        aliases_content = f.read()

    # Replace placeholder path with actual project path
    dev_py_path = project_root / 'dev.py'
    aliases_content = aliases_content.replace('/path/to/dev-environment/dev.py', str(dev_py_path))

    # Prompt user if .bash_aliases already exists (unless called from init and file doesn't exist)
    if bash_aliases.exists():
        print_warning(f"\n{bash_aliases} already exists and will be completely replaced")
        print_info("The 'aliases' file in your project is the single source of truth")
        print_info("Any custom aliases should be added to the 'Custom aliases' section in the project's aliases file")
        confirm = input("\nReplace ~/.bash_aliases with content from project aliases file? (y/N): ").strip().lower()

        if confirm != 'y':
            print_info("Alias installation cancelled")
            return False
    elif not from_init:
        # File doesn't exist and not called from init - inform user
        print_info("Creating new ~/.bash_aliases file")

    # Write the entire aliases file content to ~/.bash_aliases (full replacement)
    with open(bash_aliases, 'w') as f:
        f.write(aliases_content)

    print_success(f"Aliases written to {bash_aliases}")
    
    # Ensure .bashrc sources .bash_aliases
    if bashrc.exists():
        with open(bashrc, 'r') as f:
            bashrc_content = f.read()
        
        # Check if .bash_aliases is already sourced
        if '.bash_aliases' not in bashrc_content:
            print_info("Adding source command to ~/.bashrc...")
            
            source_lines = """
# Source bash aliases if file exists
if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi
"""
            with open(bashrc, 'a') as f:
                f.write(source_lines)
            
            print_success("Added source command to ~/.bashrc")
        else:
            print_info("~/.bashrc already sources ~/.bash_aliases")
    else:
        print_warning("~/.bashrc not found")
        print_info("Please ensure your shell sources ~/.bash_aliases")
    
    print_success("\nAliases installed successfully!")
    print_info("\nTo add custom aliases:")
    print(f"  1. Edit the 'aliases' file in: {project_root}")
    print("  2. Add your aliases to the 'Custom aliases' section")
    print("  3. Run 'dev aliases' to update ~/.bash_aliases")
    print_info("\nAvailable dev aliases:")
    print("  * dev              - Main dev.py command")
    print("  * dcomposer        - Shortcut for 'dev composer'")
    print("  * dsymfony         - Shortcut for 'dev symfony'")
    print("  * dnpm             - Shortcut for 'dev npm'")
    print("  * dshell           - Shortcut for 'dev shell'")
    print("  * dmysql           - Shortcut for 'dev mysql'")
    print("  * dlogs            - Shortcut for 'dev logs'")
    print("  * dstatus          - Shortcut for 'dev status'")
    print("  * dstart           - Shortcut for 'dev start'")
    print("  * dstop            - Shortcut for 'dev stop'")
    print("  * drestart         - Shortcut for 'dev restart'")
    print("  * dsetup           - Shortcut for 'dev setup'")
    print_info("\nReload your shell with: source ~/.bashrc")
    
    return True

def cmd_setup_steps(compose_cmd, project_root, project_name):
    """
    Run setup steps for a project without re-cloning.
    Useful for re-running database setup, installing dependencies, etc.
    Reads steps from projects.yml.
    """
    # Load projects configuration
    projects_config = load_projects_config(project_root)
    if not projects_config:
        return False

    if project_name not in projects_config:
        print_error(f"Unknown project: {project_name}")
        print_info(f"Available projects: {', '.join(projects_config.keys())}")
        return False

    project_config = projects_config[project_name]
    project_display_name = project_config['name']
    container_name = project_config['container']
    setup_steps = project_config.get('setup_steps', [])

    print_header(f"{project_display_name} Setup Steps")

    # Check if container is running
    check_cmd = f"docker ps --filter name={container_name} --filter status=running --format '{{{{.Names}}}}'"
    result = run_command(check_cmd, capture_output=True)

    if not result or container_name not in str(result):
        print_error(f"Container '{container_name}' is not running")
        print_info("Start containers with: dev start")
        return False

    if not setup_steps:
        print_warning(f"No setup steps defined for {project_display_name}")
        return True

    total = len(setup_steps)
    print_info(f"Running {total} setup step(s)...")

    for i, step in enumerate(setup_steps, 1):
        print_info(f"\n[{i}/{total}] Running: {step}")
        cmd = f"docker exec {container_name} {step}"
        if not run_command(cmd, check=False):
            print_error(f"Setup step failed: {step}")
            return False
        print_success(f"Step {i}/{total} completed")

    print_header(f"{project_display_name} Setup Complete!")
    return True

def cmd_setup(compose_cmd, project_root, project_name, force=False):
    """
    Generic project setup/reset command.
    Handles cloning and setup for any project defined in projects.yml.

    Flow:
    1. Load config and validate
    2. Get repo URL, warn user and confirm
    3. Stop the project's container + related services
    4. Delete the repo subdirectory (NOT the mount point)
    5. Clone fresh repo into subdirectory
    6. Start container + related services
    7. Wait for container readiness
    8. Run setup_steps via docker exec
    """
    print_header(f"Project Setup: {project_name}")

    # Load projects configuration
    projects_config = load_projects_config(project_root)
    if not projects_config:
        return False

    # Validate project name
    if project_name not in projects_config:
        print_error(f"Unknown project: {project_name}")
        print_info(f"Available projects: {', '.join(projects_config.keys())}")
        return False

    # Get project configuration
    project_config = projects_config[project_name]
    project_display_name = project_config['name']
    repo_env_var = project_config['repo_env_var']
    repo_subdir = project_config.get('repo_subdir', 'app')
    container_name = project_config['container']
    compose_service = project_config.get('compose_service', project_name)
    related_services = project_config.get('related_services', [])
    setup_steps = project_config.get('setup_steps', [])

    # Compute paths
    mount_point = project_root / project_config['directory']
    repo_dir = mount_point / repo_subdir

    print_info(f"Setting up: {project_display_name}")

    # Load environment variables
    env_vars = load_env_file(project_root)

    # Get repository URL from .env
    repo_url = env_vars.get(repo_env_var, '')

    # Check if URL is valid or needs prompting
    if not repo_url or is_placeholder_value(repo_url):
        print_warning(f"{repo_env_var} not set or contains placeholder value")
        print_info(f"Please enter the repository URL for {project_display_name}")
        repo_url = input(f"{repo_env_var} URL: ").strip()

        if not repo_url:
            print_error("No repository URL provided")
            print_info(f"Set {repo_env_var} in .env file or provide URL when prompted")
            return False

    # Check if repo subdirectory exists and confirm deletion
    if repo_dir.exists():
        if not force:
            print_warning(f"Repository directory already exists: {repo_dir}")
            print_info("This will DELETE the repository and re-clone it. Any uncommitted changes will be lost.")
            confirm = input("Continue? [y/N]: ").strip().lower()

            if confirm != 'y':
                print_info("Setup cancelled")
                return False

    # Stop the project's container and related services
    all_services = [compose_service] + related_services
    print_info(f"Stopping containers: {', '.join(all_services)}")
    for service in all_services:
        run_command(f"{compose_cmd} stop {service}", cwd=project_root, check=False)

    # Delete the repo subdirectory (NOT the mount point)
    if repo_dir.exists():
        print_info(f"Removing repository directory: {repo_dir}")
        try:
            shutil.rmtree(repo_dir)
            print_success("Directory removed")
        except PermissionError:
            print_warning("Permission error - cleaning up via Docker...")
            mount_point_abs = mount_point.resolve()
            cleanup_cmd = (
                f"docker run --rm -v {mount_point_abs}:/cleanup alpine "
                f"sh -c 'rm -rf /cleanup/{repo_subdir}'"
            )
            if not run_command(cleanup_cmd, check=False):
                print_error("Failed to remove directory even with Docker cleanup")
                return False
            print_success("Directory removed via Docker cleanup")
        except Exception as e:
            print_error(f"Failed to remove directory: {e}")
            return False

    # Ensure mount point exists and clone repository
    mount_point.mkdir(parents=True, exist_ok=True)

    print_info(f"\nCloning repository from: {repo_url}")
    clone_cmd = f"git clone {repo_url} {repo_dir}"
    if not run_command(clone_cmd):
        print_error("Failed to clone repository")
        return False
    print_success(f"Repository cloned to {repo_dir}")

    # Start container and related services
    print_info(f"\nStarting containers: {', '.join(all_services)}")
    for service in all_services:
        run_command(f"{compose_cmd} start {service}", cwd=project_root, check=False)

    # Wait for the project's container to be ready
    import time
    print_info(f"Waiting for {container_name} to be ready...")
    max_retries = 15
    container_ready = False
    for i in range(max_retries):
        check_cmd = f"docker ps --filter name={container_name} --filter status=running --format '{{{{.Names}}}}'"
        result = run_command(check_cmd, capture_output=True)
        if result and container_name in str(result):
            print_success(f"Container {container_name} is running")
            container_ready = True
            break
        time.sleep(2)

    if not container_ready:
        print_error(f"Container {container_name} failed to start within {max_retries * 2}s")
        return False

    # Run setup steps
    if not setup_steps:
        print_success(f"{project_display_name} setup complete (no setup steps defined)")
        return True

    total = len(setup_steps)
    print_info(f"\nRunning {total} setup step(s)...")

    for i, step in enumerate(setup_steps, 1):
        print_info(f"\n[{i}/{total}] Running: {step}")
        cmd = f"docker exec {container_name} {step}"
        if not run_command(cmd, check=False):
            print_error(f"Setup step failed: {step}")
            return False
        print_success(f"Step {i}/{total} completed")

    print_header(f"{project_display_name} Setup Complete!")
    print_success("Project is ready")
    return True

def cmd_nuke(compose_cmd, project_root, force=False):
    """Complete Docker reset - nuclear option"""
    print_header("[!] NUCLEAR OPTION - Complete Docker Reset [!]")
    
    if not force:
        print_warning("This will completely remove:")
        print("  * All project containers (running and stopped)")
        print("  * All project images")
        print("  * All project volumes (INCLUDING DATABASE DATA)")
        print("  * All build cache")
        print_warning("\nYour Symfony code will NOT be deleted")
        print_warning("But you will lose ALL database data!")
        print_warning("\nThis action CANNOT be undone!")
        
        confirm = input("\nType 'NUKE' in capitals to confirm: ").strip()
        if confirm != 'NUKE':
            print_info("Nuke cancelled")
            return False
    
    print_info("\n*** Beginning nuclear cleanup...")
    
    # Step 1: Stop and remove containers
    print_info("\n[1/5] Stopping and removing containers...")
    if run_command(f"{compose_cmd} down", cwd=project_root, check=False):
        print_success("Containers stopped and removed")
    else:
        print_warning("Failed to stop containers (they may not exist)")
    
    # Step 2: Remove volumes
    print_info("\n[2/5] Removing volumes...")
    if run_command(f"{compose_cmd} down -v", cwd=project_root, check=False):
        print_success("Volumes removed")
    else:
        print_warning("Failed to remove volumes (they may not exist)")
    
    # Step 3: Remove images
    print_info("\n[3/5] Removing images...")
    # Get image names from docker-compose
    get_images_cmd = f"{compose_cmd} config --images"
    images = run_command(get_images_cmd, cwd=project_root, capture_output=True)
    
    if images:
        for image in images.split('\n'):
            if image.strip():
                remove_cmd = f"docker rmi {image.strip()} --force"
                run_command(remove_cmd, check=False)
        print_success("Images removed")
    else:
        print_info("No images to remove")
    
    # Step 4: Prune build cache
    print_info("\n[4/5] Pruning build cache...")
    if run_command("docker builder prune -af", check=False):
        print_success("Build cache pruned")
    else:
        print_warning("Failed to prune build cache")
    
    # Step 5: Clean up orphaned resources
    print_info("\n[5/5] Cleaning up orphaned resources...")
    run_command("docker system prune -f", check=False)
    print_success("Orphaned resources cleaned")
    
    print_header("*** Nuclear Cleanup Complete! ***")
    print_success("All Docker resources have been removed")
    print_info("\nTo rebuild your environment:")
    print("  * dev init          - Full initialization")
    print("  * dev up --build    - Start with rebuild")
    
    return True

def cmd_up(compose_cmd, project_root, build=False):
    """Start containers with optional rebuild"""
    if build:
        print_header("Starting Containers with Rebuild")
    else:
        print_header("Starting Containers")
    
    # Check for .env file
    env_file = project_root / '.env'
    if not env_file.exists():
        print_error(".env file not found!")
        print_info("Run 'dev init' first to initialize the environment")
        return False
    
    # Build the command
    if build:
        cmd = f"{compose_cmd} up -d --build"
        print_info("Building and starting containers (this may take a few minutes)...")
    else:
        cmd = f"{compose_cmd} up -d"
        print_info("Starting containers...")
    
    if not run_command(cmd, cwd=project_root):
        print_error("Failed to start containers")
        return False
    
    print_success("Containers started successfully")

    # Show status
    print_info("\nContainer Status:")
    run_command(f"{compose_cmd} ps", cwd=project_root, check=False)

    print_info("\nAccess your application:")
    print(f"  * Vue Frontend: {Colors.OKBLUE}http://ape-management.andrei.dev.uk{Colors.ENDC}")
    print(f"  * Symfony API: {Colors.OKBLUE}http://ape-management.api.andrei.dev.uk{Colors.ENDC}")
    print(f"  * phpMyAdmin: {Colors.OKBLUE}http://phpmyadmin.andrei.dev.uk{Colors.ENDC}")
    print(f"  * Dozzle (Logs): {Colors.OKBLUE}http://dozzle.andrei.dev.uk{Colors.ENDC}")
    print(f"  * Traefik Dashboard: {Colors.OKBLUE}http://traefik.andrei.dev.uk{Colors.ENDC}")

    return True

# Main entry point will go here
if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    
    # Show help if no command provided
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Check Docker availability (except for aliases command)
    if args.command != 'aliases':
        if not check_docker():
            sys.exit(1)
    
    # Get Docker Compose command
    compose_cmd = check_docker_compose()
    if args.command not in ['aliases'] and not compose_cmd:
        sys.exit(1)
    
    # Store these for use in command functions
    PROJECT_ROOT = get_project_root()
    COMPOSE_CMD = compose_cmd
    
# Command routing
    if args.command == 'init':
        cmd_init(COMPOSE_CMD, PROJECT_ROOT)
    elif args.command == 'start':
        cmd_start(COMPOSE_CMD, PROJECT_ROOT)
    elif args.command == 'stop':
        cmd_stop(COMPOSE_CMD, PROJECT_ROOT)
    elif args.command == 'restart':
        cmd_restart(COMPOSE_CMD, PROJECT_ROOT)
    elif args.command == 'down':
        cmd_down(COMPOSE_CMD, PROJECT_ROOT)
    elif args.command == 'rebuild':
        cmd_rebuild(COMPOSE_CMD, PROJECT_ROOT)
    elif args.command == 'composer':
        cmd_composer(COMPOSE_CMD, PROJECT_ROOT, args.composer_args)
    elif args.command == 'symfony':
        cmd_symfony(COMPOSE_CMD, PROJECT_ROOT, args.symfony_args)
    elif args.command == 'npm':
        cmd_npm(COMPOSE_CMD, PROJECT_ROOT, args.npm_args)
    elif args.command == 'shell':
        cmd_shell(COMPOSE_CMD, PROJECT_ROOT, args.service)
    elif args.command == 'mysql':
        cmd_mysql(COMPOSE_CMD, PROJECT_ROOT)
    elif args.command == 'logs':
        cmd_logs(COMPOSE_CMD, PROJECT_ROOT, args.service, args.follow)
    elif args.command == 'status':
        cmd_status(COMPOSE_CMD, PROJECT_ROOT)
    elif args.command == 'aliases':
        cmd_aliases(PROJECT_ROOT)
    elif args.command == 'setup':
        cmd_setup(COMPOSE_CMD, PROJECT_ROOT, args.project, args.force)
    elif args.command == 'setup-symfony':
        cmd_setup_steps(COMPOSE_CMD, PROJECT_ROOT, 'symfony')
    elif args.command == 'nuke':
        cmd_nuke(COMPOSE_CMD, PROJECT_ROOT, args.force)
    elif args.command == 'up':
        cmd_up(COMPOSE_CMD, PROJECT_ROOT, args.build)
    else:
        parser.print_help()
        sys.exit(1)
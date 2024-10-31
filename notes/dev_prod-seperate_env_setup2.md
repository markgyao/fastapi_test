## Ubuntu OS

Here’s a comprehensive step-by-step guide to install and configure **FastAPI**, **Uvicorn**, **Nginx**, **pyenv**, and **MariaDB** on a single Ubuntu server for both production and development environments. We'll also cover configuring Nginx as a reverse proxy for these environments and setting up `pyenv` for environment management.

### Step 1: Install System Dependencies

Update your server and install necessary system packages:
```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl \
llvm libncursesw5-dev xz-utils tk-dev libxml2-dev \
libxmlsec1-dev libffi-dev liblzma-dev python3-openssl \
nginx mariadb-server mariadb-client
```

### Step 2: Install `pyenv` for Python Version Management

1. Install dependencies for building Python:
   ```bash
   sudo apt install -y make build-essential libssl-dev zlib1g-dev \
   libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
   libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev \
   liblzma-dev python3-openssl git
   ```

2. Install `pyenv`:
   ```bash
   curl https://pyenv.run | bash
   ```

3. Add `pyenv` to your shell startup file (`~/.bashrc` or `~/.zshrc`):
   ```bash
   echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
   echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
   echo 'eval "$(pyenv init -)"' >> ~/.bashrc
   echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
   source ~/.bashrc
   ```

4. Verify the installation:
   ```bash
   pyenv --version
   ```

### Step 3: Install Python Versions

Using `pyenv`, install a specific version of Python (e.g., 3.11.4):

```bash
pyenv install 3.11.4
```

Create separate virtual environments for production and development:

- **Production**:
  ```bash
  pyenv virtualenv 3.11.4 fastapi-prod
  ```

- **Development**:
  ```bash
  pyenv virtualenv 3.11.4 fastapi-dev
  ```

### Step 4: Install FastAPI and Uvicorn in Each Environment

#### 1. **Production Environment**:
```bash
cd /path/to/your/production/app
pyenv local fastapi-prod
pip install fastapi uvicorn python-dotenv
```

#### 2. **Development Environment**:
```bash
cd /path/to/your/development/app
pyenv local fastapi-dev
pip install fastapi uvicorn python-dotenv
```

### Step 5: Configure MariaDB Databases

1. **Install MariaDB** if you haven't already:
   ```bash
   sudo apt install mariadb-server mariadb-client
   ```

2. **Set up separate databases** for production and development:
   ```bash
   sudo mysql -u root -p
   CREATE DATABASE prod_db;
   CREATE DATABASE dev_db;
   CREATE USER 'prod_user'@'localhost' IDENTIFIED BY 'prod_password';
   CREATE USER 'dev_user'@'localhost' IDENTIFIED BY 'dev_password';
   GRANT ALL PRIVILEGES ON prod_db.* TO 'prod_user'@'localhost';
   GRANT ALL PRIVILEGES ON dev_db.* TO 'dev_user'@'localhost';
   FLUSH PRIVILEGES;
   EXIT;
   ```

3. In your FastAPI app, use environment variables (or `.env` files) to switch between the two databases:
   - **Production `.env`:**
     ```ini
     DATABASE_URL=mysql://prod_user:prod_password@localhost/prod_db
     DEBUG=False
     ```

   - **Development `.env`:**
     ```ini
     DATABASE_URL=mysql://dev_user:dev_password@localhost/dev_db
     DEBUG=True
     ```

### Step 6: Configure Uvicorn as Systemd Services

For production and development, create systemd service files to manage your Uvicorn processes.

1. **Production Service** (`/etc/systemd/system/fastapi-prod.service`):
   ```ini
   [Unit]
   Description=FastAPI Production Server
   After=network.target

   [Service]
   User=your_user
   WorkingDirectory=/path/to/production/app
   ExecStart=/path/to/your/pyenv/versions/fastapi-prod/bin/uvicorn app:app --host 127.0.0.1 --port 8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

2. **Development Service** (`/etc/systemd/system/fastapi-dev.service`):
   ```ini
   [Unit]
   Description=FastAPI Development Server
   After=network.target

   [Service]
   User=your_user
   WorkingDirectory=/path/to/development/app
   ExecStart=/path/to/your/pyenv/versions/fastapi-dev/bin/uvicorn app:app --host 127.0.0.1 --port 8001
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

Reload systemd and start both services:
```bash
sudo systemctl daemon-reload
sudo systemctl start fastapi-prod.service
sudo systemctl start fastapi-dev.service
sudo systemctl enable fastapi-prod.service
sudo systemctl enable fastapi-dev.service
```

### Step 7: Configure Nginx for Reverse Proxy

We’ll configure Nginx to act as a reverse proxy to forward traffic to the appropriate Uvicorn instance for production and development environments.

1. **Create Nginx Configuration File** (`/etc/nginx/sites-available/fastapi`):
   ```nginx
   # Production server
   server {
       listen 80;
       server_name prod.example.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }

       location /static/ {
           alias /path/to/your/production/static/;
       }
   }

   # Development server
   server {
       listen 80;
       server_name dev.example.com;

       location / {
           proxy_pass http://127.0.0.1:8001;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }

       location /static/ {
           alias /path/to/your/development/static/;
       }
   }
   ```

2. **Enable the Nginx Configuration**:
   ```bash
   sudo ln -s /etc/nginx/sites-available/fastapi /etc/nginx/sites-enabled/
   sudo nginx -t  # Test configuration
   sudo systemctl restart nginx
   ```

### Step 8: Running the Servers

1. **For Production**:
   - Nginx listens on `prod.example.com` and forwards requests to Uvicorn running on port `8000`.

   Visit `http://prod.example.com` to access your production FastAPI app.

2. **For Development**:
   - Nginx listens on `dev.example.com` and forwards requests to Uvicorn running on port `8001`.

   Visit `http://dev.example.com` to access your development FastAPI app.

### Summary of Steps:
1. Install system dependencies, including Nginx and MariaDB.
2. Install `pyenv` for Python version management.
3. Install Python, FastAPI, and Uvicorn for both production and development environments.
4. Configure MariaDB with separate databases for production and development.
5. Set up systemd services to run Uvicorn instances on different ports for production and development.
6. Configure Nginx to reverse proxy traffic to the appropriate Uvicorn instance based on the server name.
7. Start and test both the production and development servers.

This setup ensures that your production and development environments are isolated yet managed on the same server with `pyenv` and Nginx handling the reverse proxy configuration.


## MacOS

Here’s a comprehensive guide for setting up **FastAPI**, **Uvicorn**, **Nginx**, **pyenv**, and **MariaDB** on a **macOS machine** for both production and development environments, with configuration for Nginx as a reverse proxy.

### Step 1: Install System Dependencies

First, ensure that you have **Homebrew** installed. If not, install it by running:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Now, install the necessary packages:

```bash
brew install openssl readline sqlite3 xz zlib mariadb nginx
```

### Step 2: Install `pyenv` for Python Version Management

1. Install `pyenv`:
   ```bash
   brew install pyenv
   ```

2. Add `pyenv` to your shell startup file (`~/.bash_profile` or `~/.zshrc`):
   ```bash
   echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
   echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
   echo 'eval "$(pyenv init --path)"' >> ~/.zshrc
   echo 'eval "$(pyenv init -)"' >> ~/.zshrc
   source ~/.zshrc
   ```

3. Verify `pyenv` installation:
   ```bash
   pyenv --version
   ```

### Step 3: Install Python Versions Using `pyenv`

1. Install Python 3.11.4 (or any desired version) using `pyenv`:
   ```bash
   pyenv install 3.11.4
   ```

2. Create virtual environments for both production and development:

- **Production**:
  ```bash
  pyenv virtualenv 3.11.4 fastapi-prod
  ```

- **Development**:
  ```bash
  pyenv virtualenv 3.11.4 fastapi-dev
  ```

### Step 4: Install FastAPI and Uvicorn in Each Environment

#### 1. **Production Environment**:
```bash
cd /path/to/your/production/app
pyenv local fastapi-prod
pip install fastapi uvicorn python-dotenv
```

#### 2. **Development Environment**:
```bash
cd /path/to/your/development/app
pyenv local fastapi-dev
pip install fastapi uvicorn python-dotenv
```

### Step 5: Configure MariaDB Databases

1. Start MariaDB:
   ```bash
   brew services start mariadb
   ```

2. Secure the installation and create databases:
   ```bash
   mysql_secure_installation
   ```

3. Create separate databases for production and development:
   ```bash
   mysql -u root -p
   CREATE DATABASE prod_db;
   CREATE DATABASE dev_db;
   CREATE USER 'prod_user'@'localhost' IDENTIFIED BY 'prod_password';
   CREATE USER 'dev_user'@'localhost' IDENTIFIED BY 'dev_password';
   GRANT ALL PRIVILEGES ON prod_db.* TO 'prod_user'@'localhost';
   GRANT ALL PRIVILEGES ON dev_db.* TO 'dev_user'@'localhost';
   FLUSH PRIVILEGES;
   EXIT;
   ```

4. In your FastAPI app, use environment variables (or `.env` files) to switch between the two databases:
   - **Production `.env`:**
     ```ini
     DATABASE_URL=mysql://prod_user:prod_password@localhost/prod_db
     DEBUG=False
     ```

   - **Development `.env`:**
     ```ini
     DATABASE_URL=mysql://dev_user:dev_password@localhost/dev_db
     DEBUG=True
     ```

### Step 6: Configure Uvicorn to Run on Different Ports

For macOS, you won’t use systemd (as it’s more commonly used on Linux). Instead, you can manually run Uvicorn instances for production and development on different ports:

1. **For Production**:
   ```bash
   cd /path/to/your/production/app
   pyenv activate fastapi-prod
   uvicorn app:app --host 127.0.0.1 --port 8000
   ```

2. **For Development**:
   ```bash
   cd /path/to/your/development/app
   pyenv activate fastapi-dev
   uvicorn app:app --host 127.0.0.1 --port 8001
   ```

You can run both Uvicorn instances simultaneously for production and development.

### Step 7: Configure Nginx for Reverse Proxy

#### 1. Start and enable Nginx:
```bash
brew services start nginx
```

#### 2. Configure Nginx for reverse proxy by editing the Nginx config file (`/usr/local/etc/nginx/nginx.conf`):

Open the file for editing:
```bash
sudo nano /usr/local/etc/nginx/nginx.conf
```

Add the following configurations for production and development:

```nginx
# Production server
server {
    listen 80;
    server_name prod.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;  # Uvicorn for Production
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/your/production/static/;
    }
}

# Development server
server {
    listen 80;
    server_name dev.example.com;

    location / {
        proxy_pass http://127.0.0.1:8001;  # Uvicorn for Development
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/your/development/static/;
    }
}
```

Save and close the file, then restart Nginx:
```bash
sudo nginx -t  # Check for errors
sudo nginx -s reload
```

### Step 8: Running the Servers

1. **For Production**:
   - Nginx listens on `prod.example.com` and forwards requests to Uvicorn running on port `8000`.

   Access `http://prod.example.com` to interact with your production FastAPI app.

2. **For Development**:
   - Nginx listens on `dev.example.com` and forwards requests to Uvicorn running on port `8001`.

   Access `http://dev.example.com` to interact with your development FastAPI app.

### Summary of Steps:

1. Install system dependencies (Homebrew, MariaDB, Nginx).
2. Install and configure `pyenv` for managing Python versions and virtual environments.
3. Install FastAPI and Uvicorn in production and development environments.
4. Set up separate MariaDB databases for production and development.
5. Manually run Uvicorn for production and development on different ports.
6. Configure Nginx as a reverse proxy to forward requests to the correct Uvicorn instance based on the server name.
7. Test and run both production and development environments.

This setup allows you to manage separate FastAPI applications for production and development on a single macOS machine with proper separation using `pyenv` and Nginx.

## Windows OS

Setting up **FastAPI**, **Uvicorn**, **Nginx**, **pyenv**, and **MariaDB** on **Windows 11** without using Windows Subsystem for Linux (WSL) is slightly different due to the platform-specific tooling. Here's a detailed guide to achieve this setup for both production and development environments on a Windows 11 machine.

### Step 1: Install System Dependencies

For this setup, you'll need to install **Python**, **MariaDB**, and **Nginx** on Windows, along with configuring virtual environments and managing separate environments for production and development.

#### 1.1 Install Python

You can use the official Python installer for Windows:

1. Download Python from the official Python website: [Python Download](https://www.python.org/downloads/).
2. Run the installer and ensure that you **check the option to add Python to your PATH**.
3. Verify Python installation:
   ```bash
   python --version
   ```

#### 1.2 Install `pyenv-win` for Managing Python Versions

`pyenv-win` is a tool for managing multiple Python versions on Windows. Follow these steps to install it:

1. Open **PowerShell** as an Administrator and install `pyenv-win`:
   ```powershell
   git clone https://github.com/pyenv-win/pyenv-win.git $HOME\.pyenv
   ```

2. Add `pyenv` to your system's `PATH`. Open **System Properties** -> **Environment Variables**, and add the following to the `PATH` in the **User Variables** section:
   ```plaintext
   %USERPROFILE%\.pyenv\pyenv-win\bin
   %USERPROFILE%\.pyenv\pyenv-win\shims
   ```

3. Verify the `pyenv` installation:
   ```bash
   pyenv --version
   ```

#### 1.3 Install MariaDB

1. Download the MariaDB installer for Windows from the official website: [MariaDB Download](https://mariadb.org/download/).
2. Run the installer and follow the setup instructions. Make sure to set a root password during installation.
3. After installation, you can start the MariaDB service via the Windows Services Manager or by running:
   ```bash
   net start MariaDB
   ```

#### 1.4 Install Nginx

1. Download the Nginx Windows version from the official website: [Nginx for Windows](https://nginx.org/en/download.html).
2. Extract the files to a directory (e.g., `C:\nginx`).
3. Nginx can be started by running `nginx.exe` inside the `nginx` directory:
   ```bash
   cd C:\nginx
   start nginx
   ```

You should see Nginx running at `http://localhost`. To stop Nginx, use:
```bash
nginx -s stop
```

### Step 2: Install Python Versions Using `pyenv`

Once `pyenv` is installed, install the desired Python version:

1. Install Python 3.11.4 using `pyenv`:
   ```bash
   pyenv install 3.11.4
   ```

2. Create virtual environments for production and development:

- **Production**:
  ```bash
  pyenv virtualenv 3.11.4 fastapi-prod
  ```

- **Development**:
  ```bash
  pyenv virtualenv 3.11.4 fastapi-dev
  ```

### Step 3: Install FastAPI and Uvicorn in Each Environment

#### 3.1 Production Environment:

1. Open a new terminal (or PowerShell) and activate the production environment:
   ```bash
   pyenv local fastapi-prod
   ```

2. Install FastAPI, Uvicorn, and other dependencies:
   ```bash
   pip install fastapi uvicorn python-dotenv
   ```

#### 3.2 Development Environment:

1. Open another terminal (or PowerShell) and activate the development environment:
   ```bash
   pyenv local fastapi-dev
   ```

2. Install FastAPI, Uvicorn, and other dependencies:
   ```bash
   pip install fastapi uvicorn python-dotenv
   ```

### Step 4: Configure MariaDB Databases

1. Open the **MariaDB Command Line Client** or use a MySQL client like **DBeaver** to create separate databases for production and development:
   ```sql
   CREATE DATABASE prod_db;
   CREATE DATABASE dev_db;
   CREATE USER 'prod_user'@'localhost' IDENTIFIED BY 'prod_password';
   CREATE USER 'dev_user'@'localhost' IDENTIFIED BY 'dev_password';
   GRANT ALL PRIVILEGES ON prod_db.* TO 'prod_user'@'localhost';
   GRANT ALL PRIVILEGES ON dev_db.* TO 'dev_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

2. Use `.env` files to configure the database URLs for your FastAPI applications:
   - **Production `.env`:**
     ```ini
     DATABASE_URL=mysql://prod_user:prod_password@localhost/prod_db
     DEBUG=False
     ```

   - **Development `.env`:**
     ```ini
     DATABASE_URL=mysql://dev_user:dev_password@localhost/dev_db
     DEBUG=True
     ```

### Step 5: Run Uvicorn on Different Ports

On Windows, you’ll run Uvicorn manually on different ports for production and development.

1. **For Production**:
   ```bash
   cd /path/to/your/production/app
   pyenv activate fastapi-prod
   uvicorn app:app --host 127.0.0.1 --port 8000
   ```

2. **For Development**:
   ```bash
   cd /path/to/your/development/app
   pyenv activate fastapi-dev
   uvicorn app:app --host 127.0.0.1 --port 8001
   ```

You can run these two Uvicorn instances in separate terminals.

### Step 6: Configure Nginx for Reverse Proxy

Edit the Nginx configuration file (`C:\nginx\conf\nginx.conf`) to add reverse proxy settings for both production and development environments.

1. Open the Nginx configuration file in a text editor (e.g., Notepad or Visual Studio Code).
2. Add the following configuration for production and development:

```nginx
# Production server
server {
    listen 80;
    server_name prod.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;  # Uvicorn for Production
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias C:/path/to/your/production/static/;
    }
}

# Development server
server {
    listen 80;
    server_name dev.example.com;

    location / {
        proxy_pass http://127.0.0.1:8001;  # Uvicorn for Development
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias C:/path/to/your/development/static/;
    }
}
```

3. Save the configuration and restart Nginx by running the following commands in the terminal:
```bash
cd C:\nginx
nginx -s reload
```

### Step 7: Running the Servers

1. **For Production**:
   - Nginx will forward requests made to `prod.example.com` to the Uvicorn instance running on port `8000`.

   Access the app via `http://prod.example.com`.

2. **For Development**:
   - Nginx will forward requests made to `dev.example.com` to the Uvicorn instance running on port `8001`.

   Access the app via `http://dev.example.com`.

### Summary of Steps:

1. Install system dependencies (Python, MariaDB, Nginx).
2. Install and configure `pyenv-win` for managing Python versions and virtual environments.
3. Install FastAPI and Uvicorn in both production and development environments.
4. Set up separate MariaDB databases for production and development.
5. Manually run Uvicorn on different ports for production and development.
6. Configure Nginx to act as a reverse proxy and forward traffic to the appropriate Uvicorn instance based on the server name.
7. Run and test both production and development environments on your Windows 11 machine.

This setup ensures you have separate environments for production and development on Windows 11 with proper reverse proxy handling through Nginx.
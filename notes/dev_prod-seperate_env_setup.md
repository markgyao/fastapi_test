To run two separate FastAPI web servers for production and development on the same physical machine, you can follow this approach:

### 1. **Use Different Ports:**
   FastAPI web servers need to listen on different ports since both will be running on the same machine.

   - **Production server**: Configure FastAPI to run on a specific port, e.g., `8000`.
   - **Development server**: Run FastAPI on a different port, e.g., `8001`.

   You can modify the startup command for FastAPI to specify the port using the `uvicorn` command:

   - **Production**: 
     ```bash
     uvicorn app:app --host 0.0.0.0 --port 8000 --reload
     ```
   - **Development**:
     ```bash
     uvicorn app:app --host 0.0.0.0 --port 8001 --reload
     ```

### 2. **Environment Separation:**
   You need to configure your application to behave differently in production and development. A common approach is to use environment variables or configuration files:

   - **Create `.env` files** for both environments.
   - Use a Python package like `python-dotenv` to load these environment variables.

   Example `.env` file for production:
   ```ini
   DATABASE_URL=mysql://user:password@localhost/prod_db
   DEBUG=False
   ```

   Example `.env` file for development:
   ```ini
   DATABASE_URL=mysql://user:password@localhost/dev_db
   DEBUG=True
   ```

   Modify your FastAPI app to load the appropriate configuration based on the environment.

### 3. **Database Separation:**
   You already use MariaDB, so create two separate databases for development and production:

   - **Production DB**: Create a database called `prod_db`.
   - **Development DB**: Create a database called `dev_db`.

   Make sure the FastAPI app connects to the appropriate database based on the environment.

### 4. **Using Systemd for Service Management:**
   To run both servers as background services, you can create two separate `systemd` service files.

   - **Create Production Service:**
     `/etc/systemd/system/fastapi-prod.service`
     ```ini
     [Unit]
     Description=FastAPI Production Server
     After=network.target

     [Service]
     User=your_user
     WorkingDirectory=/path/to/production/app
     ExecStart=/path/to/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
     Restart=always

     [Install]
     WantedBy=multi-user.target
     ```

   - **Create Development Service:**
     `/etc/systemd/system/fastapi-dev.service`
     ```ini
     [Unit]
     Description=FastAPI Development Server
     After=network.target

     [Service]
     User=your_user
     WorkingDirectory=/path/to/development/app
     ExecStart=/path/to/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8001
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

### 5. **Optional: Use Nginx for Reverse Proxy**
   To make both servers accessible via a single domain name, use Nginx to reverse proxy based on subdomains or paths.

   - Example Nginx config for separating production and development:
     ```nginx
     server {
         server_name example.com;

         location / {
             proxy_pass http://127.0.0.1:8000;  # Production
         }

         location /dev/ {
             proxy_pass http://127.0.0.1:8001;  # Development
         }
     }
     ```

### Summary of Key Points:
- **FastAPI servers** should listen on different ports (e.g., `8000` for production and `8001` for development).
- **Databases**: Use different MariaDB databases for production and development.
- **Environment**: Use environment variables or configuration files to manage differences between production and development.
- Optionally, use **Nginx** for reverse proxy to handle routing traffic.

This setup will allow you to run both production and development environments on the same physical machine while keeping them separate.


## installation steps:

Here's a list of everything you need to install before configuring and setting up your environment for running both production and development FastAPI servers on your Ubuntu machine. I'll also show you how to use `pyenv` for managing the Python environments in this setup.

### 1. **Install System Dependencies**
You'll need to install some basic system packages for Python development, MariaDB, and web server management.

#### a. **Install Python Build Dependencies:**
```bash
sudo apt update
sudo apt install -y make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```

#### b. **Install MariaDB (if not already installed):**
```bash
sudo apt install mariadb-server mariadb-client
```

#### c. **Install Nginx (optional for reverse proxy setup):**
```bash
sudo apt install nginx
```

### 2. **Install `pyenv` for Python Version Management**

#### a. **Install `pyenv` Dependencies:**
Make sure the required packages for `pyenv` are installed (you might have installed most of these already in the previous step).
```bash
sudo apt install -y build-essential curl libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl
```

#### b. **Install `pyenv`:**
```bash
curl https://pyenv.run | bash
```

After running the script, add the following lines to your `.bashrc` (or `.zshrc` if you're using Zsh):
```bash
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

Then restart your shell:
```bash
exec "$SHELL"
```

#### c. **Verify `pyenv` Installation:**
```bash
pyenv --version
```

### 3. **Install Python Version for Your FastAPI Applications:**

Using `pyenv`, install the specific version of Python you want to use (e.g., Python 3.11.4):

```bash
pyenv install 3.11.4
```

Create separate `pyenv` environments for production and development:

#### d. **Create Production Environment:**
```bash
pyenv virtualenv 3.11.4 fastapi-prod
```

#### e. **Create Development Environment:**
```bash
pyenv virtualenv 3.11.4 fastapi-dev
```

### 4. **Set Up Your FastAPI Applications:**

#### a. **Set the Environment for Production:**
```bash
cd /path/to/your/production/app
pyenv local fastapi-prod
```

#### b. **Install FastAPI and Uvicorn in Production Environment:**
```bash
pip install fastapi uvicorn python-dotenv
```

#### c. **Set the Environment for Development:**
```bash
cd /path/to/your/development/app
pyenv local fastapi-dev
```

#### d. **Install FastAPI and Uvicorn in Development Environment:**
```bash
pip install fastapi uvicorn python-dotenv
```

### 5. **Configure MariaDB Databases:**

Create two separate MariaDB databases, one for production and one for development:
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

### 6. **Nginx Configuration (Optional):**
If you want to use Nginx for reverse proxy, install and configure it as described earlier.

```bash
sudo nano /etc/nginx/sites-available/your_domain
```
Add your Nginx configuration, save, and then enable the site.

```bash
sudo ln -s /etc/nginx/sites-available/your_domain /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

### 7. **Configure Systemd Services for FastAPI:**
Create systemd service files for both production and development, as described in the earlier response.

### Summary of Installation Steps:

1. Install system dependencies.
2. Install MariaDB and Nginx (optional).
3. Install `pyenv` and set it up.
4. Install Python versions using `pyenv` and create virtual environments.
5. Install FastAPI and Uvicorn in each environment.
6. Set up MariaDB databases for production and development.
7. Optionally, configure Nginx for reverse proxy.

After this setup, you'll have two separate FastAPI servers running on different ports, managed with `pyenv` and connecting to separate MariaDB databases.

### 1) **Uvicorn Installation:**

You’ll need to install **Uvicorn** in both the production and development environments as the ASGI server to run your FastAPI applications. Since you are using `pyenv` for managing your Python environments, Uvicorn should be installed separately for each environment. Here's how to do it:

#### Install Uvicorn in the Production Environment:

After activating the production environment (`fastapi-prod`) with `pyenv`:
```bash
cd /path/to/your/production/app
pyenv local fastapi-prod
pip install uvicorn
```

#### Install Uvicorn in the Development Environment:

After activating the development environment (`fastapi-dev`) with `pyenv`:
```bash
cd /path/to/your/development/app
pyenv local fastapi-dev
pip install uvicorn
```

Now, both environments will have Uvicorn installed and can be used to serve your FastAPI applications.

### 2) **More About Nginx vs. Uvicorn**

#### **Uvicorn**: 
Uvicorn is an ASGI server, specifically designed to run asynchronous web applications (like FastAPI). It serves your FastAPI app by listening for requests on a specific port and directly processing them.

However, Uvicorn alone is **not enough** for handling real-world production-level traffic for several reasons:
- Uvicorn is single-threaded and can handle limited concurrency on its own.
- It doesn't efficiently handle things like SSL termination (i.e., HTTPS).
- It is not optimized for handling static files (CSS, images, etc.).
- It lacks advanced load-balancing features for distributing traffic across multiple instances.

#### **Nginx**:
Nginx is a **full-fledged web server** and **reverse proxy**. It can handle a wider range of tasks than Uvicorn, making it a great front-end for your FastAPI application in production.

Key features of Nginx:
- **SSL Termination**: Handles HTTPS connections and certificates.
- **Reverse Proxy**: Forwards requests to Uvicorn running your FastAPI app, allowing you to hide the app behind Nginx.
- **Load Balancing**: Can distribute traffic across multiple FastAPI instances for scalability.
- **Caching**: Can cache static content or responses to reduce the load on Uvicorn.
- **Static File Handling**: Efficiently serves static files like images, CSS, or JavaScript that don't need to go through FastAPI.

#### **How Uvicorn and Nginx Work Together in Production:**

In a production environment, the common approach is to use **Nginx as a reverse proxy** in front of Uvicorn:

1. **Nginx** listens on port 80 (HTTP) or 443 (HTTPS) for incoming requests from users.
2. Nginx forwards requests (via a reverse proxy) to **Uvicorn**, which is running the FastAPI app on a separate internal port (like `8000`).
3. **Uvicorn** processes the requests (interacting with your Python FastAPI app) and sends the response back to Nginx.
4. Nginx then forwards the response back to the client (the user's browser or API client).

This setup makes the web server more robust, secure, and scalable.

### Example Nginx Configuration

Here’s a sample Nginx configuration for handling your production FastAPI app running on Uvicorn:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;  # Uvicorn is running on port 8000
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/static/files;  # Serve static files directly with Nginx
    }
}
```

### Why Use Nginx?
- **Security**: Nginx can be used to manage HTTPS (SSL certificates), protect against DDoS attacks, and more.
- **Efficiency**: Nginx is extremely fast for serving static content (like CSS or images) and can manage a high number of simultaneous connections.
- **Load Balancing**: Nginx can distribute traffic to multiple Uvicorn workers or instances, improving performance.
- **Caching**: Helps reduce load on the backend by caching responses or static content.

### Conclusion:
- **Uvicorn** is the core ASGI server responsible for running your FastAPI application.
- **Nginx** is a powerful, full-featured web server and reverse proxy that sits in front of Uvicorn in production environments to improve security, performance, and scalability.

For **development**, you may not need Nginx. But for **production**, Nginx will significantly improve the robustness and scalability of your FastAPI deployment.


Great question! Let's break down the role of **Nginx** and how it works with **Uvicorn** in more detail.

### 1. **Nginx as a Reverse Proxy**
Nginx acts as a **middleman** between the client (e.g., a web browser) and the FastAPI application (running under Uvicorn). Nginx doesn't handle actual application logic, but it **forwards** requests to Uvicorn, which does.

- **Forwarding Requests**: Nginx simply forwards any requests that need to be processed by your FastAPI application to Uvicorn.
- **Handling Static Files**: Nginx can serve static files (like images, CSS, JavaScript) directly without involving Uvicorn.

### 2. **How Nginx Knows What to Forward**
Nginx is configured with rules (called **location blocks**) that tell it what to do with each type of request.

- **If the request is for your FastAPI application**, Nginx will forward it to Uvicorn.
- **If the request is for a static file** (e.g., an image, a CSS file, or a JavaScript file), Nginx can handle it directly to save Uvicorn from unnecessary work.

#### Example Breakdown:

Consider this Nginx configuration:
```nginx
server {
    listen 80;
    server_name example.com;

    # Forward all requests to Uvicorn (FastAPI app)
    location / {
        proxy_pass http://127.0.0.1:8000;  # Uvicorn's address
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Serve static files like images, CSS, and JavaScript directly
    location /static/ {
        alias /path/to/static/files;  # Path to your static files
    }
}
```

### **What Each Location Block Does:**

#### **1. Forwarding Application Requests to Uvicorn**
```nginx
location / {
    proxy_pass http://127.0.0.1:8000;
}
```
- This means that **any request that starts with `/`** (which includes almost everything) will be **forwarded to Uvicorn**.
- Example: If a user visits `http://example.com/api/users`, Nginx will forward that request to Uvicorn at `http://127.0.0.1:8000/api/users`.
- **Why is this useful?** Uvicorn (running the FastAPI app) is the one that knows how to handle requests like `/api/users` because it's defined in your FastAPI routes.

#### **2. Serving Static Files**
```nginx
location /static/ {
    alias /path/to/static/files;
}
```
- This block tells Nginx: "If the request URL starts with `/static/`, don't bother forwarding it to Uvicorn. Instead, serve the file directly from the `/path/to/static/files` directory."
- Example: If the user visits `http://example.com/static/style.css`, Nginx will find the file `style.css` in `/path/to/static/files` and send it directly to the client without bothering Uvicorn.

### **What Nginx Does vs. What Uvicorn Does:**

- **Nginx**: Handles general web server tasks like:
  - SSL termination (handling HTTPS).
  - Efficiently serving static content like images, CSS, and JS.
  - Acting as a reverse proxy to forward specific requests to Uvicorn.
  - Caching, load balancing, and security features.
  
- **Uvicorn (FastAPI)**: Handles application-level tasks:
  - Processing business logic.
  - Running Python code to handle dynamic routes (e.g., `/api/users`).
  - Managing database interactions, sessions, or any complex server-side logic.

### 3. **Why Not Just Use Uvicorn Alone?**

Uvicorn is great for running your FastAPI application, but it’s **not a full web server**. Here are some things Uvicorn doesn’t do well on its own, which is why Nginx is helpful:

- **Serving Static Files**: Uvicorn can serve static files, but it’s not optimized for it. Nginx, on the other hand, is extremely fast and efficient for serving static files (such as images, CSS, or JavaScript).
- **SSL (HTTPS)**: Nginx handles SSL certificates and manages HTTPS connections. This isn't Uvicorn's job.
- **Load Balancing**: If you have multiple instances of Uvicorn running for scalability, Nginx can distribute incoming traffic across those instances.
- **Security**: Nginx can help block malicious traffic, handle rate limiting, and provide other security features like DDoS protection.
- **Efficiency**: Nginx is much more efficient for serving static content and handling things like keep-alive connections, saving Uvicorn from wasting resources on these tasks.

### 4. **Example Request Flow**

1. A user accesses `http://example.com/api/users`.
2. Nginx sees that this request is not for a static file (it doesn't start with `/static/`).
3. Nginx forwards this request to Uvicorn on port `8000`, where your FastAPI app is running.
4. FastAPI processes the request, interacts with the database if needed, and returns a response.
5. Uvicorn sends the response back to Nginx.
6. Nginx forwards the response back to the user.

For static files:

1. A user accesses `http://example.com/static/style.css`.
2. Nginx sees that this request is for a static file (because it starts with `/static/`).
3. Nginx retrieves the file from the `/path/to/static/files` directory and sends it directly to the user—no need to bother Uvicorn.

### **Summary:**
- **Nginx** handles general web server tasks like SSL, load balancing, and efficiently serving static content.
- **Uvicorn** focuses on running the FastAPI app and processing dynamic requests.
- Nginx knows which requests to forward to Uvicorn (based on the location blocks you configure) and which to handle itself (like serving static files).
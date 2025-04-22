# Simple LFI Demonstration with Gunicorn and NGINX

## 1.0 Deploying the Flask app

To host the vulnerable application, a standard Ubuntu server environment is configured using Gunicorn as the WSGI server and NGINX as the reverse proxy.   This mirros a common production deployment however, we will be making our app intentionally vulnerable.

## 1.1 Server Setup

### 1.1.1 **Prerequisites**: 
- We will use an Ubuntu 22.04 Server.  Essential packages for Python development and environment management are install:

``` bash
sudo apt update
sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools python3-venv nginx
```
### 1.1.2 **Python VENV**:
- To isolate dependencies, we will create a virtual environment within this cloned github project. (ex. ```/home/valette/feisty-ferret```):
```bash
git clone https://github.com/mikey-p-codes/feisty-ferret.git
cd feisty-ferret
python3 -m venv venv
source venv/bin/activate
```

### 1.1.3 **Install Dependencies**:
- Flask and Gunicorn are installed within the virtual environment.  To make this easier use the requirements.txt file and run:

```bash
pip install -r requirements.txt
```
### 1.1.4 **WSGI Entrypoint**:
- Use wsgi.py to provide an entrypoint for Gunicorn

### 1.1.5 **Gunicorn Systemd Servce**: 
A systemd service file (```/etc/systemd/system/feisty-ferrit.service```) is created to manage the Gunicorn process, ensuring it starts on boot and runs as a designated user in our case ```valette```.  Gunicorn is configured to bind to a Unix socket for communication with Nginx.

```ini
[Unit]
Description=Gunicorn instance to serve LFI Vulnerable Flask app
After=network.target

User=valette
Group=www-data
WorkingDirectory="PATH=/home/valette/feisty-ferret/venv/bin"
ExecStart=/home/valette/feisty-ferret/venv/bin/gunicron --workers 3 --bind unix:/home/valette/fiesty-ferret/feisty-ferret.sockk

[Install]
WantedBy=multi-user.target
```

Then start and enable the service:

```bash
sudo systemctl start feisty-ferret
sudo systemctl enable feisty-ferret
sudo systemctl status feisty-ferret
```

### 1.1.6 **Nginx Configuration**: 
Nginx acts as a reverse proxy, receiving client requests on port 80 and forwarding them to the Gunicorn application server via our unix socket.  A configuration file is created at ```/etc/nginx/sites-available/feisty-ferret```:

```Nginx
server {
    listen 80;
    localhost; # replace this with an ip address or fqdn
    
    location / {
        include proxy_params;
        proxy_pass http://unix/valette/feisty-ferret/feisty-ferrt.sock;
    }

# *** CRITICA FOR DEMO VULNERABILITY***
# This block allows direct access to uploaded files, including our webshell
# We will not configure PHP-FPM instead opt for a simpler demo.
# This demo may rely on the webshell executing commands using the system's PHP interpreter
# directly, triggered by access the file with this location block

location /uploads {
    alias /var/www/html/uploads;
# Allow direct access to uploaded files
    try_files $uri $uri/=404;
    }
}
```

### 1.1.7 **Enable Site and Firewall**: 
The Nginx site is enabled, configuration tested and the service restarted.  The firewall will be configured to allow HTTP traffic.

```bash
sudo ln -s /etc/nginx/sites-available/feisty-ferret /etc/nginx/sites-enabled/ # symlink sites
sudo nginx -t # test the nginx configuration
sudo systemctl restart nginx # restart nginx service
sudo ufw allow 'Nginx Full' # Allow HTTP/S
sudo ufw delete allow 5000 # remove direct access to the Flask dev port
```
## 1.2 Configuring the Host with an overly permissive user
To demonstrate full system compromise after initial access, a user account with intentionally esxcessive privileges is configured on the server.  This will involve granting passwordless ```sudo``` access, completely ignoring the concept of least privilege.

### 1.2.1 **Create User:**
A standard user account (ex. ```valette```) is created using the ```adduser``` command:
```bash
sudo adduser valette
```
Follow the prompts to set a password and user information.

### 1.2.2 **Grant Basic Sudo**:
```valette``` is added to the ```sudo``` group, which normally grants the user ability to run commands as root after authentication.

```bash
sudo usermod -aG sudo valette
groups valette # command to verify the group membership
```
Testing access can be done by switching to the user ```su - valette``` and running ```sudo whoami``` which will prompt for ```valette```'s password.

### 1.2.3 **Configure Passwordles Sudo**:
This step introduces our security risk.  The ```visudo``` command, which performs syntax checking to ensure that admins don't get locked out, is used to edit the sudoers configuration file safely.  A dedicated file is created in ```/etc/sudoers.d/``` to manage this specific users rule, which is considere better practice than editing the main ```/etc/sudoers``` file.

```bash
sudo visudo -f /etc/sudoers.d/99-valette-nopasswd

# Add the following line to the file

valette ALL=(ALL:ALL) NOPASSWD: ALL
```
This will grant ```valette``` the ability to run any command (```ALL```) on any host (```ALL=```) as any user and any group (```  (ALL:ALL)  ```) without providing a password (```NOPASSWD:```).

### 1.2.4 **Verify Passwordless Sudo**:
Switch to the user and run a command requiring root privileges:
```bash
su - valette
sudo whoami
```
The command should execute without prompting for a password.

### 1.2.5 **Root Shell Access**:
The ```NOPASSWD: ALL``` configuration allows ```valette``` to directly obtain a root shell without a password prompt using:

```bash
sudo bash
# or
sudo su -
```

This setup completely ignores the Principle of Least Privilege and will be leveraged to complete our attack.


# 2.0 Deploying Command and Control Infrastructure

Now that our target environment is setup, lets get to work on our attack infrastructure.

## 2.1 **Install and Configure Mythic C2**

We will use Mythic as our attack infrastructure for our simulation.  For more information on Mythic I highly recommend heading over to https://github.com/its-a-feature/Mythic to get in depth information on the framework.  Additional information about the framework is beyond the scope of this document.

### 2.1.1 **Prerequisites**:
Ensure the Docker and Docker Compose plugin are installed on the attacker machine.  Check https://docs.docker.com/engine/install and https://docs.docker.com/compose/install/ for detailed installation instructions.

### 2.1.2 **Clone Mythic Repo**:
```bash
git clone https://github.com/its-a-feature/Mythic --depth 1
```

### 2.1.3 **Build ```mythic-cli```**:

```mythic-cli``` is the command line interface for managing Mythic and must be built locally.
```bash
cd Mythic
sudo make
```
### 2.1.4 **Initial Configuration**:
Mythic uses a ```.env``` file (```Mythic/.env```) for configuration.  The file can be generated at startup.  This demonstration doesn't require an advanced setup, so we can start Mythic and let Mythic set the default environment variables.

```bash
sudo ./mythic-cli start
```

### 2.1.6 **Access UI**:
Connect to the Mythic Web Interface via ```https://attacker.ip:7443``` and log in with the credentials created at start up.  To find the credentials  you can:

```bash
cat .env | grep "MYTHIC_ADMIN_PASSWORD"
```
This will print the created admin credential to STDOUT.

## 2.2 **Install Mythic Payloads and C2 Profiles**
Mythic payloads are installed from github.  You can get all payload information here:

https://mythicmeta.github.io/overview/

Profiles like ```http, smb, tcp, dns``` need to be configured to communicate with your agents.

as you will see when installing the Medusa agent, we need to install our profile with ```mythic-cli```

```bash
sudo ./mythic-cli isntall github https://github.com/MythicC2Profiles/http
```

We are going to grab the ```Medusa``` payload and install it using ```mythic-cli```

### 2.2.1 **Install Medusa Agent**

Use ```mythic-cli``` to install the Medusa agent:
```bash
sudo./mythic-cli install github https://github.com/MythicAgents/Medusa
```

#! /bin/bash
echo "Running startup-script"
apt-get update
apt-get install -y build-essential apt-transport-https ca-certificates curl software-properties-common

echo "Installing Docker CE"
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

apt-get update
apt-get install -y docker-ce

echo "Installing NGNX"
apt-get update && apt-get install -y nginx-full

# echo "Installing NVM and NODE"
# curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.11/install.sh | bash
# export NVM_DIR="$HOME/.nvm"
# [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
# nvm install --lts
# nvm use --lts
# node -v
curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
apt-get install -y nodejs

echo "Update NPM"
npm i -g npm

echo "Installing PM2"
npm i -g pm2

echo "Deleting previous installation if not new"
if [ -d "/acople" ] 
  then
    cd /acople
    if [ -d "tink-commerce"]
      then
        rm -rf tink-commerce
      else
        echo "Error: Directory /acople/tink-commerce does not exists."
    fi
  else
    cd / && mkdir acople && cd acople
fi

echo "Running DB container"
docker run --name store-db -d -p 27017:27017 -v /acople/store-db:/data/db mongo:latest || docker start store-db

echo "Installing Tink-commerce"
git clone https://github.com/jjgumucio/tink-commerce_dituti.git tink-commerce

echo "Creating directories and files for logs"
mkdir -p tink-commerce/logs/api
touch  tink-commerce/logs/api/out.log
touch  tink-commerce/logs/api/error.log
touch  tink-commerce/logs/api/all.log

mkdir -p tink-commerce/logs/store
touch  tink-commerce/logs/store/out.log
touch  tink-commerce/logs/store/error.log
touch  tink-commerce/logs/store/all.log

echo "Change settings files"
cd /acople/tink-commerce/config
rm admin.js server.js store.js
mv admin.production.js admin.js
mv server.production.js server.js
mv store.production.js store.js
cd ..

echo "Installing dependencies"
npm i

echo "Building tink-commerce"
npm run build

# Change the email and domain to customize the client
echo "Running setup script"
npm run setup clementeserranosutil@gmail.com http://dituti.com

echo "Running the apps"
pm2 start process.json

echo "Setting up NGINX"
cd /etc/nginx/sites-available

echo '
server {
        # Dynamic image resizing server
        listen 127.0.0.1:8888;
        server_tokens off;
        location ~ "^/resize/(?<entity>\w+)/(?<id>\w+)/(?<width>[1-9][0-9][0-9]{1}|[1][0-9][0-9][0-9]{1})/(?<file>.+)$" {
                alias /acople/tink-commerce/public/content/images/$entity/$id/$file;
                image_filter_buffer 20M;
                image_filter_jpeg_quality 85;
                image_filter_interlace on;
                image_filter resize $width -;
        }
}

# Cache rule for resized images
proxy_cache_path /tmp/nginx-images-cache2/ levels=1:2 keys_zone=images:10m inactive=30d max_size=5g use_temp_path=off;

server {
        listen 80 default_server;
        server_name _;

        gzip              on;
        gzip_comp_level   2;
        gzip_min_length   1024;
        gzip_vary         on;
        gzip_proxied      expired no-cache no-store private auth;
        gzip_types        application/x-javascript application/javascript application/xml application/json text/xml text/css text$

        client_body_timeout 12;
        client_header_timeout 12;
        reset_timedout_connection on;
        send_timeout 10;
        server_tokens off;
        client_max_body_size 50m;

        expires 1y;
        access_log off;
        log_not_found off;
        root /acople/tink-commerce/public/content;

        location ~ "^/images/(?<entity>\w+)/(?<id>\w+)/(?<width>[1-9][0-9][0-9]{1}|[1][0-9][0-9][0-9]{1})/(?<file>.+)$" {
                # /images/products/id/100/file.jpg >>> Proxy to internal image resizing server
                proxy_pass http://127.0.0.1:8888/resize/$entity/$id/$width/$file;
                proxy_cache images;
                proxy_cache_valid 200 30d;
        }

        location /admin {
                alias /acople/tink-commerce/public/admin/;
		            try_files /index.html /index.html;
        }

        location /admin-assets/ {
                alias /acople/tink-commerce/public/admin-assets/;
        }

        location /assets/ {
                alias /acople/tink-commerce/theme/assets/;
        }

        location /sw.js {
                root /acople/tink-commerce/theme/assets/;
        }

        location ~ ^/(api|ajax|ws)/ {
                # Proxy to NodeJS
                expires off;
                proxy_pass       http://127.0.0.1:3001;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection "upgrade";
        }

        location / {
                try_files $uri @proxy;
        }

        location @proxy {
                # Proxy to NodeJS
                expires off;
                proxy_pass       http://127.0.0.1:3000;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
        }
}
' > default

# nginx -t && service nginx reload
sudo systemctl reload nginx

echo "Tink-commerce READY"

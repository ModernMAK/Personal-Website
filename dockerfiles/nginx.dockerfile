FROM nginx
# Setup Env
EXPOSE 80 443

COPY ../nginx/https.conf /etc/nginx/nginx.conf
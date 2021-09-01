FROM nginx
# Setup Env
EXPOSE 80

COPY ../nginx/http.conf /etc/nginx/nginx.conf
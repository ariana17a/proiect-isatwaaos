# Single-stage: copy the pre-built Vite output into nginx
# Run `npm run build` locally before `docker compose up` if dist/ is stale.
FROM nginx:1.27-alpine

# Remove default nginx welcome page
RUN rm -rf /usr/share/nginx/html/*

COPY dist/ /usr/share/nginx/html/

# Nginx config that handles SPA client-side routing
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]

# Use official Nginx image (Alpine for smaller size)
FROM nginx:alpine

# Copy custom Nginx configuration
COPY default.conf /etc/nginx/conf.d/default.conf

# Create directory for Symfony public files
RUN mkdir -p /var/www/html/app/public

# Expose port 80
EXPOSE 80

# Start Nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
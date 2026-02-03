# Use Node.js LTS Alpine for smaller image
FROM node:20-alpine

# Install necessary packages
RUN apk add --no-cache \
    shadow \
    bash

# Accept build arguments for user/group IDs
ARG USER_ID=1000
ARG GROUP_ID=1000

# Create user and group with matching IDs
RUN if [ "$GROUP_ID" != "0" ]; then \
        if getent group $GROUP_ID; then \
            GROUP_NAME=$(getent group $GROUP_ID | cut -d: -f1); \
        else \
            addgroup -g $GROUP_ID vueuser; \
            GROUP_NAME=vueuser; \
        fi; \
    else \
        GROUP_NAME=root; \
    fi && \
    if [ "$USER_ID" != "0" ]; then \
        if getent passwd $USER_ID; then \
            USER_NAME=$(getent passwd $USER_ID | cut -d: -f1); \
        else \
            adduser -D -u $USER_ID -G $GROUP_NAME vueuser; \
            USER_NAME=vueuser; \
        fi; \
    else \
        USER_NAME=root; \
    fi && \
    echo "export USER_NAME=$USER_NAME" >> /etc/profile && \
    echo "export GROUP_NAME=$GROUP_NAME" >> /etc/profile

# Set working directory
WORKDIR /app

# Change ownership of working directory
RUN if [ "$USER_ID" != "0" ]; then \
        USER_NAME=$(getent passwd $USER_ID | cut -d: -f1); \
        chown -R $USER_NAME:$(getent group $GROUP_ID | cut -d: -f1) /app; \
    fi

# Switch to non-root user if not root
USER ${USER_ID}:${GROUP_ID}

# Expose Vue CLI's default dev server port
EXPOSE 8080

# Start development server
# Note: The actual command will be run from docker-compose with volume mounted
CMD ["npm", "run", "serve"]

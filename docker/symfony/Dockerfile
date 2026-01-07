# Use official PHP 8.2 FPM base image
FROM php:8.2-fpm

# Arguments for user ID mapping (prevents permission issues)
ARG USER_ID=1000
ARG GROUP_ID=1000

# Set working directory
WORKDIR /var/www/html

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    libpng-dev \
    libonig-dev \
    libxml2-dev \
    libzip-dev \
    zip \
    unzip \
    libicu-dev \
    && rm -rf /var/lib/apt/lists/*

# Install PHP extensions required by Symfony 6.4
RUN docker-php-ext-install \
    pdo_mysql \
    mbstring \
    exif \
    pcntl \
    bcmath \
    gd \
    intl \
    opcache \
    zip \
    xml \
    dom \
    simplexml \
    xmlwriter \
    tokenizer

# Install APCu (recommended for Symfony caching and proxy-manager-bridge)
RUN pecl install apcu \
    && docker-php-ext-enable apcu

# Configure PHP for development
RUN cp "$PHP_INI_DIR/php.ini-development" "$PHP_INI_DIR/php.ini"

# Add custom PHP configuration
RUN echo "memory_limit=256M" >> "$PHP_INI_DIR/conf.d/custom.ini" \
    && echo "upload_max_filesize=20M" >> "$PHP_INI_DIR/conf.d/custom.ini" \
    && echo "post_max_size=20M" >> "$PHP_INI_DIR/conf.d/custom.ini" \
    && echo "max_execution_time=300" >> "$PHP_INI_DIR/conf.d/custom.ini" \
    && echo "date.timezone=UTC" >> "$PHP_INI_DIR/conf.d/custom.ini" \
    && echo "realpath_cache_size=4096K" >> "$PHP_INI_DIR/conf.d/custom.ini" \
    && echo "realpath_cache_ttl=600" >> "$PHP_INI_DIR/conf.d/custom.ini"

# Configure OPcache for development (disable caching for instant code changes)
RUN echo "opcache.enable=1" >> "$PHP_INI_DIR/conf.d/opcache.ini" \
    && echo "opcache.validate_timestamps=1" >> "$PHP_INI_DIR/conf.d/opcache.ini" \
    && echo "opcache.revalidate_freq=0" >> "$PHP_INI_DIR/conf.d/opcache.ini" \
    && echo "opcache.max_accelerated_files=10000" >> "$PHP_INI_DIR/conf.d/opcache.ini" \
    && echo "opcache.memory_consumption=192" >> "$PHP_INI_DIR/conf.d/opcache.ini" \
    && echo "opcache.interned_strings_buffer=16" >> "$PHP_INI_DIR/conf.d/opcache.ini"

# Configure APCu for Symfony proxy-manager-bridge
RUN echo "apc.enable_cli=1" >> "$PHP_INI_DIR/conf.d/apcu.ini"

# Install Composer (latest version)
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# Install Symfony CLI
RUN curl -sS https://get.symfony.com/cli/installer | bash \
    && mv /root/.symfony*/bin/symfony /usr/local/bin/symfony

# Create symfony user with matching UID/GID from host
RUN groupadd -g ${GROUP_ID} symfony \
    && useradd -u ${USER_ID} -g symfony -m -s /bin/bash symfony \
    && chown -R symfony:symfony /var/www

# Configure PHP-FPM to run as symfony user
RUN sed -i 's/user = www-data/user = symfony/g' /usr/local/etc/php-fpm.d/www.conf \
    && sed -i 's/group = www-data/group = symfony/g' /usr/local/etc/php-fpm.d/www.conf

# Switch to symfony user
USER symfony

# Expose PHP-FPM port
EXPOSE 9000

# Switch back to root for PHP-FPM startup
USER root

# Start PHP-FPM
CMD ["php-fpm"]
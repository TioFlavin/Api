# Use uma imagem base com PHP
FROM php:8.0-cli

# Instalar extensões necessárias
RUN apt-get update && apt-get install -y libpng-dev libjpeg-dev libfreetype6-dev && \
    docker-php-ext-configure gd --with-freetype --with-jpeg && \
    docker-php-ext-install gd

# Definir o diretório de trabalho
WORKDIR /usr/src/app

# Copiar os arquivos do projeto para o contêiner
COPY . .

# Instalar dependências do Composer
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer && \
    composer install

# Executar o servidor PHP
CMD ["php", "-S", "0.0.0.0:8080", "-t", "api"]

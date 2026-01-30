FROM alpine:3.18

# Dépendances
RUN apk add --no-cache ca-certificates curl openssl bash

# URL stable pour mkcert (architecture linux/amd64 par défaut)
ARG MKCERT_FOR=linux/amd64
ARG MKCERT_URL=https://dl.filippo.io/mkcert/latest?for=${MKCERT_FOR}

# Télécharge et installe mkcert
RUN mkdir -p /usr/local/bin \
 && curl -fsSL "${MKCERT_URL}" -o /usr/local/bin/mkcert \
 && chmod +x /usr/local/bin/mkcert \
 && /usr/local/bin/mkcert -version

WORKDIR /data
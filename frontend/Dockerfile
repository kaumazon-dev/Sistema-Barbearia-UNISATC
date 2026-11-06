# Etapa 1: build do React com Vite. O Node so existe aqui; a imagem final
# leva apenas os arquivos estaticos.
FROM node:22-alpine AS build

WORKDIR /app

# Dependencias antes do codigo: mudar uma tela nao reinstala o node_modules.
COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Vazio = mesma origem (/api/v1), resolvido pelo proxy do nginx abaixo.
ARG VITE_API_URL=
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# Etapa 2: nginx sem root, servindo o build e repassando /api ao backend.
FROM nginxinc/nginx-unprivileged:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 8080

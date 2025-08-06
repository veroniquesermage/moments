# Étape 1 : build Angular
FROM node:20 AS build
WORKDIR /app
COPY . .
RUN npm install
RUN npm run build --prod

# Étape 2 : Nginx pour servir le frontend
FROM nginx:alpine
COPY --from=build /app/dist/moments-front/browser /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

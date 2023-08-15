FROM node:16.13.0-buster-slim

WORKDIR /app/frontend

COPY ./package.json ./package-lock.json ./

RUN npm install
COPY . .
RUN npm run build

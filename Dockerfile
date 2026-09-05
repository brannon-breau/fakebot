FROM node:20-alpine

WORKDIR /app

COPY package.json ./
RUN npm install --omit=dev

COPY commands.json ./
COPY src ./src

CMD ["node", "src/index.js"]

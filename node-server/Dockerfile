FROM node:20-alpine

WORKDIR /app/

COPY package.json ./

RUN npm i -g ts-node typescript

RUN npm i

COPY . .

EXPOSE 4000

CMD ["npx", "tsx", "--watch", "src/server.ts"]

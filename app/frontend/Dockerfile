FROM node:20-alpine

WORKDIR /app

# Copy only package files first
COPY package*.json ./

# Install dependencies
RUN npm install

# Then copy the rest (excluding node_modules thanks to .dockerignore)
COPY . .

# Build for production
RUN npm run build

EXPOSE 3000
ENV HOST=0.0.0.0
ENV PORT=3000

CMD ["node", ".output/server/index.mjs"]
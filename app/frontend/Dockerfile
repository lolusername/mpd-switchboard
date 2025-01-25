FROM node:18-alpine

WORKDIR /app

# Install dependencies first (better caching)
COPY package*.json ./
RUN npm install

# Copy the rest of the application
COPY . .

# Build for production
RUN npm run build

# Expose the port
EXPOSE 3000

# Set host to allow external connections
ENV HOST=0.0.0.0
ENV PORT=3000

# Start the server
CMD ["node", ".output/server/index.mjs"]
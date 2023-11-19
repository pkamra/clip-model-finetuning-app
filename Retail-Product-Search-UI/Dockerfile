# Use Node.js image as the base image
FROM node:16 as build-stage

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application files to the working directory
COPY . .

# Build the Vue.js application
RUN npm run build

# Use nginx as the base image for serving the production build
FROM nginx:latest as production-stage

# Copy the built application from the previous stage to nginx directory
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Update the default nginx configuration to listen on port 8081
RUN sed -i 's/80/8081/g' /etc/nginx/conf.d/default.conf

# Expose port 8081
EXPOSE 8081

# Start nginx server
CMD ["nginx", "-g", "daemon off;"]

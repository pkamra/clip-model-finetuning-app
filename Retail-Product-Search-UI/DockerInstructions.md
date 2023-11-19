# Build the Docker image
docker build -t retail-product-search-ui .

# Run the Docker container on port 8081
docker run -p 8081:8081 retail-product-search-ui

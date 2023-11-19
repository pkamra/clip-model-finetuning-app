# to build Docker images
docker build -t retrieve-images .

# to run docker container
docker run -e AWS_ACCESS_KEY_ID=xxxx -e AWS_SECRET_ACCESS_KEY=xxxx  -e AWS_DEFAULT_REGION=us-east-1 -p 8080:8080  retrieve-images

# to prune 
docker system prune --volumes -a -f

# to find container id
docker ps

# check logs realtime for docker container
docker logs --follow  xxxxx


# 1. Build image
docker build -t gps_crawler .

# 2. Run (specify the port 8000)
docker run -p 8000:8000 -d gps_crawler
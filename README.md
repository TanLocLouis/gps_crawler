# 1. Build and Run
1. Build image: ```sudo docker build -t bike .```
2. Set environment variables in ```.env``` file.
3. Run container from image: ```sudo docker-compose up```
# 2. Create a user
1. Access to running container: ```sudo docker exec -it bike sh```  
2. Then create a new user: ```python gps_crawler.py --add```  
Enter new ```username``` and new ```password```

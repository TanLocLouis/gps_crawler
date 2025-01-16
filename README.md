# Summary
This repo crawl data from my tracking vehicle provider, store in .csv file, show datas on simple web page.

# 1. Build image
```docker build -t gps_crawler .```

# 2. Run (specify the port 8000)
```docker run -p 8000:8000 -d gps_crawler```

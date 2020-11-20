#### Discussion:
Here we explore the dataset, we look for insights that provide information to the business and to the modeling stage.

#### Run:
Just run `docker-compose up` and docker will do all the work for you. 

Pay attention that once `jupyter noteboook` is up, docker port 8888 is being binded to your local port 8889 (this according to `docker-compose` file), so if in your terminal the url that `jupyter notebook` tells you is something like `http://127.0.0.1:8888/notebooks/...` you should replace the url by something like this `http://127.0.0.1:8889/notebooks/...`

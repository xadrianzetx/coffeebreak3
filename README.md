# coffeebreak3

Setting up Airflow pipeline to send pictures of doggos

## Run

```
sudo docker build . --tag coffeebreak3:v1 && sudo docker run -d -p 8080:8080 -v $(pwd)/dags:/usr/local/airflow/dags --network host
```

## Base image

[puckel/docker-airflow](https://github.com/puckel/docker-airflow)
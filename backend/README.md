# BACKEND

## 1. Description

The backend of this project is designed to facilitate data harvesting, processing, and uploading using a combination of Elasticsearch, Fission, and Kafka. The system integrates various functions and configurations to automate the collection, processing, and storage of data from different sources, including Twitter and Mastodon. The backend architecture leverages Elasticsearch for data indexing and search, Fission for function execution, and Kafka for message brokering.


## 2. Fission 

### 2.1 Table of Contents

- [fission](#fission)
    - [functions](#functions)
        - [addobservations.py](#addobservations.py): a general method that add different data into different Elasticsearch index
        - [enqueue.py](#enqueue.py): enqueue the message to a Kafka topic. 
        - [incomeprocessor.py](#incomeprocessor.py): used to process income data from SUDO
        - [mastodonharvester1.py](#mastodonharvester1.py): harvest data from aus.social Mastodon server
        - [mastodonharvester2.py](#mastodonharvester2.py): harvest data from mastodon.au Mastodon server
        - [mastodonprocessor.py](#mastodonprocessor.py): used to process harvested Mastodon data
        - [retrieve.py](#retrieve.py): used to retrieve all documents from specified Elasticsearch index
        - [search.py](#search.py): used to documents that contains specific keyword from specified Elasticsearch index
        - [twitterprocessor.py](#twitterprocessor.py): used to process Twitter data from Spartan
        - [wordcloud.py](#wordcloud.py): used to generate word frequency that can be used for plotting wordcloud
    - [specs](#specs)
        - [README](#README)
        - [configmap-es.yaml](#configmap-es.yaml): store the username and password for Elasticsearch
        - [configmap-mastodon.yaml](#configmap-mastodon.yaml): store the server name and token for Mastodon
        - [env-python3.yaml](#env-python3.yaml): customize fission environment named `python3` for running Python 3.9 functions
        - [fission-deployment-config.yaml](#fission-deployment-config.yaml)
        - [function-addobservations.yaml](#function-addobservations.yaml)
        - [function-enqueue.yaml](#function-enqueue.yaml)
        - [function-incomeprocessor.yaml](#function-incomeprocessor.yaml)
        - [function-mastodonharvester1.yaml](#function-mastodonharvester1.yaml)
        - [function-mastodonharvester2.yaml](#function-mastodonharvester2.yaml)
        - [function-mastodonprocessor.yaml](#function-mastodonprocessor.yaml)
        - [function-retrieve.yaml](#function-retrieve.yaml)
        - [function-search.yaml](#function-search.yaml)
        - [function-twitterprocessor.yaml](#function-twitterprocessor.yaml)
        - [function-wordcloud.yaml](#function-wordcloud.yaml)
        - [mqtrigger-addobservations.yaml](#mqtrigger-addobservations.yaml)
        - [mqtrigger-incomeprocessor.yaml](#mqtrigger-incomeprocessor.yaml): processes JSON messages from the `income` topic using the `incomeprocessor` function
        - [mqtrigger-mastodonprocessor.yaml](#mqtrigger-mastodonprocessor.yaml): processes JSON messages from the `mastodon` topic using the `mastodonprocessor` function
        - [mqtrigger-twitterprocessor.yaml](#mqtrigger-twitterprocessor.yaml): processes JSON messages from the `twitter` topic using the `twitterprocessor` function
        - [route-enqueue.yaml](#route-enqueue.yaml): directs POST requests made to the `/enqueue/{topic}` URL path to the `enqueue` function
        - [route-retrieve-get1.yaml](#route-retrieve-get1.yaml)
        - [route-search-get1.yaml](#route-search-get1.yaml)
        - [route-search-get2.yaml](#route-search-get2.yaml)
        - [route-search-get3.yaml](#route-search-get3.yaml)
        - [route-search-get4.yaml](#route-search-get4.yaml)
        - [route-wordcloud-get1.yaml](#route-wordcloud-get1.yaml)
        - [route-wordcloud-get2.yaml](#route-wordcloud-get2.yaml)
        - [route-wordcloud-get3.yaml](#route-wordcloud-get3.yaml)
        - [route-wordcloud-get4.yaml](#route-wordcloud-get4.yaml)
        - [timetrigger-mastodonharvester1.yaml](#timetrigger-mastodonharvester1.yaml): harvest Mastodon data every 5 minutes
        - [timetrigger-mastodonharvester2.yaml](#timetrigger-mastodonharvester2.yaml): harvest Mastodon data every 5 minutes
    - [Dockerfile](#Dockerfile): create Dockerfile to customize fission envionment

### 2.2 Steps

- apply configmap to the cluster 

```shell
kubectl apply -f ./specs/configmap-mtd.yaml

# check
kubectl get pods -n kafka
```

- Create fission environment
- https://hub.docker.com/repository/docker/cccteam41/fission-python-3.9-env/general

```shell
# build and push docker image
docker build -t cccteam41/fission-python-3.9-env:v3 .
docker push cccteam41/fission-python-3.9-env:latest


# create fission env with docker image
fission env create --spec --name python3 --image cccteam41/fission-python-3.9-env:latest --builder fission/python-builder
```

- Create fission function

```shell
fission function create --spec \
    --name mastodonharvester1 \
    --env python3 \
    --code ./functions/mastodonharvester1.py \
    --fntimeout=300 \
    --configmap configmap-mastodon

fission function create --spec \
    --name mastodonharvester2 \
    --env python3 \
    --code ./functions/mastodonharvester2.py \
    --fntimeout=300 \
    --configmap configmap-mastodon

fission function create --spec \
    --name enqueue \
    --env python3 \
    --code ./functions/enqueue.py

fission function create --spec \
    --name mastodonprocessor \
    --env python3 \
    --code ./functions/mastodonprocessor.py
fission function create --spec \
    --name twitterprocessor \
    --env python3 \
    --code ./functions/twitterprocessor.py

fission function create --spec \
    --name incomeprocessor \
    --env python3 \
    --code ./functions/incomeprocessor.py

fission function create --spec \
    --name addobservations \
    --env python3 \
    --code ./functions/addobservations.py \
    --configmap configmap-es
fission function create --spec \
    --name retrieve \
    --env python3 \
    --code ./functions/retrieve.py \
    --fntimeout=300 \
    --configmap configmap-es

fission function create --spec \
    --name search \
    --env python3 \
    --code ./functions/search.py \
    --fntimeout=300 \
    --configmap configmap-es

fission function create --spec \
    --name wordcloud \
    --env python3 \
    --code ./functions/wordcloud.py \
    --fntimeout=300 \
    --configmap configmap-es

```

- Create fission mqtrigger

```shell
fission mqtrigger create --spec \
    --name mastodonprocessor \
    --function mastodonprocessor \
    --mqtype kafka \
    --mqtkind keda \
    --topic topic-mastodon \
    --resptopic topic-observations \
    --errortopic topic-errors \
    --maxretries 3 \
    --metadata bootstrapServers=mycluster-kafka-bootstrap.kafka.svc:9092 \
    --metadata consumerGroup=my-group \
    --cooldownperiod=30 \
    --pollinginterval=5

fission mqtrigger create --spec \
    --name twitterprocessor \
    --function twitterprocessor \
    --mqtype kafka \
    --mqtkind keda \
    --topic topic-twitter \
    --resptopic topic-observations \
    --errortopic topic-errors \
    --maxretries 3 \
    --metadata bootstrapServers=mycluster-kafka-bootstrap.kafka.svc:9092 \
    --metadata consumerGroup=my-group \
    --cooldownperiod=30 \
    --pollinginterval=5

fission mqtrigger create --spec \
    --name incomeprocessor \
    --function incomeprocessor \
    --mqtype kafka \
    --mqtkind keda \
    --topic topic-income \
    --resptopic topic-observations \
    --errortopic topic-errors \
    --maxretries 3 \
    --metadata bootstrapServers=mycluster-kafka-bootstrap.kafka.svc:9092 \
    --metadata consumerGroup=my-group \
    --cooldownperiod=30 \
    --pollinginterval=5

fission mqtrigger create --spec \
    --name addobservations\
    --function addobservations \
    --mqtype kafka \
    --mqtkind keda \
    --topic topic-observations \
    --errortopic topic-errors \
    --maxretries 3 \
    --metadata bootstrapServers=mycluster-kafka-bootstrap.kafka.svc:9092 \
    --metadata consumerGroup=my-group \
    --cooldownperiod=30 \
    --pollinginterval=5

```
- Create fission route


```shell
fission route create --spec \
    --name enqueue \
    --url "/enqueue/{topic}" \
    --method POST \
    --createingress \
    --function enqueue

fission route create --spec \
    --url '/retrieve/{server:[a-zA-Z0-9_]+}' \
    --function retrieve \
    --name retrieve-get1 \
    --createingress \
    --method GET 

fission route create --spec \
    --url '/search/{server:[a-zA-Z0-9]+}/keyword/{keyword:[a-zA-Z0-9]+}' \
    --function search \
    --name search-get1 \
    --createingress \
    --method GET 

fission route create --spec \
    --url '/search/{server:[a-zA-Z0-9]+}/keyword/{keyword:[a-zA-Z0-9]+}/size/{size:[0-9]+}' \
    --function search \
    --name search-get2 \
    --createingress \
    --method GET 

fission route create --spec \
    --url '/search/{server:[a-zA-Z0-9]+}/keyword/{keyword:[a-zA-Z0-9]+}/start/{start:[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]}/end/{end:[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]}' \
    --function search \
    --name search-get3 \
    --createingress \
    --method GET 

fission route create --spec \
    --url '/search/{server:[a-zA-Z0-9]+}/keyword/{keyword:[a-zA-Z0-9]+}/start/{start:[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]}/end/{end:[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]}/size/{size:[0-9]+}' \
    --function search \
    --name search-get4 \
    --createingress 
    --method GET

fission route create --spec \
    --url '/wordcloud/{server:[a-zA-Z0-9]+}/keyword/{keyword:[a-zA-Z0-9]+}' \
    --function wordcloud \
    --name wordcloud-get1 \
    --createingress \
    --method GET 

fission route create --spec \
    --url '/wordcloud/{server:[a-zA-Z0-9]+}/keyword/{keyword:[a-zA-Z0-9]+}/size/{size:[0-9]+}' \
    --function wordcloud \
    --name wordcloud-get2 \
    --createingress \
    --method GET 

fission route create --spec \
    --url '/wordcloud/{server:[a-zA-Z0-9]+}/keyword/{keyword:[a-zA-Z0-9]+}/start/{start:[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]}/end/{end:[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]}' \
    --function wordcloud \
    --name wordcloud-get3 \
    --createingress \
    --method GET 

fission route create --spec \
    --url '/wordcloud/{server:[a-zA-Z0-9]+}/keyword/{keyword:[a-zA-Z0-9]+}/start/{start:[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]}/end/{end:[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]}/size/{size:[0-9]+}' \
    --function wordcloud \
    --name wordcloud-get4 \
    --createingress \
    --method GET 

```
- Create fission timer


```shell
fission timer create --spec \
    --name mastodonharvester1 \
    --function mastodonharvester1 \
    --cron "@every 5m"
        
fission timer create --spec \
    --name mastodonharvester2 \
    --function mastodonharvester2 \
    --cron "@every 5m" 
```


## 3. Kafka: 

### 3.1 Table of Contents

- [kafka](#kafka)
    - [topic](#topic)
        - [topic-errors.yaml](#topic-errors.yaml)
        - [topic-income.yaml](#topic-income.yaml)
        - [topic-mastodon.yaml](#topic-mastodon.yaml)
        - [topic-obervations.yaml](#topic-obervations.yaml)
        - [topic-twitter.yaml](#topic-twitter.yaml)
    - [kafka-cluster.yaml](#kafka-cluster.yaml): used to create Kafka cluster

### 3.2 Kafka: Steps

- Create Kafka cluster 

```shell
kubectl apply -f ./kafka/kafka-cluster.yaml -n kafka
```

- Create Kafka topic

```shell
kubectl apply -f ./kafka/topics/topic-errors.yaml --namespace kafka
kubectl apply -f ./kafka/topics/topic-income.yaml --namespace kafka
kubectl apply -f ./kafka/topics/topic-mastodon.yaml --namespace kafka
kubectl apply -f ./kafka/topics/topic-observations.yaml --namespace kafka
kubectl apply -f ./kafka/topics/topic-twitter.yaml --namespace kafka
```










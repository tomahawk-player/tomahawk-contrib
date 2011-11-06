#!/bin/bash  
#Change to path, ey?
SCRAPER_PATH=/home/charts/tomahawk-contrib/charts/src/scrapers
API_SCRAPER_PATH=$SCRAPER_PATH/apis
LOG_PATH=$SCRAPER_PATH/logs

if [ ! -d "$SCRAPER_PATH" -o ! -d "$API_SCRAPER_PATH" ]; then 
  echo "Some paths does not exist"
  exit
fi

if [ ! -d "$LOG_PATH" ]; then 
  echo "$LOG_PATH does not exist, creating..."
  mkdir $LOG_PATH
  if [ ! -d "$LOG_PATH" ]; then
    echo "Failed to create $LOG_PATH";
    exit
  fi
fi


if [ ! -n "$1" ]
then
  echo "Usage: `basename $0` string:name {optional string:pythonVersion }"
  exit
fi 
 
PYTHONV=${2:-python}

case "$1" in
  "itunes") cd $SCRAPER_PATH && scrapy crawl itunes.com --set FEED_FORMAT=json &> $LOG_PATH/$1.$(date +\%Y\%m\%d).log
;;
  "billboard") cd $SCRAPER_PATH && scrapy crawl billboard.com --set FEED_FORMAT=json &> $LOG_PATH/$1.$(date +\%Y\%m\%d).log
;;
  "rdio") cd $API_SCRAPER_PATH && $PYTHONV $1.py &> $LOG_PATH/$1.$(date +\%Y\%m\%d).log   
;;
  "wah") cd $API_SCRAPER_PATH && $PYTHONV $1.py &> $LOG_PATH/$1.$(date +\%Y\%m\%d).log
;;
esac

#!/usr/bin/env bash

NAME=linkchecker.zip

rm -f $NAME

zip -r $NAME . -x "*.idea/*" -x "*.pyc"  -x "pack.sh" -x "test/*" -x "build/*" -x "data/*" -x "*egg*" -x "*.pid" -x "scrapyd_service/logs/*" -x "scrapyd_service/items/*" -x "scrapyd_service/dbs/*" -x "crawls/*" -x "ssh_config" -x "*.pem"

mv $NAME /Users/geo/Copy
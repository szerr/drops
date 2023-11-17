#!/bin/sh

bakPath="/backup/db"

mysqldump --databases <dbname> -h <dbhost> -u <user> -p<pwd> | xz > $bakPath/`date "+%Y-%m-%d"`.sql.xz

rm -f $bakPath/`date "+%Y-%m-%d" -d "-16day"`.sql.xz

#!/bin/sh

for obj in /srv/drops/*
do
    cd $obj
    echo $obj
    pwd
    drops backup -c -d %Y-%m-%d -t /srv/backup  -f
    cd /srv/drops/
done
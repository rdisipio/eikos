#!/bin/bash

msg="commit"
[ ! -z $1 ] && msg=$1

git commit -a -m $msg
git push origin master


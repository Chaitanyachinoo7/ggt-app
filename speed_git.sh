#!/bin/bash
set -ex
message="${1}"

git checkout dev2 
git pull 
git add .
git commit -m ${message}
git push -u origin dev2

git checkout dev
git pull 
git merge dev2
git push -u origin dev

git checkout qa
git pull 
git merge dev
git push -u origin qa

git checkout master
git pull 
git merge qa
git push -u origin master

git checkout production-patient
git pull 
git merge master
git push -u origin production-patient


git checkout dev2

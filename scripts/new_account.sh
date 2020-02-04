#!/bin/bash


if [ "$*" -ne 2 ] 
then
  echo "Need 2 args, project name end and billing acocunt"
fi

if [

### Create the project
gcloud projects create qwiklabs-gcp-${1} --enable-cloud-apis --folder=396521612403
gcloud beta billing projects link qwiklabs-gcp-${1} --billing-account=${2}


#!/bin/bash

input=$1
file_name="${input##*/}"
aws s3 cp $1 $file_name

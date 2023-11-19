#!/bin/bash
BUCKET_NAME="$1"


BUILD_ROOT=/tmp/model_path
S3_PATH=s3://${BUCKET_NAME}/models/clip/model.tar.gz


rm -rf $BUILD_ROOT
mkdir $BUILD_ROOT
cp new_clip_model.pt $BUILD_ROOT
cd $BUILD_ROOT && tar -czvf model.tar.gz .
aws s3 cp $BUILD_ROOT/model.tar.gz  $S3_PATH
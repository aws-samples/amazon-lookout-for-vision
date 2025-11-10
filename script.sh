#!/bin/bash

# Make sure we're in the right directory before running the loop
cd "$(dirname "$0")/amazon-lookout-for-vision/aliens-dataset"
# Copy anomaly images with .anomaly.png suffix
for file in anomaly/*.png; do
  if [ -f "$file" ]; then
    filename=$(basename "$file")
    cp "$file" "all/${filename}.anomaly.png"
  fi
done
# Count files to verify
echo "Normal images: $(find normal -name "*.png" | wc -l)"
echo "Anomaly images: $(find anomaly -name "*.png" | wc -l)"
echo "Total images in all directory: $(find all -type f | wc -l)"
# Upload to S3
aws s3 cp all/ s3://<BUCKET_NAME>/aliens-dataset-all/ --recursive
# Clean up - remove the cloned repository
cd ../..
rm -rf amazon-lookout-for-vision

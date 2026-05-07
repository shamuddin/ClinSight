#!/bin/bash
cd /opt/clinsight
mkdir -p backend/data/images
# Copy from dist demo-images to backend data path
cp -n frontend/react-app/dist/demo-images/*.png backend/data/images/ 2>/dev/null
# Also copy from public if dist is missing
cp -n frontend/react-app/public/demo-images/*.png backend/data/images/ 2>/dev/null
echo "IMAGES_OK"
ls backend/data/images/ | wc -l

#!/bin/bash

set -eu

BACKEND_DIR="backend-src"

cd ..
pushd $BACKEND_DIR

MODULES=$( find . -type d -d 1 )
for module in $MODULES; do
  echo "=> $( pwd )"
  echo "Building $module"
  pushd "$module"
  [ ! -r "package.json" ] && popd && continue
  [ -r "${module}.zip" ] && rm "${module}.zip"
  npm install && zip -q -r $module.zip .
  echo "Done"
  echo
  popd
done


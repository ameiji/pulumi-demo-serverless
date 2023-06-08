#!/usr/bin/env bash
set -euE -o pipefail
set -x

pulumi_cmd=${PULUMI_PATH=$(which pulumi)}
echo "Pulumi = $(which $pulumi_cmd)"

get_stack_name(){
  set +x
  files=$(ls -1 .)
  for f in $files; do
    if [[ $f =~ ^Pulumi ]]; then
      stack_name=$(echo "$f" | sed -E 's/Pulumi\.(.*)\.yaml/\1/')
      break
    fi
  done

  echo "$stack_name"
  set -x
}

stack_name="$(get_stack_name)"
echo "Stack name is = $stack_name"

$pulumi_cmd stack init "$stack_name" || true
$pulumi_cmd stack select "$stack_name"

./build-backend.sh

$pulumi_cmd up --yes

./build-frontend.sh

$pulumi_cmd up --yes
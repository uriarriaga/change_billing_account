#!/bin/bash
# Copyright 2019 Théo Chamley
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Usage:
#   bash change_billing_account.sh OLD_BILLING_ACCOUNT_ID NEW_BILLING_ACCOUNT_ID [PROJECT_ID_TO_SKIP...]

containsElement () {
  local e match="$1"
  shift
  for e; do [[ "$e" == "$match" ]] && return 0; done
  return 1
}

OLD_BILLING_ID=$1
NEW_BILLING_ID=$2
shift 2
EXCEPTIONS=$@

PROJECTS=$(gcloud beta billing projects list --billing-account=${OLD_BILLING_ID} --format='value(projectId)')

for p in $PROJECTS; do
  if containsElement $p ${EXCEPTIONS}; then
    echo "Project $p in exception list, skipping."
    continue
  else
    echo "Reassigning project $p billing acount from ${OLD_BILLING_ID} to ${NEW_BILLING_ID}"
    gcloud beta billing projects link $p --billing-account=${NEW_BILLING_ID}
  fi
done
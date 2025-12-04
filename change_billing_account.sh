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
#   bash change_billing_account.sh NEW_BILLING_ACCOUNT_ID CSV_FILE

NEW_BILLING_ID=$1
CSV_FILE=$2

if [[ -z "$NEW_BILLING_ID" || -z "$CSV_FILE" ]]; then
  echo "Usage: $0 NEW_BILLING_ACCOUNT_ID CSV_FILE"
  exit 1
fi

if [[ ! -f "$CSV_FILE" ]]; then
    echo "File not found: $CSV_FILE"
    exit 1
fi

while IFS="," read -r project_id rest || [ -n "$project_id" ]; do
  # Clean up project_id (trim spaces)
  project_id=$(echo "$project_id" | xargs)

  # Skip header (simple check if first line is 'project_id')
  if [[ "$project_id" == "project_id" ]]; then
      continue
  fi

  if [[ -z "$project_id" ]]; then
    continue
  fi

  echo "Reassigning project $project_id billing account to ${NEW_BILLING_ID}"
  gcloud beta billing projects link "$project_id" --billing-account="${NEW_BILLING_ID}"
done < "$CSV_FILE"

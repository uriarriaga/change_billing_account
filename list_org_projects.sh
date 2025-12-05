#!/bin/bash
# Copyright 2024 Google LLC
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
#   bash list_org_projects.sh ORG_ID [OUTPUT_FILE]
#
# This script lists all projects in a GCP Organization using the Cloud Asset API.
# It requires the Cloud Asset API to be enabled and sufficient permissions (e.g. Viewer on the Org).

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 ORG_ID [OUTPUT_FILE]"
    exit 1
fi

ORG_ID=$1
OUTPUT_FILE=${2:-projects.csv}

echo "Listing projects in Organization ${ORG_ID}..."

gcloud asset search-all-resources \
    --scope="organizations/${ORG_ID}" \
    --asset-types="cloudresourcemanager.googleapis.com/Project" \
    --format="csv(name, additionalAttributes.projectId, additionalAttributes.projectNumber, state, displayName)" \
    > "$OUTPUT_FILE"

if [ $? -eq 0 ]; then
    echo "Projects listed successfully in $OUTPUT_FILE"
else
    echo "Failed to list projects. Ensure you have the Cloud Asset API enabled and sufficient permissions."
    exit 1
fi

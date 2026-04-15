#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${PROJECT_ID:-$(gcloud config get-value project 2>/dev/null)}"
if [[ -z "${PROJECT_ID}" ]]; then
  echo "Set PROJECT_ID or run 'gcloud config set project <id>' before deploying." >&2
  exit 1
fi
REGION="${REGION:-us-west1}"
SERVICE_NAME="${SERVICE_NAME:-friends-renta}"
REPOSITORY="${REPOSITORY:-personal-images}"

# Ensure Artifact Registry repo exists
if ! gcloud artifacts repositories describe "${REPOSITORY}" \
  --project "${PROJECT_ID}" \
  --location "${REGION}" >/dev/null 2>&1; then
  gcloud artifacts repositories create "${REPOSITORY}" \
    --project "${PROJECT_ID}" \
    --location "${REGION}" \
    --repository-format docker \
    --description "Personal project container images"
fi

IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${SERVICE_NAME}:$(date +%Y%m%d-%H%M%S)"
BUILD_FILE="$(mktemp)"
trap 'rm -f "${BUILD_FILE}"' EXIT

cat >"${BUILD_FILE}" <<EOF
steps:
  - name: gcr.io/cloud-builders/docker
    args:
      - build
      - -f
      - Dockerfile
      - -t
      - \${_IMAGE}
      - .
images:
  - \${_IMAGE}
EOF

echo "Building and pushing image..."
gcloud builds submit \
  --project "${PROJECT_ID}" \
  --config "${BUILD_FILE}" \
  --substitutions "_IMAGE=${IMAGE}" \
  .

# Get session secret from homepage service (shared auth)
SESSION_SECRET=$(gcloud run services describe homepage \
  --project "${PROJECT_ID}" \
  --region "${REGION}" \
  --format='value(spec.template.spec.containers[0].env[0].value)' 2>/dev/null || echo "")
if [[ -z "${SESSION_SECRET}" ]]; then
  echo "WARNING: Could not read SESSION_SECRET from homepage service. Auth may not work." >&2
  SESSION_SECRET="dev-secret-change-me"
fi

echo "Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
  --project "${PROJECT_ID}" \
  --region "${REGION}" \
  --image "${IMAGE}" \
  --allow-unauthenticated \
  --max-instances=2 \
  --set-env-vars="SESSION_SECRET=${SESSION_SECRET}"

SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
  --project "${PROJECT_ID}" \
  --region "${REGION}" \
  --format='value(status.url)')

echo ""
echo "Deployed! Service URL: ${SERVICE_URL}"
echo "Renta available at: ${SERVICE_URL}/friends/renta"

# Register in site manifest
SITE_PATH="/friends/renta"
SITE_LABEL="renta"
SITE_MIN_TIER="friends"
MANIFEST_BUCKET="gs://ethanpease-site-manifest"
echo "Updating site manifest..."
gcloud storage cp "${MANIFEST_BUCKET}/manifest.json" /tmp/manifest.json 2>/dev/null || echo '{"sites":[]}' > /tmp/manifest.json
python3 -c "
import json
m = json.load(open('/tmp/manifest.json'))
entry = {'path': '${SITE_PATH}', 'label': '${SITE_LABEL}', 'min_tier': '${SITE_MIN_TIER}'}
m['sites'] = [s for s in m['sites'] if s['path'] != entry['path']] + [entry]
json.dump(m, open('/tmp/manifest.json', 'w'), indent=2)
"
gcloud storage cp /tmp/manifest.json "${MANIFEST_BUCKET}/manifest.json"
echo "Manifest updated."

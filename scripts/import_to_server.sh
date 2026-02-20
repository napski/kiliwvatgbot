#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  ./scripts/import_to_server.sh <user@host> <remote_path> [--env-file .env]

Examples:
  ./scripts/import_to_server.sh root@203.0.113.10 /opt/kiliwvatgbot
  ./scripts/import_to_server.sh deploy@my-server /srv/kiliwvatgbot --env-file .env.prod

What script does:
  1) Creates remote folder
  2) Uploads project with rsync (excluding .git, venv, caches)
  3) Optionally uploads your local env file to <remote_path>/.env
  4) Prints exact commands to run on server
USAGE
}

if [[ $# -lt 2 ]]; then
  usage
  exit 1
fi

TARGET_HOST="$1"
REMOTE_PATH="$2"
shift 2

ENV_FILE=""
if [[ $# -gt 0 ]]; then
  if [[ "$1" == "--env-file" && $# -eq 2 ]]; then
    ENV_FILE="$2"
  else
    usage
    exit 1
  fi
fi

if [[ -n "$ENV_FILE" && ! -f "$ENV_FILE" ]]; then
  echo "[ERROR] env file not found: $ENV_FILE" >&2
  exit 1
fi

echo "==> [1/4] Create remote directory ${REMOTE_PATH}"
ssh "$TARGET_HOST" "mkdir -p '$REMOTE_PATH'"

echo "==> [2/4] Upload project files"
rsync -az --delete \
  --exclude '.git' \
  --exclude '.venv' \
  --exclude '__pycache__' \
  --exclude '.pytest_cache' \
  ./ "$TARGET_HOST:$REMOTE_PATH/"

if [[ -n "$ENV_FILE" ]]; then
  echo "==> [3/4] Upload env file to $REMOTE_PATH/.env"
  scp "$ENV_FILE" "$TARGET_HOST:$REMOTE_PATH/.env"
else
  echo "==> [3/4] Skip env upload (use .env.example on server)"
fi

echo "==> [4/4] Next commands on server"
cat <<NEXT
ssh $TARGET_HOST
cd $REMOTE_PATH
cp -n .env.example .env
# edit .env: TELEGRAM_BOT_TOKEN and DATABASE_URL
# optional: docker compose pull
sudo docker compose up -d --build
sudo docker compose ps
NEXT

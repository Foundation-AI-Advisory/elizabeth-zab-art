#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "================================================="
echo "Elizabeth Zab Art — Vercel deploy (3 prototypes)"
echo "================================================="
echo ""

# Make sure user is logged into Vercel CLI
if ! npx -y vercel whoami > /dev/null 2>&1; then
  echo "You need to log in to Vercel first. Running 'vercel login'..."
  npx -y vercel login
fi

echo ""
echo "Logged in as: $(npx -y vercel whoami)"
echo ""

URLS_FILE="$PWD/_DEPLOY_URLS.txt"
echo "Vercel deploy results — $(date)" > "$URLS_FILE"
echo "" >> "$URLS_FILE"

for slug in elizabeth-zab-prototype-a elizabeth-zab-prototype-b elizabeth-zab-prototype-c; do
  echo ""
  echo "--- Deploying $slug ---"
  cd "$PWD/$slug" 2>/dev/null || cd "$(dirname "$0")/$slug"
  URL=$(npx -y vercel deploy --prod --yes --name="$slug" 2>&1 | tail -1)
  echo "$slug -> $URL"
  echo "$slug -> $URL" >> "$URLS_FILE"
  cd "$(dirname "$0")"
done

echo ""
echo "================================================="
echo "All three deployed. URLs saved to:"
echo "  $URLS_FILE"
echo "================================================="
echo ""
cat "$URLS_FILE"
echo ""
echo "Press ENTER to close this window..."
read

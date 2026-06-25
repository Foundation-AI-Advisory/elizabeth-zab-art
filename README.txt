ELIZABETH ZAB ART — VERCEL DEPLOY PACKAGE

Three prototypes, each in its own folder, each with vercel.json pinning the project name.

Recommended:
  1. Double-click DEPLOY_ALL.command. Terminal opens.
  2. If prompted, log in to Vercel (one-time). A browser tab opens; sign in normally.
  3. The script deploys all three projects in sequence.
  4. URLs are printed to the terminal AND saved to _DEPLOY_URLS.txt.
  5. Share the 3 URLs back to the assistant for verification.

Manual fallback (if double-click is blocked by Gatekeeper):
  Open Terminal and run:
    cd ~/Downloads/vercel_deploys && bash DEPLOY_ALL.command

If you want to deploy one at a time:
  cd elizabeth-zab-prototype-a && npx vercel deploy --prod --yes --name=elizabeth-zab-prototype-a
  cd ../elizabeth-zab-prototype-b && npx vercel deploy --prod --yes --name=elizabeth-zab-prototype-b
  cd ../elizabeth-zab-prototype-c && npx vercel deploy --prod --yes --name=elizabeth-zab-prototype-c

GlobalTech — GitHub + Cloudflare Pages Ultimate Deploy

WHAT THIS PACKAGE DOES
1. index.html is small and mobile/FB in-app-browser safe.
2. Every catalog model has its own deterministic local path under assets/products/.
3. GitHub Actions automatically downloads the exact-model source image, converts it to 900x900 white-background WebP, and stores it locally.
4. The browser always tries the local image first. If a local file is temporarily missing, it tries that model's exact remote source, then a text-only fallback. It never substitutes a different product model.
5. Cloudflare caches product WebP files at the edge.
6. GA4 G-E76V1Z9TX7, product_click and whatsapp_inquiry remain enabled.

UPLOAD
Upload ALL contents of this folder to the ROOT of your GitHub repo:
  .github/
  assets/
  scripts/
  _headers
  index.html
  README_DEPLOY.txt

FIRST SYNC
After upload, open GitHub -> Actions -> Sync product images.
The workflow normally starts automatically because the workflow file itself was pushed. If it does not, click Run workflow once.
When it finishes it commits the downloaded WebP images back to main. Cloudflare Pages will then auto-deploy the new commit.

CHECK
- GitHub assets/products should grow toward one WebP per product model.
- assets/image-sync-report.json shows which exact source downloaded successfully.
- Cloudflare Pages Deployments should show Success.
- In browser Network, index.html should stay small and images should load from /assets/products/*.webp.

IMPORTANT
Some manufacturer/CDN servers occasionally block automated downloads. The workflow never replaces a good existing local file with a broken file. A blocked model keeps its existing local copy or exact remote fallback. No cross-model image substitution is used.

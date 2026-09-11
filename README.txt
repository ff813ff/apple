GlobalTech Wholesale — GitHub + Cloudflare Pages deployment package

Upload the CONTENTS of this folder to the root of your GitHub repository:

  index.html
  _headers
  assets/products/...

Cloudflare Pages will serve the local product images from its CDN.
The product images extracted from the previous Base64 HTML are now independent WebP assets,
so the browser can cache them and lazy-load them instead of downloading them inside the HTML.

GA4 remains configured with G-E76V1Z9TX7.
Existing product_click and whatsapp_inquiry tracking remains in index.html.

Do not rename or move assets/products unless you also update the paths in index.html.

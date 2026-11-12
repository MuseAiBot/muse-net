# MuseAi-FED-NET promotional site

This folder is a static site. Publish the folder itself as the Pages output directory.

For GitHub Pages, select the `site/` folder as the published artifact in the workflow or copy its contents to the Pages branch. For Cloudflare Pages, use `site` as the build output directory and no build command is required.

Before publishing, replace `url` in `site-config.js` with the final Pages or custom-domain URL. The shared value updates the visible title and URL stamps throughout the HTML.

All navigation targets are HTML documents, including `404.html`; the site does not depend on a server-side router.

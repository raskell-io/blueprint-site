# Template and theme rules

Applies when editing `themes/blueprint/` or `templates/`.

- The theme is meant to live in its own repository. Change it there, then bump the submodule here. Never fork theme
  files into the site's `templates/` to work around something; fix the theme.
- No inline `<script>` and no inline `style=` attributes: the CSP in `static/_headers` blocks both. Scripts are files
  in `static/js/`, loaded with `defer`. If you need a computed value in JS, put it in a `data-` attribute.
- No requests to third parties. Fonts are self-hosted or the system stack.
- Every page must work without JavaScript. Scripts add to a page, they do not build it.
- Accessibility: one `h1` per page, a skip link, visible focus styles, labels on icon-only buttons
  (`aria-label`), and motion only under `prefers-reduced-motion: no-preference`.
- JSON-LD comes from `partials/jsonld.html` and uses the type `data/kinds.toml` assigns to the kind. Keep the
  structured data and the visible page saying the same thing.

# Copilot instructions for Orbit (patch-only workflow)

These instructions guide GitHub Copilot (and contributors) to make safe, reproducible changes in this repo. The Firefox engine code lives under `engine/`. We never edit files in `engine/` directly. All changes to engine files are applied via git patches stored under `src/browser/themes/**`.

## Core rules (must follow)
- Do NOT edit files inside `engine/**` directly.
- Place all modifications as unified-diff patches under `src/browser/themes/**`. Prefer the same subfolder structure as the target (e.g. `shared/newtab/*.patch`, `shared/branding/*.patch`).
- Keep patches minimal: only include the lines changed and a few context lines so they apply across Firefox bumps.
- After adding or editing patches, validate by running: `pnpm imp`. Build/run with `pnpm bs`.

## Patch format checklist (unified diff)
A valid patch must contain, in order:
1) `diff --git a/<path> b/<path>`
2) `--- a/<path>` (no extra spaces, no BOM)
3) `+++ b/<path>`
4) One or more hunks with a header like `@@ -<start>,<len> +<start>,<len> @@ <optional context>`
5) Lines inside each hunk:
   - Context: single leading space
   - Deletions: single leading `-` at column 1
   - Additions: single leading `+` at column 1
   - Never use `++`/`--` for context lines; never indent the `+`/`-` markers
6) Ensure a trailing newline at end of file.

Common errors and how to avoid them:
- "patch with only garbage at line X" → Missing or malformed `diff --git` / `---` / `+++` / `@@` headers, or stray characters before them.
- "corrupt patch at line X" → Incorrect line prefixes (e.g., `++` instead of `+`, or spaces before `+`/`-`), malformed hunk header, or mixed encodings.
- If a patch fails with offset, add/adjust context lines but keep the change minimal.

## Where specific customizations go

### New Tab (Activity Stream) – logo and wallpaper
- Target file: `browser/extensions/newtab/css/activity-stream.css`
- Patches:
  - `src/browser/themes/shared/newtab/activity-stream-css.patch` – use Orbit SVG logo and (optionally) hide wordmark.
  - `src/browser/themes/shared/newtab/default-wallpaper.patch` – set the default `background-image` fallback to our brand wallpaper.
- Required change pattern for wallpaper fallback (minimal hunk):

```
diff --git a/browser/extensions/newtab/css/activity-stream.css b/browser/extensions/newtab/css/activity-stream.css
--- a/browser/extensions/newtab/css/activity-stream.css
+++ b/browser/extensions/newtab/css/activity-stream.css
@@ -<approx line>,6 +<approx line>,6 @@ body {
   background-repeat: no-repeat;
   background-size: cover;
   background-position: center;
   background-attachment: fixed;
-  background-image: var(--newtab-wallpaper, ""), linear-gradient(to right, var(--newtab-wallpaper-color, ""), var(--newtab-wallpaper-color, ""));
+  background-image: var(--newtab-wallpaper, url("chrome://branding/content/orbit-newtab-bg.png")), linear-gradient(to right, var(--newtab-wallpaper-color, transparent), var(--newtab-wallpaper-color, transparent));
}
```

Notes:
- It’s okay if the starting line number changes; keep a few context lines so patch fuzz applies.
- Do not add unrelated CSS.

### Packaging new assets (JAR manifests)
- We never drop files directly into `engine/…` without a corresponding patch.
- To package a wallpaper image in the branding JAR, modify `browser/branding/stable/content/jar.mn` via a patch:

```
diff --git a/browser/branding/stable/content/jar.mn b/browser/branding/stable/content/jar.mn
--- a/browser/branding/stable/content/jar.mn
+++ b/browser/branding/stable/content/jar.mn
@@ -24,1 +24,3 @@
-  content/branding/aboutDialog.css
+  content/branding/aboutDialog.css
+  # Orbit: New Tab default wallpaper
+  content/branding/orbit-newtab-bg.png
```

Place this patch at `src/browser/themes/shared/branding/branding-stable-jar-mn.patch`.

### Adding the actual image
Choose one strategy:
- Preferred: Binary patch that adds `browser/branding/stable/content/orbit-newtab-bg.png` to the source. Generate with `git diff --binary` against a branch that contains the file. Store the result under `src/browser/themes/shared/branding/orbit-newtab-bg.patch`. Then ensure the JAR manifest patch (above) includes the new file path.
- Alternative: Embed image as a data URI in CSS (no asset file). Update the `background-image` fallback accordingly. Use lossless compression; keep lines under ~200 chars where possible or break across lines with proper CSS syntax.

Do NOT commit the image directly under `engine/**` without a corresponding patch.

## Apply/validate workflow
1) Apply patches:
   - `pnpm imp`
2) If import fails:
   - Read the exact patch and fix headers/markers.
   - Ensure added/deleted lines have the correct `+`/`-` prefix at column 1.
   - Ensure there’s at least one `@@` hunk per file.
3) Build/run locally:
   - `pnpm bs` (build + start)
4) Quick verifications:
   - New Tab logo renders from `about-logo.svg`.
   - Wordmark visibility matches our patch (hidden until custom wordmark exists).
   - Background shows fallback wallpaper or user-selected wallpaper.

## Style and scope
- Keep patches focused (one intent per patch when practical) and place them under the most specific folder (`shared/newtab`, `shared/branding`, etc.).
- Update `src/browser/themes/README.md` if you add a new patch so humans know where it applies and how to run it.

## Do/Don’t quick list
- ✅ Do create unified-diff patches under `src/browser/themes/**`.
- ✅ Do run `pnpm imp` to validate patches.
- ✅ Do package new assets by updating the relevant `jar.mn` via a patch.
- ❌ Don’t edit `engine/**` directly.
- ❌ Don’t include stray characters, extra `+`/`-`, or missing hunk headers in patches.

## Troubleshooting examples
- Error: `patch with only garbage at line 4` → Missing `diff --git`/`---`/`+++`/`@@` headers. Recreate the patch as a proper unified diff.
- Error: `corrupt patch at line 30` → A line inside the hunk has `++` or a leading space before `+`/`-`. Ensure each changed line begins with a single `+`/`-` in column 1 and context lines with a single space.

By following this guide, Copilot should propose correct, patch-only changes that import cleanly and survive upstream Firefox updates.

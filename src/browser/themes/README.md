# Orbit Browser Theme Patches

This directory contains patches that customize the Firefox browser to create the Orbit brand identity.

## Structure

The patches are organized by component:

### `/src/browser/themes/shared/`
- **newtab/activity-stream-css.patch** - Updates the new tab page logo to use the SVG logo from branding
- **newtab/default-wallpaper.patch** - Sets a default New Tab background wallpaper via CSS variables
 - **branding/branding-stable-jar-mn.patch** - Packages the default wallpaper image in the branding JAR
- **about/aboutDialog-ftl.patch** - Updates the About dialog description with Orbit's brand message

### `/src/browser/themes/linux/`, `/src/browser/themes/osx/`, `/src/browser/themes/windows/`
- Platform-specific CSS patches for browser chrome styling

## How Patches Work

These patches are applied during the build process to customize Firefox source files without modifying the original engine code. This makes it easier to:

1. **Update Firefox versions** - When you update to a new Firefox version, you only need to verify the patches still apply
2. **Maintain separation** - Keep Orbit-specific changes separate from the Firefox engine
3. **Track changes** - Easily see what was customized for branding

## Branding Changes Made

### New Tab Page Logo
**File**: `engine/browser/extensions/newtab/css/activity-stream.css`

Changed the logo to use the SVG version instead of PNG:
```css
/* Before: */
background: image-set(url("chrome://branding/content/about-logo.png"), url("chrome://branding/content/about-logo@2x.png") 2x) no-repeat center;

/* After: */
background: url("chrome://branding/content/about-logo.svg") no-repeat center;
```

This ensures your logo from `/engine/browser/branding/release/content/about-logo.svg` appears on the new tab page.

### New Tab Default Wallpaper
**File**: `engine/browser/extensions/newtab/css/activity-stream.css`

Adds a default wallpaper using CSS custom properties so it shows up out of the box but still lets users override it with the built‑in Wallpaper feature:

```css
/* Added in default-wallpaper.patch */
:root {
	--newtab-wallpaper: url("chrome://branding/content/orbit-newtab-bg.png");
	--newtab-wallpaper-color: transparent;
}
```

Place your wallpaper image at:
- `/engine/browser/branding/stable/content/orbit-newtab-bg.png`

PNG is recommended (2560×1440 or larger). AVIF/WEBP are also supported if you change the filename in the patch accordingly.

### About Dialog Description
**File**: `engine/browser/locales/en-US/browser/aboutDialog.ftl`

Replaced the generic Firefox description with Orbit's brand message:
```
Orbit is a modern, privacy-focused web browser developed by SafeCircle—the digital 
safety company committed to protecting families and individuals online. Built on 
trusted open-source foundations, Orbit combines the performance of a modern browser 
with SafeCircle's mission of accessible, transparent security.
```

## Applying Patches

Patches are typically applied during the build process. To manually apply a patch:

```bash
cd engine
patch -p1 < ../src/browser/themes/shared/newtab/activity-stream-css.patch
patch -p1 < ../src/browser/themes/shared/newtab/default-wallpaper.patch
patch -p1 < ../src/browser/themes/shared/branding/branding-stable-jar-mn.patch
patch -p1 < ../src/browser/themes/shared/about/aboutDialog-ftl.patch
```

If the wallpaper doesn't appear, verify the image exists at `/engine/browser/branding/stable/content/orbit-newtab-bg.png` and rebuild.

## Updating for New Firefox Versions

When updating to a new Firefox version:

1. Try to apply the patches to see if they still work
2. If a patch fails, manually check the target file
3. Update the patch with the new context lines
4. Test that the branding appears correctly

## Brand Assets Location

The logo files referenced in these patches are located at:
- `/engine/browser/branding/release/content/about-logo.svg`
- `/engine/browser/branding/release/content/about-logo.png`
- `/engine/browser/branding/release/content/about-logo@2x.png`

The wordmark is at:
- `/engine/browser/branding/release/content/firefox-wordmark.svg` (you may want to replace this with your own)

## Additional Branding Files

Other branding is configured in:
- `/engine/browser/branding/release/configure.sh` - Application display name
- `/engine/browser/branding/release/locales/en-US/brand.ftl` - Brand strings
- `/engine/browser/branding/release/locales/en-US/brand.properties` - Brand properties

# static/style.css — Stylesheet
This file controls the visual appearance of the whole site. I used a **nature/green theme** to fit the "animal detection on rural roads" concept of the project. The site uses Bootstrap 5 as a base, and this stylesheet overrides Bootstrap's defaults to apply the custom colour scheme.
---
## CSS Variables (Custom Properties)
At the top of the file I defined a set of colour variables using `:root`:
```css
:root {
  --env-bg:         #f2f8f2;   /* light green-white page background */
  --env-surface:    #ffffff;   /* card/panel background */
  --env-border:     #c3e0c3;   /* soft green border colour */
  --env-green:      #2e7d32;   /* primary dark green */
  --env-green-mid:  #4caf50;   /* medium green for accents */
  --env-green-soft: #a5d6a7;   /* light green for subtle highlights */
  --env-green-pale: #e8f5e9;   /* very pale green for backgrounds */
  --env-text:       #1b2e1c;   /* near-black dark green for text */
  --env-muted:      #5a7a5b;   /* muted green-grey for secondary text */
  ...
}
```
Using variables makes it easy to change the whole theme in one place — I just update the variable values instead of hunting through the whole file.
---
## Fonts
```css
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=DM+Sans:wght@400;500;600&display=swap');
```
Two fonts are imported from Google Fonts:
- **Nunito** — used for headings (`h1`–`h6`) and the navbar brand. It's rounded and friendly.
- **DM Sans** — used for body text. Clean and modern but easy to read.
---
## Body Background
```css
body {
  background-color: var(--env-bg);
  background-image:
    radial-gradient(ellipse at 10% 0%, rgba(165,214,167,0.25) ...),
    radial-gradient(ellipse at 90% 100%, rgba(200,230,201,0.2) ...);
}
```
The body has a subtle gradient overlay — two soft green ellipses in the top-left and bottom-right corners. It's barely visible but adds a bit of depth to the background.
---
## Navbar (`.csi-navbar`)
The navbar has a dark green horizontal gradient:
```css
background: linear-gradient(90deg, #1b5e20 0%, #2e7d32 60%, #388e3c 100%);
```
Nav links are white at 85% opacity normally, and go to bright mint green (`#b9f6ca`) on hover or when active. The active link also gets a green underline.
---
## Cards (`.csi-card`)
The main card style used throughout the app. White background with a soft green border and a very subtle box shadow. On hover the shadow gets slightly stronger to give a slight lift effect.
```css
.csi-card {
  border-radius: 14px;
  box-shadow: 0 2px 12px rgba(46,125,50,0.07);
  transition: box-shadow 0.2s;
}
```
---
## Stat Cards (`.stat-card`)
Used on the dashboard for the 4 top summary numbers. Has a left colour border and a faint diagonal gradient from white to pale green.
---
## Role Badges
Each user role gets its own badge colour:
- `admin` → dark green (`#2e7d32`)
- `operator` → olive green (`#558b2f`)
- `viewer` → blue-grey (`#78909c`)
---
## Tables
Bootstrap's dark table classes are overridden to use a light green-white colour scheme instead of an actual dark theme:
```css
.table-dark {
  --bs-table-bg: #ffffff;
  --bs-table-hover-bg: #e8f5e9;
  --bs-table-border-color: var(--env-border);
}
```
The table headers (`.table-secondary`) are pale green with uppercase bold text. Alert rows (`.table-danger`) are a soft pink-red to stand out.
---
## Alerts
Bootstrap's alert colours are all overridden to fit the green theme. For example, success alerts are pale green instead of Bootstrap's default green, and info alerts use a sky-blue tone.
---
## Confidence Colours (Upload Page)
Defined inline in `upload.html`'s `<style>` block rather than here, but they follow the same pattern:
- `conf-high` (≥80%) → bright green
- `conf-med` (≥60%) → yellow
- `conf-low` (<60%) → red
---
## Pulse Animation
```css
.pulse { animation: pulse 1.5s infinite; }
@keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:.35;} }
```
Used on the "LIVE" badge on the dashboard to make it fade in and out, indicting the feed is active and updating.
---
## Scrollbar
The custom scrollbar styles target WebKit browsers (Chrome, Edge, Safari). Te thumb uses the soft green colour to match the rest of the theme.
---
## Overrides for Bootstrap Dark Classes
A few Bootstrap utility classes that normally make things dark (like `.table-dark`, `.bg-dark`, `.bg-black`) are overridden to use light surfaces instead, since the whole site theme is light-mode green rather than dark mode
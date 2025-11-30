# Adding Your Company Logo

## Quick Setup

1. **Place your logo file in this directory** (`server/static/`)
   - Supported formats: PNG, JPG, SVG
   - Recommended size: 180x100 pixels or similar aspect ratio
   - Example: Save as `logo.png`

2. **Update kiosk.html** to use your logo:

   Open `kiosk.html` and find this section (around line 157):

   ```html
   <!-- Logo -->
   <div id="logo-section">
       <div class="logo-placeholder">
           TRAMPOLINE<br>PARK
       </div>
   </div>
   ```

   Replace it with:

   ```html
   <!-- Logo -->
   <div id="logo-section">
       <img id="logo" src="/static/logo.png" alt="Company Logo">
   </div>
   ```

3. **Restart the server** or refresh the kiosk display

## Alternative: Use Base64 Embedded Logo

If you prefer to embed the logo directly in the HTML (no separate file):

1. Convert your logo to base64:
   ```bash
   base64 -i logo.png
   ```

2. Replace the logo section with:
   ```html
   <div id="logo-section">
       <img id="logo" src="data:image/png;base64,YOUR_BASE64_STRING_HERE" alt="Company Logo">
   </div>
   ```

## Styling the Logo

The logo styling is defined in the CSS section:

```css
#logo {
    max-width: 180px;
    max-height: 100px;
    object-fit: contain;
}
```

Adjust these values to resize your logo as needed.

## Placeholder

The current placeholder uses your company colors:
- Red: #ff1152
- Green: #26f434
- Lime: #caff1a

This will display until you add your actual logo.

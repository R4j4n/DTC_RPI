# Multi-Location Configuration Guide

This guide explains how to add and manage multiple locations in your Next.js application.

## 🚀 Quick Start: Adding a New Location

### Option 1: Automated (Recommended)

1. **Edit the `.env` file** and add your new location:

```bash
# Add the location ID to the list
NEXT_PUBLIC_LOCATIONS=Oakville,London,Toronto

# Add the location configuration
NEXT_PUBLIC_LOCATION_Toronto_NAME=Toronto Downtown
NEXT_PUBLIC_LOCATION_Toronto_HOST=http://192.168.3.100:7777
```

2. **Run the generator script**:

```bash
npm run generate-locations
```

3. **Restart the dev server** (if running):

```bash
# Press Ctrl+C to stop, then:
npm run dev
```

That's it! Your new location will automatically appear in the LocationSelector. ✨

---

### Option 2: Manual

If you prefer to do it manually:

1. **Edit `.env`** (same as above)

2. **Edit `src/lib/locationConfig.js`** and add to the `envVars` object:

```javascript
const envVars = {
  // ... existing locations ...
  NEXT_PUBLIC_LOCATION_Toronto_NAME: process.env.NEXT_PUBLIC_LOCATION_Toronto_NAME,
  NEXT_PUBLIC_LOCATION_Toronto_HOST: process.env.NEXT_PUBLIC_LOCATION_Toronto_HOST,
};
```

3. **Restart the dev server**

---

## 📝 Environment Variable Format

Each location requires **two environment variables**:

```bash
NEXT_PUBLIC_LOCATION_{ID}_NAME={Display Name}
NEXT_PUBLIC_LOCATION_{ID}_HOST={Server URL}
```

**Rules:**
- `{ID}` must be alphanumeric (no spaces or special characters except underscore)
- `{ID}` must match exactly in the `NEXT_PUBLIC_LOCATIONS` list
- `{Display Name}` can contain spaces and special characters
- `{Server URL}` **must** start with `http://` or `https://`

**Example:**

```bash
# ✅ Good
NEXT_PUBLIC_LOCATIONS=Oakville,NewYork,LA_Office
NEXT_PUBLIC_LOCATION_Oakville_NAME=Oakville Branch
NEXT_PUBLIC_LOCATION_Oakville_HOST=http://192.168.1.100:7777
NEXT_PUBLIC_LOCATION_NewYork_NAME=New York HQ
NEXT_PUBLIC_LOCATION_NewYork_HOST=https://ny.example.com:7777
NEXT_PUBLIC_LOCATION_LA_Office_NAME=Los Angeles Office
NEXT_PUBLIC_LOCATION_LA_Office_HOST=http://192.168.3.50:7777

# ❌ Bad
NEXT_PUBLIC_LOCATIONS=New York  # Space in ID - won't work!
NEXT_PUBLIC_LOCATION_NY_HOST=192.168.1.100  # Missing http:// - will fail validation!
```

---

## 🤖 Automation Details

### What the Script Does

The `npm run generate-locations` script:

1. Reads your `.env` file
2. Finds all `NEXT_PUBLIC_LOCATION_*` variables
3. Auto-generates the `envVars` object in `src/lib/locationConfig.js`
4. Replaces the section marked with `🤖 AUTO-GENERATED`

### When to Run the Script

**Automatically runs:**
- During production build (`npm run build`)

**Manually run when:**
- You add a new location to `.env`
- You rename a location ID in `.env`
- You remove a location from `.env`

**Command:**
```bash
npm run generate-locations
```

### Auto-Generated Section

**Do not edit this section manually** in `locationConfig.js`:

```javascript
// 🤖 AUTO-GENERATED - DO NOT EDIT THIS SECTION MANUALLY
// Run 'npm run generate-locations' to regenerate
const envVars = {
  // ... generated code ...
};
// 🤖 END AUTO-GENERATED SECTION
```

Any manual changes between these markers will be **overwritten** when the script runs.

---

## 🔍 Troubleshooting

### Location Not Appearing

**Symptoms:** Added location to `.env` but it doesn't show up in LocationSelector

**Solutions:**

1. **Run the generator:**
   ```bash
   npm run generate-locations
   ```

2. **Restart the dev server:**
   ```bash
   # Press Ctrl+C
   npm run dev
   ```

3. **Clear browser cache:**
   - In browser console: `sessionStorage.clear()`
   - Hard refresh: Ctrl+Shift+R (or Cmd+Shift+R on Mac)

4. **Check console logs** for validation errors:
   - Open browser DevTools (F12)
   - Look for `Location {ID} missing NAME` or similar warnings

### Validation Errors

If you see: `Location XYZ missing NAME - skipping`

**Check:**
- ID in `NEXT_PUBLIC_LOCATIONS` matches exactly (case-sensitive)
- Both `_NAME` and `_HOST` variables are defined
- No typos in variable names
- `.env` file saved and server restarted

### Location Shows "Offline"

**This is normal!** The health check runs when LocationSelector loads.

**Possible reasons:**
- Server actually offline (expected behavior)
- Network timeout (server slow to respond)
- Firewall blocking connection
- Incorrect URL in `_HOST`

**You can still select offline locations** - the system will try to connect when you authenticate.

---

## 📊 Example Configurations

### Two Locations (Simple)

```bash
NEXT_PUBLIC_LOCATIONS=Main,Backup
NEXT_PUBLIC_LOCATION_Main_NAME=Main Office
NEXT_PUBLIC_LOCATION_Main_HOST=http://192.168.1.100:7777
NEXT_PUBLIC_LOCATION_Backup_NAME=Backup Server
NEXT_PUBLIC_LOCATION_Backup_HOST=http://192.168.1.200:7777
```

### Five Locations (Complex)

```bash
NEXT_PUBLIC_LOCATIONS=HQ,Store1,Store2,Store3,Remote

NEXT_PUBLIC_LOCATION_HQ_NAME=Headquarters - Toronto
NEXT_PUBLIC_LOCATION_HQ_HOST=http://192.168.1.10:7777

NEXT_PUBLIC_LOCATION_Store1_NAME=Store #1 - Oakville
NEXT_PUBLIC_LOCATION_Store1_HOST=http://192.168.2.10:7777

NEXT_PUBLIC_LOCATION_Store2_NAME=Store #2 - London
NEXT_PUBLIC_LOCATION_Store2_HOST=http://192.168.3.10:7777

NEXT_PUBLIC_LOCATION_Store3_NAME=Store #3 - Hamilton
NEXT_PUBLIC_LOCATION_Store3_HOST=http://192.168.4.10:7777

NEXT_PUBLIC_LOCATION_Remote_NAME=Remote Access (zrok)
NEXT_PUBLIC_LOCATION_Remote_HOST=https://abc123.share.zrok.io
```

### Using Cloud Tunnels (zrok, ngrok, etc.)

```bash
NEXT_PUBLIC_LOCATIONS=Local,Cloud

NEXT_PUBLIC_LOCATION_Local_NAME=Local Network
NEXT_PUBLIC_LOCATION_Local_HOST=http://192.168.1.100:7777

NEXT_PUBLIC_LOCATION_Cloud_NAME=Remote Access (Cloud)
NEXT_PUBLIC_LOCATION_Cloud_HOST=https://abc123xyz.share.zrok.io
```

---

## 🛠️ Advanced: Script Location

The generator script is located at:
```
frontend/scripts/generate-location-config.js
```

**Script Features:**
- ✅ Reads `.env` automatically
- ✅ Validates marker presence
- ✅ Alphabetically sorts variables
- ✅ Provides detailed error messages
- ✅ Shows configured location IDs

**Modifying the script:**
If you need to customize the generation logic, edit this file. The script is well-commented.

---

## 📚 Architecture Notes

### Why Manual envVars Mapping?

Next.js performs **static analysis** at build time and replaces `process.env.VARIABLE_NAME` with actual values. This means:

❌ **Doesn't work:**
```javascript
const key = 'NEXT_PUBLIC_LOCATION_' + locationId + '_NAME';
const value = process.env[key];  // Returns undefined!
```

✅ **Works:**
```javascript
const value = process.env.NEXT_PUBLIC_LOCATION_Oakville_NAME;  // Works!
```

That's why we need to explicitly reference each variable in the `envVars` object.

### Why Auto-Generate?

Without automation, you'd need to:
1. Edit `.env`
2. Edit `locationConfig.js` manually
3. Add two lines per location
4. Keep both files in sync

With automation:
1. Edit `.env`
2. Run `npm run generate-locations`
3. Done! ✨

---

## 🎯 Production Deployment

### Building for Production

The generator runs automatically during build:

```bash
npm run build
```

This ensures your production build always has the latest location configuration.

### Environment Variables in Production

Make sure your production environment has all `NEXT_PUBLIC_LOCATION_*` variables set:

- Vercel: Add to Project Settings → Environment Variables
- Docker: Include in `.env` file or pass via `-e` flags
- PM2: Use `ecosystem.config.js` or `.env` file
- Other platforms: Follow their environment variable setup

---

## 💡 Tips

1. **Use descriptive location names** - "Toronto Downtown Store" is better than "Store1"

2. **Keep IDs simple** - Use short, alphanumeric IDs like `Toronto`, `NYC`, `LA`

3. **Document your locations** - Add comments in `.env`:
   ```bash
   # Store #1 - Opened Jan 2024
   NEXT_PUBLIC_LOCATION_Store1_NAME=Oakville Branch
   ```

4. **Test health checks** - Ensure URLs are accessible before deploying

5. **Backup `.env`** - Keep a backup before making changes

---

## 📞 Need Help?

If you encounter issues:

1. Check the browser console for errors (F12)
2. Check server logs for backend issues
3. Verify `.env` syntax (no spaces around `=`)
4. Ensure server restarted after changes
5. Run `npm run generate-locations` manually

---

**Last Updated:** December 2024

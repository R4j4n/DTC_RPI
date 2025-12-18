// lib/locationConfig.js
// Location configuration parser for multi-location support

/**
 * Validates a location configuration
 * @param {string} id - Location ID
 * @param {string} name - Display name
 * @param {string} host - Server URL
 * @returns {boolean} - True if valid
 */
function validateLocationConfig(id, name, host) {
  if (!name || name.trim() === '') {
    console.warn(`Location ${id} missing NAME - skipping`);
    return false;
  }

  if (!host || host.trim() === '') {
    console.warn(`Location ${id} missing HOST - skipping`);
    return false;
  }

  if (!host.startsWith('http://') && !host.startsWith('https://')) {
    console.warn(`Location ${id} HOST must start with http:// or https:// - skipping`);
    return false;
  }

  return true;
}

/**
 * Parses environment variables to build location objects
 * @returns {Array} - Array of location objects
 */
export function parseLocations() {
  const locationsStr = process.env.NEXT_PUBLIC_LOCATIONS;

  console.log('locationConfig: NEXT_PUBLIC_LOCATIONS =', locationsStr);

  // No locations configured - fallback to legacy mode
  if (!locationsStr || locationsStr.trim() === '') {
    const legacyHost = process.env.NEXT_PUBLIC_ACTIVE_SERVER_HOSTNAME;

    if (!legacyHost) {
      console.error('No locations configured and no legacy NEXT_PUBLIC_ACTIVE_SERVER_HOSTNAME found');
      return [];
    }

    console.warn('⚠️ NEXT_PUBLIC_LOCATIONS not found - using legacy single-server mode');
    console.warn('⚠️ Make sure to restart the dev server after changing .env file!');
    return [{
      id: 'default',
      name: 'Main Server',
      host: legacyHost
    }];
  }

  // Parse location IDs
  const locationIds = locationsStr.split(',').map(id => id.trim()).filter(id => id !== '');

  if (locationIds.length === 0) {
    console.warn('NEXT_PUBLIC_LOCATIONS is empty - falling back to legacy mode');
    const legacyHost = process.env.NEXT_PUBLIC_ACTIVE_SERVER_HOSTNAME;
    return legacyHost ? [{
      id: 'default',
      name: 'Main Server',
      host: legacyHost
    }] : [];
  }

  // Build a map of all NEXT_PUBLIC_LOCATION_* env vars
  // Next.js doesn't support dynamic env var access (process.env[key])
  // So we need to explicitly reference each possible env var
  // 🤖 AUTO-GENERATED - DO NOT EDIT THIS SECTION MANUALLY
  // Run 'npm run generate-locations' to regenerate
  const envVars = {
    NEXT_PUBLIC_LOCATION_London_HOST: process.env.NEXT_PUBLIC_LOCATION_London_HOST,
    NEXT_PUBLIC_LOCATION_London_NAME: process.env.NEXT_PUBLIC_LOCATION_London_NAME,
    NEXT_PUBLIC_LOCATION_Oakville_HOST: process.env.NEXT_PUBLIC_LOCATION_Oakville_HOST,
    NEXT_PUBLIC_LOCATION_Oakville_NAME: process.env.NEXT_PUBLIC_LOCATION_Oakville_NAME,
    NEXT_PUBLIC_LOCATION_Scarborough_HOST: process.env.NEXT_PUBLIC_LOCATION_Scarborough_HOST,
    NEXT_PUBLIC_LOCATION_Scarborough_NAME: process.env.NEXT_PUBLIC_LOCATION_Scarborough_NAME,
  };
  // 🤖 END AUTO-GENERATED SECTION

  // Build location objects from environment variables
  const locations = [];

  for (const id of locationIds) {
    const nameKey = `NEXT_PUBLIC_LOCATION_${id}_NAME`;
    const hostKey = `NEXT_PUBLIC_LOCATION_${id}_HOST`;

    const name = envVars[nameKey];
    const host = envVars[hostKey];

    console.log(`locationConfig: Checking ${id} - name=${name}, host=${host}`);

    // Validate configuration
    if (validateLocationConfig(id, name, host)) {
      locations.push({
        id,
        name,
        host
      });
    }
  }

  if (locations.length === 0) {
    console.warn('No valid locations found - falling back to legacy mode');
    const legacyHost = process.env.NEXT_PUBLIC_ACTIVE_SERVER_HOSTNAME;
    return legacyHost ? [{
      id: 'default',
      name: 'Main Server',
      host: legacyHost
    }] : [];
  }

  console.log(`Loaded ${locations.length} location(s):`, locations.map(l => l.name).join(', '));
  return locations;
}

// Cache parsed locations to avoid re-parsing on every call
let cachedLocations = null;

/**
 * Gets all configured locations (cached)
 * @returns {Array} - Array of location objects
 */
export function getAllLocations() {
  if (!cachedLocations) {
    cachedLocations = parseLocations();
  }
  return cachedLocations;
}

/**
 * Gets a specific location by ID
 * @param {string} id - Location ID
 * @returns {Object|null} - Location object or null if not found
 */
export function getLocationById(id) {
  const locations = getAllLocations();
  return locations.find(loc => loc.id === id) || null;
}

/**
 * Clears the location cache (useful for testing or dynamic config updates)
 */
export function clearLocationCache() {
  cachedLocations = null;
}

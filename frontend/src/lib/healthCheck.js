// lib/healthCheck.js
// Health check utilities for location servers

/**
 * Checks if a single location server is reachable
 * @param {Object} location - Location object with host property
 * @returns {Promise<string>} - Status: 'online', 'offline', or 'error'
 */
export async function checkLocationHealth(location) {
  try {
    // Create AbortController for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout

    // Try to fetch from the /pis endpoint (lightweight check)
    const response = await fetch(`${location.host}/pis`, {
      signal: controller.signal,
      method: 'GET',
      headers: {
        'skip_zrok_interstitial': '1'
      }
    });

    clearTimeout(timeoutId);

    // Check response status
    if (response.ok) {
      return 'online';
    } else {
      console.warn(`Location ${location.name} returned non-OK status:`, response.status);
      return 'error';
    }
  } catch (error) {
    // Handle abort (timeout) or network errors
    if (error.name === 'AbortError') {
      console.warn(`Location ${location.name} health check timed out`);
      return 'offline';
    }

    console.warn(`Location ${location.name} health check failed:`, error.message);
    return 'offline';
  }
}

/**
 * Checks health of all locations in parallel
 * @param {Array} locations - Array of location objects
 * @returns {Promise<Array>} - Array of locations with healthStatus property
 */
export async function checkAllLocations(locations) {
  // Run all health checks in parallel
  const healthChecks = locations.map(async (location) => {
    const status = await checkLocationHealth(location);
    return {
      ...location,
      healthStatus: status
    };
  });

  // Wait for all checks to complete (even if some fail)
  const results = await Promise.allSettled(healthChecks);

  // Extract values from settled promises
  return results.map((result, index) => {
    if (result.status === 'fulfilled') {
      return result.value;
    } else {
      // If the health check itself threw an error
      console.error(`Failed to check location ${locations[index].name}:`, result.reason);
      return {
        ...locations[index],
        healthStatus: 'error'
      };
    }
  });
}

/**
 * Continuous health monitor that updates location statuses periodically
 * @param {Array} locations - Array of location objects
 * @param {Function} onUpdate - Callback function called with updated locations
 * @param {number} interval - Update interval in milliseconds (default: 30000 = 30 seconds)
 * @returns {Function} - Cleanup function to stop monitoring
 */
export function startHealthMonitor(locations, onUpdate, interval = 30000) {
  let isActive = true;

  const runCheck = async () => {
    if (!isActive) return;

    const updatedLocations = await checkAllLocations(locations);
    if (isActive) {
      onUpdate(updatedLocations);
    }
  };

  // Run initial check immediately
  runCheck();

  // Set up periodic checks
  const intervalId = setInterval(runCheck, interval);

  // Return cleanup function
  return () => {
    isActive = false;
    clearInterval(intervalId);
  };
}

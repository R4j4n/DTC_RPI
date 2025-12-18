// contexts/LocationContext.jsx
"use client";

import { createContext, useState, useEffect } from 'react';
import { getAllLocations } from '@/lib/locationConfig';

// Create the Location Context
export const LocationContext = createContext(null);

/**
 * LocationProvider component
 * Provides location state to all child components
 */
export function LocationProvider({ children }) {
  const [currentLocation, setCurrentLocation] = useState(null);
  const [allLocations, setAllLocations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Load all locations on mount
  useEffect(() => {
    console.log('LocationProvider: Loading locations...');
    const locations = getAllLocations();
    console.log('LocationProvider: Loaded locations:', locations);
    setAllLocations(locations);
    setIsLoading(false);

    // Auto-select if only one location
    if (locations.length === 1) {
      console.log('Only one location found, auto-selecting:', locations[0].name);
      setCurrentLocation(locations[0]);
    }
  }, []);

  /**
   * Set the current location
   * @param {Object} location - Location object to set as current
   */
  const setLocation = (location) => {
    console.log('Setting current location to:', location?.name);
    setCurrentLocation(location);
  };

  /**
   * Clear the current location
   */
  const clearLocation = () => {
    console.log('Clearing current location');
    setCurrentLocation(null);
  };

  const value = {
    currentLocation,
    allLocations,
    setLocation,
    clearLocation,
    isLoading
  };

  return (
    <LocationContext.Provider value={value}>
      {children}
    </LocationContext.Provider>
  );
}

// hooks/useLocation.js
"use client";

import { useContext } from 'react';
import { LocationContext } from '@/contexts/LocationContext';

/**
 * Custom hook to access the LocationContext
 * Must be used within a LocationProvider
 * @returns {Object} - Location context value
 * @throws {Error} - If used outside LocationProvider
 */
export function useLocation() {
  const context = useContext(LocationContext);

  if (!context) {
    throw new Error('useLocation must be used within a LocationProvider');
  }

  return context;
}

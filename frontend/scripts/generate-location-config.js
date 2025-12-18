#!/usr/bin/env node
/**
 * Auto-generates the location configuration code for locationConfig.js
 * This script reads the .env file and generates the envVars object
 * so you don't have to manually update locationConfig.js when adding new locations.
 *
 * Run: node scripts/generate-location-config.js
 */

const fs = require('fs');
const path = require('path');

// Read .env file
const envPath = path.join(__dirname, '../.env');
const locationConfigPath = path.join(__dirname, '../src/lib/locationConfig.js');

console.log('🔧 Generating location configuration...');

// Read and parse .env file
let envContent;
try {
  envContent = fs.readFileSync(envPath, 'utf8');
} catch (error) {
  console.error('❌ Error: Could not read .env file');
  process.exit(1);
}

// Extract all NEXT_PUBLIC_LOCATION_* variables
const locationVarRegex = /^NEXT_PUBLIC_LOCATION_(\w+)_(NAME|HOST)=(.+)$/gm;
const matches = [...envContent.matchAll(locationVarRegex)];

if (matches.length === 0) {
  console.log('⚠️  No NEXT_PUBLIC_LOCATION_* variables found in .env');
  console.log('   Using legacy single-server mode');
  process.exit(0);
}

// Build a map of location IDs and their variables
const locationVars = new Map();

matches.forEach(match => {
  const [, locationId, varType, value] = match;
  const fullVarName = `NEXT_PUBLIC_LOCATION_${locationId}_${varType}`;
  locationVars.set(fullVarName, true);
});

// Generate the envVars object code
const envVarsLines = Array.from(locationVars.keys())
  .sort()
  .map(varName => `    ${varName}: process.env.${varName},`);

const envVarsCode = `  // Build a map of all NEXT_PUBLIC_LOCATION_* env vars
  // Next.js doesn't support dynamic env var access (process.env[key])
  // So we need to explicitly reference each possible env var
  // 🤖 AUTO-GENERATED - DO NOT EDIT THIS SECTION MANUALLY
  // Run 'npm run generate-locations' to regenerate
  const envVars = {
${envVarsLines.join('\n')}
  };
  // 🤖 END AUTO-GENERATED SECTION`;

// Read current locationConfig.js
let configContent;
try {
  configContent = fs.readFileSync(locationConfigPath, 'utf8');
} catch (error) {
  console.error('❌ Error: Could not read locationConfig.js');
  process.exit(1);
}

// Replace the envVars section
const startMarker = '  // Build a map of all NEXT_PUBLIC_LOCATION_* env vars';
const endMarker = '  // 🤖 END AUTO-GENERATED SECTION';

const startIndex = configContent.indexOf(startMarker);
const endIndex = configContent.indexOf(endMarker);

if (startIndex === -1 || endIndex === -1) {
  console.error('❌ Error: Could not find auto-generation markers in locationConfig.js');
  console.error('   Make sure the file has the correct markers');
  process.exit(1);
}

// Replace the section
const beforeSection = configContent.substring(0, startIndex);
const afterSection = configContent.substring(endIndex + endMarker.length);
const newContent = beforeSection + envVarsCode + afterSection;

// Write back to file
try {
  fs.writeFileSync(locationConfigPath, newContent, 'utf8');
  console.log('✅ Successfully generated location configuration!');
  console.log(`   Found ${locationVars.size} location variables`);

  // Extract unique location IDs
  const locationIds = new Set();
  Array.from(locationVars.keys()).forEach(varName => {
    const match = varName.match(/NEXT_PUBLIC_LOCATION_(\w+)_(NAME|HOST)/);
    if (match) {
      locationIds.add(match[1]);
    }
  });

  console.log(`   Configured locations: ${Array.from(locationIds).join(', ')}`);
} catch (error) {
  console.error('❌ Error: Could not write to locationConfig.js');
  console.error(error);
  process.exit(1);
}

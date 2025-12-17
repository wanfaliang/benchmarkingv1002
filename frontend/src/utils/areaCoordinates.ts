/**
 * Mapping of BLS area codes to geographic coordinates (latitude, longitude)
 * Used for displaying metro areas on the map
 */

export interface Coordinates {
  lat: number;
  lng: number;
}

export const areaCoordinates: Record<string, Coordinates> = {
  // National
  '0000': { lat: 39.8283, lng: -98.5795 }, // U.S. city average (geographic center of US)

  // Northeast
  'S12A': { lat: 40.7128, lng: -74.0060 }, // New York-Newark-Jersey City, NY-NJ-PA
  'S12B': { lat: 39.9526, lng: -75.1652 }, // Philadelphia-Camden-Wilmington, PA-NJ-DE-MD
  'S11A': { lat: 42.3601, lng: -71.0589 }, // Boston-Cambridge-Newton, MA-NH
  'A104': { lat: 40.4406, lng: -79.9959 }, // Pittsburgh, PA

  // Midwest
  'S23A': { lat: 41.8781, lng: -87.6298 }, // Chicago-Naperville-Elgin, IL-IN-WI
  'S23B': { lat: 42.3314, lng: -83.0458 }, // Detroit-Warren-Dearborn, MI
  'S24A': { lat: 44.9778, lng: -93.2650 }, // Minneapolis-St.Paul-Bloomington, MN-WI
  'S24B': { lat: 38.6270, lng: -90.1994 }, // St. Louis, MO-IL
  'A210': { lat: 41.4993, lng: -81.6944 }, // Cleveland-Akron, OH
  'A212': { lat: 43.0389, lng: -87.9065 }, // Milwaukee-Racine, WI
  'A213': { lat: 39.1031, lng: -84.5120 }, // Cincinnati-Hamilton, OH-KY-IN
  'A214': { lat: 39.0997, lng: -94.5786 }, // Kansas City, MO-KS

  // South
  'S35C': { lat: 33.7490, lng: -84.3880 }, // Atlanta-Sandy Springs-Roswell, GA
  'S37A': { lat: 32.7767, lng: -96.7970 }, // Dallas-Fort Worth-Arlington, TX
  'S37B': { lat: 29.7604, lng: -95.3698 }, // Houston-The Woodlands-Sugar Land, TX
  'S35B': { lat: 25.7617, lng: -80.1918 }, // Miami-Fort Lauderdale-West Palm Beach, FL
  'S35D': { lat: 27.9506, lng: -82.4572 }, // Tampa-St. Petersburg-Clearwater, FL
  'S35A': { lat: 38.9072, lng: -77.0369 }, // Washington-Arlington-Alexandria, DC-VA-MD-WV
  'S35E': { lat: 39.2904, lng: -76.6122 }, // Baltimore-Columbia-Towson, MD
  'A311': { lat: 38.9072, lng: -77.0369 }, // Washington-Baltimore, DC-MD-VA-WV (use DC coords)

  // West
  'S49G': { lat: 61.2181, lng: -149.9003 }, // Urban Alaska (Anchorage)
  'S48B': { lat: 39.7392, lng: -104.9903 }, // Denver-Aurora-Lakewood, CO
  'S49F': { lat: 21.3099, lng: -157.8581 }, // Urban Hawaii (Honolulu)
  'S49A': { lat: 34.0522, lng: -118.2437 }, // Los Angeles-Long Beach-Anaheim, CA
  'S49C': { lat: 33.9533, lng: -117.3962 }, // Riverside-San Bernardino-Ontario, CA
  'S48A': { lat: 33.4484, lng: -112.0740 }, // Phoenix-Mesa-Scottsdale, AZ
  'S49E': { lat: 32.7157, lng: -117.1611 }, // San Diego-Carlsbad, CA
  'S49B': { lat: 37.7749, lng: -122.4194 }, // San Francisco-Oakland-Hayward, CA
  'S49D': { lat: 47.6062, lng: -122.3321 }, // Seattle-Tacoma-Bellevue WA
  'A421': { lat: 34.0522, lng: -118.2437 }, // Los Angeles-Riverside-Orange County, CA (use LA coords)
  'A425': { lat: 45.5152, lng: -122.6784 }, // Portland-Salem, OR-WA

  // Regional aggregates (use approximate center points)
  '0100': { lat: 41.2033, lng: -77.1945 }, // Northeast
  '0200': { lat: 41.4925, lng: -87.6298 }, // Midwest
  '0300': { lat: 32.3547, lng: -86.2677 }, // South
  '0400': { lat: 40.1500, lng: -111.8624 }, // West

  // Regional subdivisions
  '0110': { lat: 42.5, lng: -71.5 }, // New England
  '0120': { lat: 40.7, lng: -75.5 }, // Middle Atlantic
  '0230': { lat: 41.5, lng: -84.0 }, // East North Central
  '0240': { lat: 44.0, lng: -96.0 }, // West North Central
  '0350': { lat: 33.5, lng: -80.0 }, // South Atlantic
  '0360': { lat: 34.0, lng: -86.5 }, // East South Central
  '0370': { lat: 31.0, lng: -95.0 }, // West South Central
  '0480': { lat: 39.5, lng: -111.0 }, // Mountain
  '0490': { lat: 38.0, lng: -121.0 }, // Pacific

  // Size Class aggregates (approximate US center or regional centers)
  'S000': { lat: 39.0, lng: -98.0 }, // Size Class A (more than 2,500,000)
  'S100': { lat: 41.0, lng: -74.5 }, // Northeast - Size Class A
  'S200': { lat: 41.8, lng: -87.6 }, // Midwest - Size Class A
  'S300': { lat: 33.5, lng: -84.0 }, // South - Size Class A
  'S400': { lat: 37.5, lng: -119.0 }, // West - Size Class A
  'N000': { lat: 38.5, lng: -98.0 }, // Size Class B/C (2,500,000 or less)
  'N100': { lat: 42.5, lng: -73.5 }, // Northeast - Size Class B/C
  'N200': { lat: 43.0, lng: -89.0 }, // Midwest - Size Class B/C
  'N300': { lat: 35.0, lng: -82.0 }, // South - Size Class B/C
  'N400': { lat: 43.0, lng: -116.0 }, // West - Size Class B/C
};

/**
 * Get coordinates for a BLS area code
 */
export function getAreaCoordinates(areaCode: string): Coordinates | null {
  return areaCoordinates[areaCode] || null;
}

/**
 * Get all area codes that have coordinates
 */
export function getAreaCodesWithCoordinates(): string[] {
  return Object.keys(areaCoordinates);
}

// components/Dashboard.jsx
"use client";

import { Suspense, useState, useEffect } from "react";
import { PiGrid } from "./PiGrid";
import { DashboardHeader } from "./DashboardHeader";
import { LocationSelector } from "./LocationSelector";
import { Montserrat } from "next/font/google";
import { auth_login, fetchPis, setCurrentLocationHost } from "@/lib/api";
import { useLocation } from "@/hooks/useLocation";
import Image from "next/image";
import { Lock, Sparkles, ArrowRight } from "lucide-react";

const montserrat = Montserrat({
  subsets: ["latin"],
  weight: ["400", "700"],
});

export default function Dashboard() {
  const { currentLocation, allLocations, isLoading: locationsLoading } = useLocation();
  const [locationSelected, setLocationSelected] = useState(false);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [firstPi, setFirstPi] = useState(null);

  // Debug logging
  useEffect(() => {
    console.log("=== Dashboard State Debug ===");
    console.log("locationsLoading:", locationsLoading);
    console.log("allLocations:", allLocations);
    console.log("allLocations.length:", allLocations?.length);
    console.log("currentLocation:", currentLocation);
    console.log("locationSelected:", locationSelected);
    console.log("selectedLocation:", selectedLocation);
    console.log("isAuthenticated:", isAuthenticated);
    console.log("Should show LocationSelector?", !locationsLoading && !locationSelected && allLocations.length > 1);
  }, [locationsLoading, allLocations, currentLocation, locationSelected, selectedLocation, isAuthenticated]);


  const get_all_pis_list = async (check_index=0) => {
    const all_pis = await fetchPis();
      if ((all_pis.length) >0){
        setFirstPi(all_pis[check_index].host);
      }
  }

  // Handle location selection
  const handleLocationSelect = (location) => {
    console.log("Location selected:", location.name);
    setSelectedLocation(location);
    setLocationSelected(true);
    setCurrentLocationHost(location.host);
  };

  // Handle location switch from header
  const handleLocationSwitch = () => {
    // Clear authentication
    sessionStorage.removeItem("authToken");
    setIsAuthenticated(false);

    // Reset to location selector
    setLocationSelected(false);
    setSelectedLocation(null);
    setCurrentLocationHost(null);
    setPassword("");
    setError("");
  };

  // Check for auto-selection of single location or already selected location
  useEffect(() => {
    console.log("=== Auto-selection check ===");
    console.log("currentLocation:", currentLocation);
    console.log("allLocations.length:", allLocations.length);
    console.log("locationSelected:", locationSelected);

    // If there's only one location and context auto-selected it
    if (currentLocation && allLocations.length === 1 && !locationSelected) {
      console.log("AUTO-SELECTING single location:", currentLocation.name);
      handleLocationSelect(currentLocation);
    }

    // Check existing auth token
    try{
      const token = sessionStorage.getItem("authToken");
      console.log("Auth token exists:", !!token);
      if (token && locationSelected) {
        console.log("Auto-authenticating with existing token");
        setIsAuthenticated(true);
      }
    } catch(e){
      console.error("Error checking auth token:", e);
    }
  }, [currentLocation, allLocations, locationSelected]);

  // Fetch Pi list when location is selected
  useEffect(() => {
    if (locationSelected && selectedLocation) {
      get_all_pis_list().catch(e => {
        console.error("Error loading initial Pi list:", e);
      });
    }
  }, [locationSelected, selectedLocation]);

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    try {
      const login_response = await auth_login(firstPi, password);
      if (login_response.ok) {
        const data = await login_response.json();
        sessionStorage.setItem("authToken", data.token);
        setIsAuthenticated(true);
      } else {
        const errorData = await login_response.json().catch(() => ({}));
        setError(errorData.message || "Login failed. Please try again.");
      }
    } catch (err) {
      setError("An error occurred. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handlePasswordChange = (e) => {
    setPassword(e.target.value);
  };

  return (
    <div className="w-full h-[100vh] text-center">
      {/* Loading locations */}
      {locationsLoading ? (
        <div className="relative h-full w-full flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 overflow-hidden">
          <div className="absolute inset-0 overflow-hidden">
            <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-purple-500/10 rounded-full blur-3xl animate-pulse"></div>
            <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-blue-500/10 rounded-full blur-3xl animate-pulse"></div>
          </div>

          <div className="relative backdrop-blur-xl bg-slate-800/50 border border-slate-700/50 rounded-2xl p-12 shadow-2xl shadow-purple-500/20">
            <div className="relative">
              <div className="animate-spin rounded-full h-16 w-16 border-4 border-purple-500/30 border-t-purple-500 mx-auto mb-6"></div>
              <div className="absolute inset-0 bg-purple-500/20 rounded-full blur-xl animate-pulse"></div>
            </div>
            <p className="text-2xl font-bold text-white">Loading locations...</p>
            <p className="text-sm text-purple-200 mt-2">Please wait</p>
          </div>
        </div>
      ) : /* Step 1: Location Selection */
      !locationSelected && allLocations.length > 1 ? (
        <LocationSelector
          onLocationSelect={handleLocationSelect}
          locations={allLocations}
        />
      ) : /* Step 2: Authentication */
      !isAuthenticated ? (
        <div className="relative h-full w-full flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 overflow-hidden">
          {/* Animated Background */}
          <div className="absolute inset-0 overflow-hidden">
            <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-purple-500/10 rounded-full blur-3xl animate-pulse"></div>
            <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-blue-500/10 rounded-full blur-3xl animate-pulse delay-700"></div>
          </div>

          {/* Login Card */}
          <div className="relative z-10 w-[90%] md:w-[500px] lg:w-[600px]">
            <div className="relative overflow-hidden bg-gradient-to-br from-slate-800/90 to-slate-900/90 backdrop-blur-2xl border-2 border-slate-700/50 rounded-3xl shadow-2xl shadow-purple-500/20 p-8 md:p-12">
              {/* Glow Effect */}
              <div className="absolute inset-0 bg-gradient-to-r from-purple-500/0 via-purple-500/5 to-blue-500/0"></div>

              {/* Content */}
              <div className="relative space-y-8">
                {/* Logo */}
                <div className="flex justify-center">
                  <div className="relative">
                    <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-blue-500 blur-xl opacity-50 animate-pulse"></div>
                    <Image
                      src="/logo.png"
                      width={120}
                      height={120}
                      className="relative shadow-2xl"
                      alt="Logo"
                    />
                  </div>
                </div>

                {/* Title */}
                <div className="text-center space-y-3">
                  <div className="flex items-center justify-center gap-2">
                    {/* <Sparkles className="h-6 w-6 text-yellow-400 animate-pulse" /> */}
                    <h1 className={`font-black text-3xl md:text-4xl bg-gradient-to-r from-white via-purple-200 to-white bg-clip-text text-transparent ${montserrat.className}`}>
                      Welcome Back
                    </h1>
                    {/* <Sparkles className="h-6 w-6 text-yellow-400 animate-pulse" /> */}
                  </div>
                  <p className="text-purple-200 text-lg">
                    {selectedLocation?.name || 'Media Player Interface'}
                  </p>
                  <div className="flex items-center justify-center gap-2 text-sm text-slate-400">
                    <Lock className="h-4 w-4" />
                    <span>Secure Authentication Required</span>
                  </div>
                </div>

                {/* Login Form */}
                <form onSubmit={handleLogin} className="space-y-6">
                  <div className="space-y-2">
                    <label className="block text-sm font-semibold text-slate-300 text-left">
                      Passcode
                    </label>
                    <input
                      type="password"
                      value={password}
                      onChange={handlePasswordChange}
                      autoFocus
                      placeholder="Enter your passcode"
                      className="w-full h-14 px-6 bg-slate-900/50 border-2 border-slate-700/50 focus:border-purple-500/50 rounded-xl text-white text-lg placeholder:text-slate-500 focus:outline-none focus:ring-4 focus:ring-purple-500/20 transition-all duration-300"
                    />
                  </div>

                  {error && (
                    <div className="p-4 bg-red-500/10 border border-red-500/50 rounded-xl">
                      <p className="text-red-400 text-sm font-medium">{error}</p>
                    </div>
                  )}

                  <button
                    type="submit"
                    disabled={isLoading}
                    className="w-full h-14 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white font-bold text-lg rounded-xl shadow-lg hover:shadow-purple-500/50 transition-all duration-300 hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed group"
                  >
                    <span className="flex items-center justify-center gap-2">
                      {isLoading ? (
                        <>
                          <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full"></div>
                          Authenticating...
                        </>
                      ) : (
                        <>
                          Login
                          <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform duration-300" />
                        </>
                      )}
                    </span>
                  </button>
                </form>

                {/* Footer */}
                <div className="text-center text-slate-400 text-sm">
                  <p>Protected by end-to-end encryption</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : /* Step 3: Dashboard */
      (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4 md:p-8">
          <div className="max-w-7xl mx-auto space-y-8">
            <DashboardHeader
              onLocationSwitch={handleLocationSwitch}
              currentLocation={selectedLocation}
            />
            <Suspense
              fallback={
                <div className="flex items-center justify-center p-12">
                  <div className="relative">
                    <div className="animate-spin rounded-full h-12 w-12 border-4 border-purple-500/30 border-t-purple-500"></div>
                    <div className="absolute inset-0 bg-purple-500/20 rounded-full blur-xl animate-pulse"></div>
                  </div>
                </div>
              }
            >
              <PiGrid />
            </Suspense>
          </div>
        </div>
      )}
    </div>
  );
}

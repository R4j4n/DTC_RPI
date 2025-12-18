// components/LocationSelector.jsx
"use client";

import { useState, useEffect } from "react";
import { Montserrat } from "next/font/google";
import Image from "next/image";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { HealthBadge } from "./HealthBadge";
import { checkAllLocations } from "@/lib/healthCheck";
import { MapPin, ArrowRight, Zap } from "lucide-react";

const montserrat = Montserrat({
  subsets: ["latin"],
  weight: ["400", "700", "900"],
});

/**
 * LocationSelector component
 * Pre-authentication screen for choosing which location to connect to
 * @param {Object} props
 * @param {Function} props.onLocationSelect - Callback when location is selected
 * @param {Array} props.locations - Array of location objects
 */
export function LocationSelector({ onLocationSelect, locations }) {
  const [locationsWithHealth, setLocationsWithHealth] = useState([]);
  const [isChecking, setIsChecking] = useState(true);

  // Run health checks on mount
  useEffect(() => {
    const runHealthChecks = async () => {
      setIsChecking(true);

      // Initialize locations with 'checking' status
      setLocationsWithHealth(
        locations.map(loc => ({ ...loc, healthStatus: 'checking' }))
      );

      // Run actual health checks
      const updatedLocations = await checkAllLocations(locations);
      setLocationsWithHealth(updatedLocations);
      setIsChecking(false);
    };

    if (locations && locations.length > 0) {
      runHealthChecks();

      // Refresh health checks every 30 seconds
      const interval = setInterval(runHealthChecks, 30000);
      return () => clearInterval(interval);
    }
  }, [locations]);

  const handleSelect = (location) => {
    console.log("Location selected:", location.name);
    onLocationSelect(location);
  };

  if (!locations || locations.length === 0) {
    return (
      <div className="h-full w-full bg-banner bg-cover bg-center items-center justify-center flex">
        <div className="m-0 p-0 w-full h-full bg-pink-800/10 flex justify-center items-center">
          <div className="h-fit w-[85%] md:w-[35%] px-10 backdrop-blur-lg bg-slate-100/10 brightness-75 rounded-xl drop-shadow-2xl items-center justify-center py-20 text-center text-white">
            <Image src="/logo.png" width={150} height={100} className="m-auto pb-10" alt="Logo" />
            <h1 className={`font-extrabold text-2xl pb-4 ${montserrat.className}`}>
              No Locations Configured
            </h1>
            <p className="text-lg">
              Please configure location servers in your environment variables.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="relative h-full min-h-screen w-full bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-purple-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-blue-500/10 rounded-full blur-3xl animate-pulse delay-700"></div>
      </div>

      {/* Content */}
      <div className="relative z-10 flex items-center justify-center min-h-screen p-4 md:p-8">
        <div className="w-full max-w-6xl">
          {/* Header */}
          <div className="text-center mb-12 animate-fade-in">
            <div className="flex items-center justify-center mb-6">
              <Image
                src="/logo.png"
                width={180}
                height={180}
                className="shadow-2xl"
                alt="AeroSports Media Logo"
              />
            </div>

            <div className="flex items-center justify-center gap-3 mb-4">
              <h1 className={`font-black text-3xl md:text-4xl bg-gradient-to-r from-white via-purple-200 to-white bg-clip-text text-transparent ${montserrat.className}`}>
                Choose Your Location
              </h1>
            </div>

            <p className="text-base md:text-lg text-purple-200 font-medium">
              Select a location to access your display management system
            </p>
          </div>

          {/* Location Grid */}
          <div className="flex flex-wrap justify-center gap-6 mb-8">
            {locationsWithHealth.map((location, index) => (
              <div
                key={location.id}
                className="group animate-slide-up w-full md:w-auto md:flex-1 md:min-w-[400px] md:max-w-[500px]"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <Card className="relative overflow-hidden bg-gradient-to-br from-slate-800/90 to-slate-900/90 backdrop-blur-xl border-2 border-slate-700/50 hover:border-purple-500/50 transition-all duration-500 hover:scale-[1.02] hover:shadow-2xl hover:shadow-purple-500/20">
                  {/* Glow Effect */}
                  <div className="absolute inset-0 bg-gradient-to-r from-purple-500/0 via-purple-500/5 to-blue-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>

                  {/* Corner Accent */}
                  <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-purple-500/20 to-transparent rounded-bl-full opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>

                  <CardHeader className="relative">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg shadow-lg group-hover:scale-110 transition-transform duration-300">
                          <MapPin className="h-6 w-6 text-white" />
                        </div>
                        <div>
                          <CardTitle className="text-2xl font-bold text-white group-hover:text-purple-200 transition-colors">
                            {location.name}
                          </CardTitle>
                        </div>
                      </div>
                      <div className="transform group-hover:scale-110 transition-transform duration-300">
                        <HealthBadge status={location.healthStatus} size="md" />
                      </div>
                    </div>

                    <CardDescription className="text-slate-400 text-sm font-mono bg-slate-900/50 px-3 py-2 rounded-lg border border-slate-700/50">
                      {location.host}
                    </CardDescription>
                  </CardHeader>

                  <CardContent className="relative">
                    <div className="space-y-4">
                      {/* Health Status */}
                      <div className="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg border border-slate-700/50">
                        <span className="font-semibold text-slate-300 flex items-center gap-2">
                          <Zap className="h-4 w-4 text-yellow-400" />
                          Status:
                        </span>
                        <HealthBadge status={location.healthStatus} showText size="sm" />
                      </div>

                      {/* Select Button */}
                      <Button
                        onClick={() => handleSelect(location)}
                        className="w-full h-12 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white font-bold text-lg rounded-lg shadow-lg hover:shadow-purple-500/50 transition-all duration-300 hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed group/btn"
                        disabled={isChecking}
                      >
                        <span className="flex items-center gap-2">
                          {isChecking ? (
                            <>
                              <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full"></div>
                              Checking...
                            </>
                          ) : (
                            <>
                              Connect
                              <ArrowRight className="h-5 w-5 group-hover/btn:translate-x-1 transition-transform duration-300" />
                            </>
                          )}
                        </span>
                      </Button>

                      {/* Warning for offline locations */}
                      {location.healthStatus === 'offline' && (
                        <div className="text-xs text-amber-400 text-center p-2 bg-amber-500/10 rounded-lg border border-amber-500/20 animate-pulse">
                          Location appears offline but you can still try to connect
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>
            ))}
          </div>

          {/* Footer */}
          <div className="text-center">
            <div className="inline-flex items-center gap-2 px-6 py-3 bg-slate-800/50 backdrop-blur-xl rounded-full border border-slate-700/50 text-slate-300">
              <div className="h-2 w-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium">Health status updates every 30 seconds</span>
            </div>
          </div>
        </div>
      </div>

      {/* Add custom animations */}
      <style jsx>{`
        @keyframes fade-in {
          from {
            opacity: 0;
            transform: translateY(-20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes slide-up {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .animate-fade-in {
          animation: fade-in 0.8s ease-out;
        }

        .animate-slide-up {
          animation: slide-up 0.6s ease-out both;
        }
      `}</style>
    </div>
  );
}

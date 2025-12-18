// components/DashboardHeader.jsx

"use client";

import { useState } from "react";
import { RefreshCw, Settings, LogOut, MapPin, ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useRouter } from "next/navigation";
import { Montserrat } from "next/font/google";
import Image from "next/image";
import { DeviceNamesSettings } from "./DeviceNamesSettings";
import { HealthBadge } from "./HealthBadge";
import { useLocation } from "@/hooks/useLocation";

const montserrat = Montserrat({
  subsets: ["latin"],
  weight: ["400", "700"],
});

export function DashboardHeader({ onLocationSwitch, currentLocation }) {
  const router = useRouter();
  const { allLocations } = useLocation();
  const [showSettings, setShowSettings] = useState(false);

  const handleCloseSettings = () => {
    setShowSettings(false);
    router.refresh();
  };

  const handleLogout = () => {
    sessionStorage.removeItem("authToken");
    router.refresh();
  };

  const handleLocationSwitchClick = () => {
    const confirmed = confirm(
      `Switch location? You will need to log in again.`
    );
    if (confirmed && onLocationSwitch) {
      onLocationSwitch();
    }
  };

  return (
    <>
      <div className={`relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-800/50 to-slate-900/50 backdrop-blur-xl border border-slate-700/50 p-6 mb-6 shadow-xl ${montserrat.className}`}>
        {/* Subtle glow effect */}
        <div className="absolute inset-0 bg-gradient-to-r from-purple-500/5 to-blue-500/5"></div>

        <div className="relative flex items-center justify-between">
          {/* Left: Logo and Title */}
          <div className="flex items-center gap-4">
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-blue-500 blur-lg opacity-0 group-hover:opacity-50 transition-opacity duration-300"></div>
              <Image
                src="/logo.png"
                height={60}
                width={60}
                alt="Logo"
                className="relative shadow-lg"
              />
            </div>
            <div>
              <h1 className="text-2xl font-black bg-gradient-to-r from-white to-purple-200 bg-clip-text text-transparent">
                Display Management
              </h1>
              <p className="text-sm text-slate-400">Control & Monitor</p>
            </div>
          </div>

          {/* Right: Action Buttons */}
          <div className="flex items-center gap-2">
            {/* Location Switcher */}
            {allLocations && allLocations.length > 1 && (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="outline"
                    className="border-slate-600 bg-slate-800/50 hover:bg-slate-700/50 hover:border-purple-500/50 text-white transition-all duration-300"
                  >
                    <MapPin className="h-4 w-4 mr-2 text-purple-400" />
                    {currentLocation?.name || 'Select Location'}
                    <ChevronDown className="h-3 w-3 ml-2" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent
                  align="end"
                  className="w-56 bg-slate-800 border-slate-700"
                >
                  <DropdownMenuLabel className="text-slate-300">
                    Current Location
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator className="bg-slate-700" />
                  <div className="px-2 py-1.5 text-sm font-medium text-purple-400">
                    {currentLocation?.name || 'None'}
                  </div>
                  <DropdownMenuSeparator className="bg-slate-700" />
                  <DropdownMenuLabel className="text-slate-300">
                    Switch Location
                  </DropdownMenuLabel>
                  <DropdownMenuItem
                    onClick={handleLocationSwitchClick}
                    className="text-white hover:bg-purple-500/20 focus:bg-purple-500/20 cursor-pointer"
                  >
                    <MapPin className="h-4 w-4 mr-2" />
                    Choose Different Location
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            )}

            <Button
              variant="outline"
              onClick={() => setShowSettings(true)}
              className="border-slate-600 bg-slate-800/50 hover:bg-slate-700/50 hover:border-blue-500/50 text-white transition-all duration-300"
            >
              <Settings className="h-4 w-4 mr-2 text-blue-400" />
              <span className="hidden md:inline">Device Names</span>
            </Button>

            <Button
              onClick={() => router.refresh()}
              className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white border-0 shadow-lg hover:shadow-purple-500/50 transition-all duration-300 hover:scale-105"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              <span className="hidden md:inline">Refresh</span>
            </Button>

            <Button
              variant="outline"
              onClick={handleLogout}
              className="border-red-500/50 bg-red-500/10 hover:bg-red-500/20 hover:border-red-500 text-red-400 hover:text-red-300 transition-all duration-300"
            >
              <LogOut className="h-4 w-4 mr-2" />
              <span className="hidden md:inline">Logout</span>
            </Button>
          </div>
        </div>
      </div>
      {showSettings && <DeviceNamesSettings onClose={handleCloseSettings} />}
    </>
  );
}

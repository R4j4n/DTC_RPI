// components/DashboardHeader.jsx

"use client";

import { useState } from "react";
import { RefreshCw, Settings, LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { Montserrat } from "next/font/google";
import Image from "next/image";
import { DeviceNamesSettings } from "./DeviceNamesSettings";

const montserrat = Montserrat({
  subsets: ["latin"],
  weight: ["400", "700"],
});

export function DashboardHeader() {
  const router = useRouter();
  const [showSettings, setShowSettings] = useState(false);

  const handleCloseSettings = () => {
    setShowSettings(false);
    router.refresh();
  };

  const handleLogout = () => {
    sessionStorage.removeItem("authToken");
    router.refresh();
  };

  return (
    <>
      <div
        className={`flex items-center justify-between pb-4 ${montserrat.className}`}
      >
        <div className="flex items-center w-fit gap-x-4">
          <Image src="/logo.png" height={80} width={80} alt="Logo" />
          <h1 className="text-2xl font-bold">Aerosports TV control</h1>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setShowSettings(true)}>
            <Settings className="h-4 w-4 mr-2" />
            Device Names
          </Button>
          <Button onClick={() => router.refresh()}>
            <RefreshCw className="h-3 w-4 mr-2" />
            Refresh All
          </Button>
          <Button variant="outline" onClick={handleLogout} className="text-red-600 hover:text-red-700 hover:bg-red-50">
            <LogOut className="h-4 w-4 mr-2" />
            Logout
          </Button>
        </div>
      </div>
      {showSettings && <DeviceNamesSettings onClose={handleCloseSettings} />}
    </>
  );
}

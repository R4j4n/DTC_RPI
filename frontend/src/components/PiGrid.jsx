// components/PiGrid.jsx
"use client";

import { useState, useEffect } from "react";
import { PiCard } from "./PiCard";
import { GroupsList } from "./GroupManagement";
import { GroupControl } from "./GroupControl";
import { fetchPis, getDeviceNames } from "@/lib/api";
import { isDeviceInAnyGroup, getGroups } from "@/lib/groupUtils";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";

export function PiGrid() {
  const [pis, setPis] = useState([]);
  const [deviceNames, setDeviceNames] = useState({});
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("individual");
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [loading, setLoading] = useState(true);


  useEffect(() => {
    async function loadPis() {
      try {
        setLoading(true);
        const [pisResult, namesResult] = await Promise.all([
          fetchPis(process.env.NEXT_PUBLIC_ACTIVE_SERVER_HOSTNAME),
          getDeviceNames().catch(() => ({}))
        ]);
        const pisList = Array.isArray(pisResult) ? pisResult : Object.values(pisResult);

        // Merge custom names with device data
        const pisWithCustomNames = pisList.map(pi => ({
          ...pi,
          displayName: namesResult[pi.host] || pi.name
        }));

        setPis(pisWithCustomNames);
        setDeviceNames(namesResult);
        setLoading(false);
      } catch (err) {
        console.error("Failed to fetch Pis:", err);
        setError("Failed to load Pis");
        setLoading(false);
      }
    }

    loadPis();
  }, []);

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]" role="status">
            <span className="!absolute !-m-px !h-px !w-px !overflow-hidden !whitespace-nowrap !border-0 !p-0 ![clip:rect(0,0,0,0)]">Loading...</span>
          </div>
          <p className="mt-4 text-gray-600">Loading devices...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="individual">Individual Devices</TabsTrigger>
          <TabsTrigger value="groups">Device Groups</TabsTrigger>
        </TabsList>

        <TabsContent value="individual" className="space-y-6">
          {pis.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500 text-lg">No Raspberry Pi devices found on the network</p>
              <p className="text-gray-400 text-sm mt-2">Make sure your devices are powered on and connected to the network</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
              {pis.map((pi) => (
                <PiCard key={pi.host} pi={pi} />
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="groups">
          {selectedGroup ? (
            <div className="space-y-4">
              <button
                onClick={() => setSelectedGroup(null)}
                className="text-blue-600 hover:underline mb-4"
              >
                ← Back to Groups
              </button>
              <GroupControl group={selectedGroup} />
            </div>
          ) : (
            <GroupsList
              availablePis={pis}
              onSelectGroup={(group) => {
                setSelectedGroup(group);
                console.log("Selected group:", group);
              }}
            />
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}

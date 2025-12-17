"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { getDeviceNames, updateDeviceName, deleteDeviceName, fetchPis } from "@/lib/api";
import { X, Save, Edit2, Check } from "lucide-react";

export function DeviceNamesSettings({ onClose }) {
  const [deviceNames, setDeviceNames] = useState({});
  const [devices, setDevices] = useState([]);
  const [editingDevice, setEditingDevice] = useState(null);
  const [editValue, setEditValue] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [namesData, pisData] = await Promise.all([
        getDeviceNames(),
        fetchPis()
      ]);
      setDeviceNames(namesData);
      setDevices(Array.isArray(pisData) ? pisData : Object.values(pisData));
      setLoading(false);
    } catch (err) {
      console.error("Failed to load data:", err);
      setError("Failed to load device information");
      setLoading(false);
    }
  };

  const handleStartEdit = (device) => {
    setEditingDevice(device.host);
    setEditValue(deviceNames[device.host] || device.name);
    setError(null);
    setSuccess(null);
  };

  const handleSave = async (host) => {
    try {
      if (!editValue.trim()) {
        setError("Device name cannot be empty");
        return;
      }

      await updateDeviceName(host, editValue.trim());
      setDeviceNames({ ...deviceNames, [host]: editValue.trim() });
      setEditingDevice(null);
      setSuccess("Device name updated successfully");
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      console.error("Failed to update device name:", err);
      setError("Failed to update device name");
    }
  };

  const handleReset = async (host) => {
    try {
      await deleteDeviceName(host);
      const newDeviceNames = { ...deviceNames };
      delete newDeviceNames[host];
      setDeviceNames(newDeviceNames);
      setSuccess("Device name reset to default");
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      console.error("Failed to reset device name:", err);
      setError("Failed to reset device name");
    }
  };

  const handleCancel = () => {
    setEditingDevice(null);
    setEditValue("");
    setError(null);
  };

  const getDisplayName = (device) => {
    return deviceNames[device.host] || device.name;
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <Card className="w-full max-w-2xl mx-4">
          <CardContent className="p-8">
            <div className="text-center">Loading...</div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
        <CardHeader className="border-b">
          <div className="flex items-center justify-between">
            <CardTitle className="text-2xl font-bold">Device Name Settings</CardTitle>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-5 w-5" />
            </Button>
          </div>
          <p className="text-sm text-gray-500 mt-2">
            Customize the display names for your Raspberry Pi devices
          </p>
        </CardHeader>
        <CardContent className="p-6 overflow-y-auto">
          {error && (
            <Alert variant="destructive" className="mb-4">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          {success && (
            <Alert className="mb-4 bg-green-50 text-green-900 border-green-200">
              <AlertDescription>{success}</AlertDescription>
            </Alert>
          )}

          <div className="space-y-4">
            {devices.map((device) => (
              <div
                key={device.host}
                className="border rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-center justify-between gap-4">
                  <div className="flex-1">
                    <div className="text-sm text-gray-500 mb-1">
                      Host: {device.host}
                    </div>
                    {editingDevice === device.host ? (
                      <input
                        type="text"
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                        className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Enter device name"
                        autoFocus
                        onKeyPress={(e) => {
                          if (e.key === "Enter") {
                            handleSave(device.host);
                          } else if (e.key === "Escape") {
                            handleCancel();
                          }
                        }}
                      />
                    ) : (
                      <div className="flex items-center gap-2">
                        <div className="font-semibold text-lg">
                          {getDisplayName(device)}
                        </div>
                        {deviceNames[device.host] && (
                          <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                            Custom
                          </span>
                        )}
                      </div>
                    )}
                    {!editingDevice && (
                      <div className="text-xs text-gray-400 mt-1">
                        Original: {device.name}
                      </div>
                    )}
                  </div>

                  <div className="flex gap-2">
                    {editingDevice === device.host ? (
                      <>
                        <Button
                          size="sm"
                          onClick={() => handleSave(device.host)}
                          className="bg-green-600 hover:bg-green-700"
                        >
                          <Check className="h-4 w-4 mr-1" />
                          Save
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={handleCancel}
                        >
                          Cancel
                        </Button>
                      </>
                    ) : (
                      <>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleStartEdit(device)}
                        >
                          <Edit2 className="h-4 w-4 mr-1" />
                          Edit
                        </Button>
                        {deviceNames[device.host] && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleReset(device.host)}
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                          >
                            Reset
                          </Button>
                        )}
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {devices.length === 0 && (
            <div className="text-center text-gray-500 py-8">
              No devices found
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

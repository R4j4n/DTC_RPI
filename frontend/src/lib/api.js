// api.js

// Helper function to get the base URL
export function getBaseUrl() {
  const hostname = process.env.NEXT_PUBLIC_ACTIVE_SERVER_HOSTNAME;
  console.log("Base URL being used:", hostname);
  // Check if hostname is a complete URL (like from zrok)
  if (hostname.startsWith('http://') || hostname.startsWith('https://')) {
    return hostname;
  }
  
  // For local development, add the port
  return `http://${hostname}:7777`;
}

// Dashboard Login function
export async function auth_login(host, user_entered_pw) {
  const response = await fetch(`${getBaseUrl()}/pi/${host}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      'skip_zrok_interstitial': '1'
    },
    body: JSON.stringify({
      password: user_entered_pw,
    }),
  });
  
  if (!response.ok) {
    const errorText = await response.text();
    console.error('Login failed:', response.status, errorText);
    throw new Error(`Failed to login: ${response.status} ${errorText}`);
  }
  return response;
}

export async function fetchPis(host) {
  const response = await fetch(`${getBaseUrl()}/pis`, {
    headers: {
      'skip_zrok_interstitial': '1'
    }
  });
  if (!response.ok) throw new Error("Failed to fetch Pis");
  return response.json();
}

// Individual pi API functions
export async function fetchPiStatus(host) {
  try {
    const auth_token = sessionStorage.getItem("authToken");
    const response = await fetch(`${getBaseUrl()}/pi/${host}/status`, {
      method: "GET",
      headers: {
        "AUTH": auth_token,
        'skip_zrok_interstitial': '1'
      }
    });

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error(`Authentication failed. Please log in again.`);
      } else if (response.status === 503) {
        throw new Error(`Device ${host} is offline or unreachable`);
      } else {
        throw new Error(`Failed to fetch status from ${host} (Error ${response.status})`);
      }
    }

    const data = await response.json();
    console.log(data);
    return data;
  } catch (error) {
    if (error.message) throw error;
    throw new Error(`Network error connecting to device ${host}`);
  }
}

export async function uploadVideo(host, file, onProgress = () => {}) {
  const auth_token = sessionStorage.getItem("authToken");
  const formData = new FormData();
  formData.append('file', file, file.name);

  try {
    const response = await fetch(`${getBaseUrl()}/pi/${host}/upload`, {
      method: "POST",
      headers: {
        "AUTH": auth_token,
        'skip_zrok_interstitial': '1',
      },
      body: formData,
      // Add timeout of 10 minutes for large files
      signal: AbortSignal.timeout(600000)
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Upload failed with status:', response.status);
      console.error('Error details:', errorText);

      if (response.status === 503) {
        throw new Error(`Device ${host} is offline or unreachable`);
      } else if (response.status === 413) {
        throw new Error('File is too large. Maximum size is 500MB.');
      } else if (response.status === 401) {
        throw new Error('Authentication failed. Please log in again.');
      }
      throw new Error(`Upload failed: ${errorText || 'Unknown error'}`);
    }
    const result = await response.json();
    return result;
  } catch (error) {
    if (error.name === 'TimeoutError') {
      throw new Error('Upload timed out after 10 minutes. Try a smaller file or check your connection.');
    }
    if (error.message) throw error;
    throw new Error(`Network error while uploading to ${host}`);
  }
}

export async function playVideo(host, videoName) {
  const auth_token = sessionStorage.getItem("authToken");
  const response = await fetch(`${getBaseUrl()}/pi/${host}/play`, {
    method: "POST",
    headers: {"AUTH": auth_token, "Content-Type": "application/json",'skip_zrok_interstitial': '1'},
    body: JSON.stringify({ video_name: videoName }),
  });
  if (!response.ok) {
    if (response.status === 503) {
      throw new Error(`Device ${host} is offline`);
    }
    throw new Error(`Failed to play "${videoName}" on device`);
  }
}

export async function pauseVideo(host) {
  const auth_token = sessionStorage.getItem("authToken");
  const response = await fetch(`${getBaseUrl()}/pi/${host}/pause`, {
    headers: {"AUTH": auth_token,'skip_zrok_interstitial': '1'},
    method: "POST"
  });
  if (!response.ok) throw new Error("Failed to pause video");
}

export async function resumeVideo(host) {
  const auth_token = sessionStorage.getItem("authToken");
  const response = await fetch(`${getBaseUrl()}/pi/${host}/resume`, {
    method: "POST",
    headers: {"AUTH": auth_token,'skip_zrok_interstitial': '1'},
  });
  if (!response.ok) throw new Error("Failed to resume video");
}

export async function stopVideo(host) {
  const auth_token = sessionStorage.getItem("authToken");
  const response = await fetch(`${getBaseUrl()}/pi/${host}/stop`, {
    method: "POST",
    headers: {"AUTH": auth_token,'skip_zrok_interstitial': '1'}
  });
  if (!response.ok) throw new Error("Failed to stop video");
}

export async function deleteVideo(host, videoName) {
  const auth_token = sessionStorage.getItem("authToken");
  const response = await fetch(`${getBaseUrl()}/pi/${host}/video/${videoName}`, {
    method: "DELETE",
    headers: {"AUTH": auth_token,'skip_zrok_interstitial': '1'}
  });
  if (!response.ok) throw new Error("Failed to delete video");
}

export async function previewVideo(host) {
  const auth_token = sessionStorage.getItem("authToken");
  const response = await fetch(`${getBaseUrl()}/pi/${host}/preview/`, {
    method: "GET",
    headers: {"AUTH": auth_token,'skip_zrok_interstitial': '1'}
  });
  if (!response.ok) throw new Error("Failed to get preview");
  return response;
}

// TV controls API functions
export async function isTVOn(host) {
  const auth_token = sessionStorage.getItem("authToken");
  const response = await fetch(`${getBaseUrl()}/pi/${host}/tv/status`, {
    method: "GET",
    headers: {"AUTH": auth_token,'skip_zrok_interstitial': '1'}
  });
  if (!response.ok) throw new Error("Failed to fetch the tv status.");
  return response.json();
}

export async function getSchedule(host) {
  const auth_token = sessionStorage.getItem("authToken");
  try {
    const response = await fetch(`${getBaseUrl()}/pi/${host}/tv/get_schedule`, {
      headers: {"AUTH": auth_token,'skip_zrok_interstitial': '1'}
    });
    if (!response.ok) throw new Error("Failed to fetch the schedule");
    return response.json();
  } catch {
    console.log("Failed to fetch the schedule. . . .");
  }
}

export async function saveSchedule(host, schedule) {
  const auth_token = sessionStorage.getItem("authToken");
  const response = await fetch(`${getBaseUrl()}/pi/${host}/tv/set_schedule`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "AUTH": auth_token,'skip_zrok_interstitial': '1'},
    body: JSON.stringify(schedule),
  });
  if (!response.ok) throw new Error("Failed to save schedule");
}

export async function deleteSchedule(host) {
  const auth_token = sessionStorage.getItem("authToken");
  try {
    const response = await fetch(`${getBaseUrl()}/pi/${host}/tv/clear_schedule`, {
      method: "DELETE",
      headers: {"AUTH": auth_token,'skip_zrok_interstitial': '1'}
    });
    if (!response.ok) throw new Error("Failed to clear the schedule");
    return response.json();
  } catch {
    console.log("Failed to delete the schedule. . . .");
  }
}

export async function check_json(host) {
  const auth_token = sessionStorage.getItem("authToken");
  const response = await fetch(`${getBaseUrl()}/pi/${host}/tv/check_json`, {
    method: "GET",
    headers: {"AUTH": auth_token,'skip_zrok_interstitial': '1'}
  });
  if (!response.ok) throw new Error("Failed to fetch if the json file exists.");
  return response.json();
}

export async function set_hdmi_map(host, formData) {
  const auth_token = sessionStorage.getItem("authToken");
  const response = await fetch(`${getBaseUrl()}/pi/${host}/tv/set_hdmi_map`, {
    method: "POST",
    headers: {"AUTH": auth_token, "Content-Type": "application/json",'skip_zrok_interstitial': '1'},
    body: JSON.stringify(formData),
  });
  console.log("The response is: ", response.status);
  if (!response.ok)
    throw new Error("Failed to set the hdmi map.");
}

export async function fetch_hdmi_map(host) {
  const auth_token = sessionStorage.getItem("authToken");
  const response = await fetch(`${getBaseUrl()}/pi/${host}/tv/fetch_hdmi_map`, {
    method: "GET",
    headers: {"AUTH": auth_token,'skip_zrok_interstitial': '1'},
  });
  if (!response.ok) throw new Error("Failed to fetch the hdmi map.");
  return response.json();
}

export async function getCurrentActiveDevice(host) {
  try {
    const auth_token = sessionStorage.getItem("authToken");
    const response = await fetch(`${getBaseUrl()}/pi/${host}/tv/current`, {
      headers: {"AUTH": auth_token,'skip_zrok_interstitial': '1'},
      method: 'GET'
    });
    if (!response.ok) throw new Error("Failed to fetch the current device");
    const data = await response.json();
    return data;
  } catch {
    console.log("Failed to fetch the current device. . . .");
  }
}

export async function reset_hdmi_map(host) {
  const auth_token = sessionStorage.getItem("authToken");
  const response = await fetch(`${getBaseUrl()}/pi/${host}/tv/reset`, {
    method: "POST",
    headers: {"AUTH": auth_token,'skip_zrok_interstitial': '1'},
  });
  if (!response.ok) throw new Error("Failed to reset the hdmi map.");
}

export async function switchDevice(host, new_device) {
  const auth_token = sessionStorage.getItem("authToken");
  const response = await fetch(`${getBaseUrl()}/pi/${host}/tv/switch/${new_device}`, {
    method: "POST",
    headers: {"AUTH": auth_token,'skip_zrok_interstitial': '1'},
    body: JSON.stringify(new_device),
  });
  if (response.status === 500) console.error("Unable to switch device . . .");
}

// Device Names API functions
export async function getDeviceNames() {
  const response = await fetch(`${getBaseUrl()}/device-names`, {
    headers: {
      'skip_zrok_interstitial': '1'
    }
  });
  if (!response.ok) throw new Error("Failed to fetch device names");
  return response.json();
}

export async function updateDeviceName(host, customName) {
  const response = await fetch(`${getBaseUrl()}/device-names`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      'skip_zrok_interstitial': '1'
    },
    body: JSON.stringify({ host, custom_name: customName }),
  });
  if (!response.ok) throw new Error("Failed to update device name");
  return response.json();
}

export async function deleteDeviceName(host) {
  const response = await fetch(`${getBaseUrl()}/device-names/${host}`, {
    method: "DELETE",
    headers: {
      'skip_zrok_interstitial': '1'
    }
  });
  if (!response.ok) throw new Error("Failed to delete device name");
  return response.json();
}
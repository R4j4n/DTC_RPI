// components/HealthBadge.jsx
"use client";

import { CheckCircle2, XCircle, AlertCircle, Loader2 } from "lucide-react";

/**
 * HealthBadge component - Sleek visual indicator for location/server health status
 * @param {Object} props
 * @param {'online'|'offline'|'checking'|'error'} props.status - Health status
 * @param {'sm'|'md'} props.size - Badge size (default: 'md')
 * @param {boolean} props.showText - Whether to show status text (default: false)
 */
export function HealthBadge({ status, size = 'md', showText = false }) {
  const sizeClasses = {
    sm: 'h-3 w-3',
    md: 'h-5 w-5'
  };

  const iconSize = sizeClasses[size] || sizeClasses.md;

  const statusConfig = {
    online: {
      icon: CheckCircle2,
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-500/20',
      borderColor: 'border-emerald-500/50',
      glowColor: 'shadow-emerald-500/50',
      text: 'Online',
      pulseColor: 'bg-emerald-400'
    },
    offline: {
      icon: XCircle,
      color: 'text-red-400',
      bgColor: 'bg-red-500/20',
      borderColor: 'border-red-500/50',
      glowColor: 'shadow-red-500/50',
      text: 'Offline',
      pulseColor: 'bg-red-400'
    },
    error: {
      icon: AlertCircle,
      color: 'text-amber-400',
      bgColor: 'bg-amber-500/20',
      borderColor: 'border-amber-500/50',
      glowColor: 'shadow-amber-500/50',
      text: 'Error',
      pulseColor: 'bg-amber-400'
    },
    checking: {
      icon: Loader2,
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/20',
      borderColor: 'border-blue-500/50',
      glowColor: 'shadow-blue-500/50',
      text: 'Checking...',
      animate: true,
      pulseColor: 'bg-blue-400'
    }
  };

  const config = statusConfig[status] || statusConfig.checking;
  const Icon = config.icon;

  if (showText) {
    return (
      <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full border ${config.bgColor} ${config.borderColor} backdrop-blur-sm shadow-lg ${config.glowColor} transition-all duration-300 hover:scale-105`}>
        <div className="relative">
          <Icon
            className={`${iconSize} ${config.color} ${config.animate ? 'animate-spin' : ''}`}
          />
          {!config.animate && (
            <div className={`absolute inset-0 ${config.pulseColor} rounded-full blur-md opacity-50 animate-pulse`}></div>
          )}
        </div>
        <span className={`text-xs font-bold ${config.color} uppercase tracking-wider`}>
          {config.text}
        </span>
      </div>
    );
  }

  return (
    <div className="relative inline-flex items-center group">
      {/* Glow effect */}
      <div className={`absolute inset-0 ${config.pulseColor} rounded-full blur-lg opacity-0 group-hover:opacity-60 transition-opacity duration-300`}></div>

      {/* Icon */}
      <div className="relative">
        <Icon
          className={`${iconSize} ${config.color} ${config.animate ? 'animate-spin' : ''} drop-shadow-lg`}
          aria-label={config.text}
        />
        {/* Pulse ring for non-checking states */}
        {!config.animate && (
          <div className={`absolute inset-0 ${config.pulseColor} rounded-full animate-ping opacity-20`}></div>
        )}
      </div>
    </div>
  );
}

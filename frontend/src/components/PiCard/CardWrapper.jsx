// components/PiCard/CardWrapper.jsx
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";
import TVOnStatus from "./TVOnStatus";

export function CardWrapper({
  pi,
  title,
  status,
  error,
  tvStatus,
  onRefresh,
  isGroup = false,
  children,
}) {
  return (
    <Card
      className={`w-full drop-shadow-lg ${
        !status ? "bg-red-400/20" : ""
      } hover:drop-shadow-xl `}
    >
      <CardHeader className="space-y-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-xl font-bold truncate flex-1">
            {isGroup ? title : (pi?.displayName || pi?.name)}
          </CardTitle>
          {onRefresh && (
            <Button
              variant="ghost"
              size="icon"
              onClick={() => onRefresh()}
              className="ml-2 flex-shrink-0"
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
          )}
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          {!isGroup && <TVOnStatus tvStatus={tvStatus} />}
          {status ? (
            <div className="text-slate-200 px-4 py-1 rounded-full bg-emerald-600 text-sm">
              Active
            </div>
          ) : (
            <div className="text-slate-200 px-4 py-1 rounded-full bg-rose-600 text-sm">
              Inactive
            </div>
          )}
        </div>
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
      </CardHeader>
      <CardContent className="space-y-4">{children}</CardContent>
    </Card>
  );
}
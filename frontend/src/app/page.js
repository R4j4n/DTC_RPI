// app/page.js

import Dashboard from '@/components/Dashboard'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { LocationProvider } from '@/contexts/LocationContext'

export default function Home() {
  return (
    <ErrorBoundary>
      <LocationProvider>
        <Dashboard />
      </LocationProvider>
    </ErrorBoundary>
  )
}
import { Link, Outlet, useLocation } from 'react-router-dom'
import { Film, Home, History, Settings, Zap } from 'lucide-react'
import { cn } from '@/lib/utils'

const nav = [
  { to: '/', icon: Home, label: 'Dashboard' },
  { to: '/generate', icon: Zap, label: 'Generate' },
  { to: '/history', icon: History, label: 'History' },
  { to: '/config', icon: Settings, label: 'Config' },
]

export function Layout() {
  const location = useLocation()
  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      <header className="sticky top-0 z-50 border-b border-zinc-800 bg-zinc-950/95 backdrop-blur">
        <div className="mx-auto flex h-14 max-w-7xl items-center px-4 sm:px-6">
          <Link to="/" className="flex items-center gap-2 font-semibold">
            <Film className="h-6 w-6 text-red-500" />
            <span className="hidden sm:inline">YouTube Shorts</span>
          </Link>
          <nav className="ml-8 flex gap-1">
            {nav.map(({ to, icon: Icon, label }) => (
              <Link
                key={to}
                to={to}
                className={cn(
                  'flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                  location.pathname === to || (to !== '/' && location.pathname.startsWith(to))
                    ? 'bg-zinc-800 text-white'
                    : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-zinc-200'
                )}
              >
                <Icon className="h-4 w-4" />
                {label}
              </Link>
            ))}
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6">
        <Outlet />
      </main>
    </div>
  )
}

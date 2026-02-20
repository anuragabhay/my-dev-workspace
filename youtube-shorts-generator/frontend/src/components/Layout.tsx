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
      <header className="sticky top-0 z-50 border-b border-zinc-800/60 bg-zinc-950/80 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-7xl items-center gap-8 px-4 sm:px-6">
          <Link to="/" className="flex items-center gap-2.5 font-bold text-lg">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-red-600">
              <Film className="h-4 w-4 text-white" />
            </div>
            <span className="hidden sm:inline bg-gradient-to-r from-white to-zinc-400 bg-clip-text text-transparent">
              Shorts Generator
            </span>
          </Link>
          <nav className="flex gap-1">
            {nav.map(({ to, icon: Icon, label }) => (
              <Link
                key={to}
                to={to}
                className={cn(
                  'flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-all duration-150',
                  location.pathname === to || (to !== '/' && location.pathname.startsWith(to))
                    ? 'bg-zinc-800 text-white shadow-sm shadow-zinc-900/50'
                    : 'text-zinc-400 hover:bg-zinc-800/40 hover:text-zinc-200'
                )}
              >
                <Icon className="h-4 w-4" />
                <span className="hidden sm:inline">{label}</span>
              </Link>
            ))}
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
        <Outlet />
      </main>
    </div>
  )
}

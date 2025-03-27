import Link from "next/link"
import { Button } from "@/components/ui/button"

const navigation = [
  { name: "Dashboard", href: "/dashboard" },
  { name: "Birth Chart", href: "/birth-chart" },
  { name: "Compatibility", href: "/compatibility" },
  { name: "Daily Horoscope", href: "/horoscope-today" },
  { name: "Personality Profile", href: "/personality-profile" },
]

export function MainNav() {
  return (
    <nav className="border-b border-white/10 bg-background">
      <div className="container flex h-16 items-center justify-between">
        <Link href="/" className="flex items-center space-x-2">
          <span className="font-medium">
            <span className="text-neon-teal">Daily</span>
            <span className="text-neon-pink">Heavens</span>
          </span>
        </Link>
        <div className="flex items-center gap-4">
          <Button variant="ghost" className="text-white hover:text-neon-teal">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
            </svg>
            Login
          </Button>
        </div>
      </div>
    </nav>
  )
} 
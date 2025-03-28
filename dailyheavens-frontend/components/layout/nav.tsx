import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import Link from "next/link"

export function Nav({ email, activeTab, onTabChange }: { 
  email: string
  activeTab: string
  onTabChange: (value: string) => void 
}) {
  return (
    <header className="border-b">
      <div className="container flex h-16 items-center justify-between px-4">
        <div className="flex items-center gap-6">
          <Link href="/" className="font-semibold">
            Daily Heavens
          </Link>
          <Tabs value={activeTab} onValueChange={onTabChange} className="hidden md:block">
            <TabsList>
              <TabsTrigger value="birth-chart">Birth Chart</TabsTrigger>
              <TabsTrigger value="interpretation">Interpretation</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>
        <div className="flex items-center gap-4">
          <Link href="/profile">
            <div className="flex items-center gap-2">
              <Avatar className="h-8 w-8">
                <AvatarFallback>{email.substring(0, 2).toUpperCase()}</AvatarFallback>
              </Avatar>
              <span className="hidden md:inline-block text-sm">{email}</span>
            </div>
          </Link>
        </div>
      </div>
    </header>
  )
} 
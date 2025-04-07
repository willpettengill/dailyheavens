import React from "react"
import Link from "next/link"

interface NavProps {
  email: string;
  activeTab: string;
  onTabChange: (tab: string) => void;
}

export function Nav({ email, activeTab, onTabChange }: NavProps) {
  return (
    <div className="border-b">
      <div className="flex h-16 items-center px-4">
        <div className="flex items-center gap-6">
          <Link href="/" className="font-semibold">
            Daily Heavens
          </Link>
          <div className="flex gap-4">
            <button
              onClick={() => onTabChange("birth-chart")}
              className={`text-sm font-medium ${
                activeTab === "birth-chart"
                  ? "text-foreground"
                  : "text-muted-foreground"
              }`}
            >
              Birth Chart
            </button>
            <button
              onClick={() => onTabChange("interpretation")}
              className={`text-sm font-medium ${
                activeTab === "interpretation"
                  ? "text-foreground"
                  : "text-muted-foreground"
              }`}
            >
              Interpretation
            </button>
          </div>
        </div>
        <div className="ml-auto flex items-center space-x-4">
          <div className="text-sm text-muted-foreground">
            {email}
          </div>
        </div>
      </div>
    </div>
  )
} 
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function ProfilePage() {
  return (
    <div className="container mx-auto py-8 px-4">
      <Card>
        <CardHeader>
          <CardTitle>Profile</CardTitle>
          <CardDescription>
            Your account settings and preferences.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">Profile settings coming soon...</p>
        </CardContent>
      </Card>
    </div>
  )
} 
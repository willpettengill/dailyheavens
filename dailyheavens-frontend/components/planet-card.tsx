import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { planetIcons, signIcons, planetDescriptions } from "@/components/ui/planet-icons"

interface PlanetCardProps {
  planet: string
  sign: string
  house: string
  sign_description?: string
  description?: string
  retrograde?: boolean
}

export function PlanetCard({ planet, sign, house, sign_description, description, retrograde }: PlanetCardProps) {
  const formattedPlanet = planet.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')
  
  const signLower = sign?.toLowerCase();
  const signIcon = signLower && signIcons[signLower] ? signIcons[signLower] : '';

  // Debug
  console.log(`PlanetCard ${formattedPlanet}: retrograde=${retrograde}`);

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex flex-col">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg font-bold">
              {planetIcons[planet]} {formattedPlanet}
            </CardTitle>
            <span className="text-sm text-muted-foreground">House {house || '?'}</span>
          </div>
          <p className="text-xs text-muted-foreground mt-1">{description || planetDescriptions[planet]}</p>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col items-center text-center">
          <h4 className="text-xl font-semibold flex items-center">
            {signIcon && <span className="mr-2">{signIcon}</span>}
            {sign || 'Unknown'}
            {retrograde && <Badge className="ml-2 bg-orange-600" variant="secondary">Rx</Badge>}
          </h4>
          {sign_description && (
            <p className="text-sm text-muted-foreground mt-1 italic">
              {sign_description}
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  )
} 
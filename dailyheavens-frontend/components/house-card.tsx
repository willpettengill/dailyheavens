import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { signIcons, houseIcons, houseDescriptions } from "@/lib/astrological-symbols"

interface HouseCardProps {
  house: string
  sign: string
  description?: string
}

export function HouseCard({ house, sign, description }: HouseCardProps) {
  const signLower = sign?.toLowerCase();
  const signIcon = signLower && signIcons[signLower] ? signIcons[signLower] : '';
  
  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex flex-col">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg font-bold">
              {houseIcons[house]} House {house}
            </CardTitle>
          </div>
          <p className="text-xs text-muted-foreground mt-1">{description || houseDescriptions[house]}</p>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col items-center text-center">
          <h4 className="text-xl font-semibold flex items-center">
            {signIcon && <span className="mr-2">{signIcon}</span>}
            {sign}
          </h4>
        </div>
      </CardContent>
    </Card>
  )
} 
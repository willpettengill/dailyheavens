import { NextResponse } from 'next/server';

// API endpoint URLs
const BIRTH_CHART_API_URL = process.env.NEXT_PUBLIC_BIRTH_CHART_API_URL || "http://localhost:8001/api/v1/birthchart";
const INTERPRETATION_API_URL = process.env.NEXT_PUBLIC_INTERPRETATION_API_URL || "http://localhost:8002/api/v1/interpretation";

// Helper to convert ZIP code to coordinates (mock implementation)
const getCoordinatesFromZip = (zipcode: string) => {
  // For the purpose of this demo, we'll use Westford, MA coordinates (01886)
  // In a real application, this would call a geocoding service
  return {
    latitude: 42.5795, // Westford, MA latitude
    longitude: -71.4377, // Westford, MA longitude
    timezone: "America/New_York"
  };
};

export async function POST(request: Request) {
  try {
    const data = await request.json();
    
    // Handle both frontend form submissions and direct JSON requests
    if (data.birth_date && data.birth_time && data.birth_place_zip) {
      // Handle form submission with birth_date, birth_time, and birth_place_zip
      const { birth_date, birth_time, birth_place_zip, email } = data;
      
      // Parse date and time
      const [year, month, day] = birth_date.split('-').map(Number);
      const [hour, minute] = birth_time.split(':').map(Number);
      
      // Create Date object in local timezone
      const birthDateTime = new Date(year, month - 1, day, hour, minute);
      
      // Get coordinates from ZIP
      const coordinates = getCoordinatesFromZip(birth_place_zip);
      
      // Format request for birth chart API
      const birthChartRequest = {
        date: birthDateTime.toISOString(),
        latitude: coordinates.latitude,
        longitude: coordinates.longitude,
        timezone: coordinates.timezone
      };
      
      // Make the API calls with this data
      return await processBirthChartRequest(birthChartRequest, { email, birth_date, birth_time, birth_place_zip });
    } 
    else if (data.date && data.latitude && data.longitude) {
      // Handle direct API request with date, latitude, longitude
      const { date, latitude, longitude, timezone = "UTC" } = data;
      
      // Format request for birth chart API
      const birthChartRequest = {
        date,
        latitude,
        longitude,
        timezone
      };
      
      // Make the API calls with this data
      return await processBirthChartRequest(birthChartRequest, null);
    }
    else {
      return NextResponse.json(
        { error: "Missing required fields" },
        { status: 400 }
      );
    }
  } catch (error) {
    console.error('Error processing birth chart request:', error);
    return NextResponse.json(
      { error: "Failed to process request" },
      { status: 500 }
    );
  }
}

// Process the birth chart request by calling the backend APIs
async function processBirthChartRequest(birthChartRequest: any, userData: any) {
  try {
    // Call birth chart API
    console.log("Calling birth chart API with:", JSON.stringify(birthChartRequest));
    const birthChartResponse = await fetch(BIRTH_CHART_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(birthChartRequest),
    });

    if (!birthChartResponse.ok) {
      console.error(`Birth chart API error: ${birthChartResponse.status}`);
      return NextResponse.json(
        { error: `Birth chart API returned ${birthChartResponse.status}` },
        { status: birthChartResponse.status }
      );
    }

    const birthChartData = await birthChartResponse.json();
    
    if (birthChartData.status !== "success") {
      console.error("Birth chart API returned error:", birthChartData.error);
      return NextResponse.json(
        { error: birthChartData.error || "Birth chart calculation failed" },
        { status: 400 }
      );
    }

    // Format request for interpretation API
    const interpretationRequest = {
      birth_chart: birthChartData.data,
      level: "detailed",
      area: "general"
    };

    // Call interpretation API
    console.log("Calling interpretation API");
    const interpretationResponse = await fetch(INTERPRETATION_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(interpretationRequest),
    });

    if (!interpretationResponse.ok) {
      console.error(`Interpretation API error: ${interpretationResponse.status}`);
      // Still return birth chart data even if interpretation fails
      return NextResponse.json({
        user: userData,
        birth_chart: birthChartData.data,
        interpretation: null,
        message: "Interpretation service unavailable"
      });
    }

    const interpretationData = await interpretationResponse.json();

    // Combine the birth chart and interpretation data
    const combinedResponse = {
      user: userData,
      birth_chart: birthChartData.data,
      interpretation: interpretationData.data
    };

    return NextResponse.json(combinedResponse);
  } catch (error) {
    console.error('Error in processBirthChartRequest:', error);
    return NextResponse.json(
      { error: "Failed to process birth chart" },
      { status: 500 }
    );
  }
} 
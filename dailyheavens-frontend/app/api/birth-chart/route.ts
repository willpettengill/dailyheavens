import { NextResponse } from 'next/server';

interface BirthChartRequest {
  birth_date: string;
  birth_time: string;
  birth_place_zip: string;
  email: string;
}

// Function to process birth chart request
async function processBirthChartRequest(
  date: string,
  latitude: number,
  longitude: number,
  timezone: string,
  userData: BirthChartRequest
): Promise<Record<string, unknown>> {
  try {
    // Call birth chart API
    console.log("Calling birth chart API with:", { date, latitude, longitude, timezone });
    const birthChartResponse = await fetch(`${process.env.NEXT_PUBLIC_BIRTH_CHART_API_URL}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        date,
        latitude,
        longitude,
        timezone,
      }),
    });

    if (!birthChartResponse.ok) {
      throw new Error("Birth chart API call failed");
    }

    const birthChartData = await birthChartResponse.json();

    // Call interpretation API
    console.log("Calling interpretation API");
    const interpretationResponse = await fetch(`${process.env.NEXT_PUBLIC_INTERPRETATION_API_URL}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        birth_chart: birthChartData.data,
        level: "detailed",
        area: "general"
      }),
    });

    if (!interpretationResponse.ok) {
      throw new Error("Interpretation API call failed");
    }

    const interpretationData = await interpretationResponse.json();

    // Combine the data - Be explicit about the structure
    return {
      user: {
        email: userData.email,
        birth_date: userData.birth_date,
        birth_time: userData.birth_time,
        birth_place_zip: userData.birth_place_zip
      },
      // Explicitly include the birth chart data, assuming it's in birthChartData.data
      birth_chart: birthChartData.data, 
      // Access the correct interpretations key from the response
      interpretation: interpretationData.data?.interpretations || null 
    };
  } catch (error) {
    console.error("Error processing birth chart request:", error);
    throw error;
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json() as BirthChartRequest;

    // Convert birth date and time to ISO string
    const [year, month, day] = body.birth_date.split("-").map(Number);
    const [hours, minutes] = body.birth_time.split(":").map(Number);
    const date = new Date(year, month - 1, day, hours, minutes);

    // For now, using hardcoded coordinates for testing
    const latitude = 42.5795;
    const longitude = -71.4377;
    const timezone = "America/New_York";

    const result = await processBirthChartRequest(
      date.toISOString(),
      latitude,
      longitude,
      timezone,
      body
    );

    return NextResponse.json(result);
  } catch (error) {
    console.error("Error in birth chart API route:", error);
    return NextResponse.json(
      { error: "Failed to process birth chart request" },
      { status: 500 }
    );
  }
} 
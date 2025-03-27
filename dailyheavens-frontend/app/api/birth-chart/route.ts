import { NextResponse } from 'next/server';

// Mock API endpoint URLs
const BIRTH_CHART_API_URL = process.env.BIRTH_CHART_API_URL || "http://localhost:8001/api/v1/birthchart";
const INTERPRETATION_API_URL = process.env.INTERPRETATION_API_URL || "http://localhost:8002/api/v1/interpretation";

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
    const { birth_date, birth_time, birth_place_zip, email } = data;

    if (!birth_date || !birth_time || !birth_place_zip) {
      return NextResponse.json(
        { error: "Missing required fields" },
        { status: 400 }
      );
    }

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

    // Call birth chart API (simulated for demo)
    // In a real application, this would make an actual API call
    const birthChartResponse = {
      status: "success",
      data: {
        planets: {
          sun: { sign: "Gemini", degree: 28.5, house: "10" },
          moon: { sign: "Virgo", degree: 15.2, house: "1" },
          mercury: { sign: "Gemini", degree: 20.1, house: "10" },
          venus: { sign: "Taurus", degree: 10.7, house: "9" },
          mars: { sign: "Aries", degree: 5.3, house: "8" },
          jupiter: { sign: "Taurus", degree: 22.4, house: "9" },
          saturn: { sign: "Capricorn", degree: 2.8, house: "5" },
          uranus: { sign: "Capricorn", degree: 1.5, house: "5" },
          neptune: { sign: "Capricorn", degree: 10.3, house: "5" },
          pluto: { sign: "Scorpio", degree: 11.7, house: "3" }
        },
        houses: {
          "1": { sign: "Virgo", degree: 5.2 },
          "2": { sign: "Libra", degree: 3.1 },
          "3": { sign: "Scorpio", degree: 2.5 },
          "4": { sign: "Sagittarius", degree: 3.7 },
          "5": { sign: "Capricorn", degree: 7.2 },
          "6": { sign: "Aquarius", degree: 10.3 },
          "7": { sign: "Pisces", degree: 5.2 },
          "8": { sign: "Aries", degree: 3.1 },
          "9": { sign: "Taurus", degree: 2.5 },
          "10": { sign: "Gemini", degree: 3.7 },
          "11": { sign: "Cancer", degree: 7.2 },
          "12": { sign: "Leo", degree: 10.3 }
        },
        aspects: [
          { planet1: "sun", planet2: "moon", type: "trine", orb: 2.1 },
          { planet1: "sun", planet2: "mercury", type: "conjunction", orb: 8.4 },
          { planet1: "venus", planet2: "jupiter", type: "conjunction", orb: 11.7 },
          { planet1: "mars", planet2: "saturn", type: "square", orb: 2.5 }
        ]
      }
    };

    // Format request for interpretation API
    const interpretationRequest = {
      birth_chart: birthChartResponse.data,
      level: "detailed",
      area: "general"
    };

    // Call interpretation API (simulated for demo)
    // In a real application, this would make an actual API call
    const interpretationResponse = {
      status: "success",
      data: {
        summary: "Your birth chart reveals a blend of Gemini and Virgo energies, with strong Earth and Air influences. The Sun in Gemini gives you versatility and intellectual curiosity, while the Moon in Virgo brings analytical precision to your emotional nature.",
        planets: [
          {
            planet: "Sun",
            sign: "Gemini",
            house: "10",
            interpretation: "With your Sun in Gemini in the 10th House, you express your core identity through communication and intellect, especially in your career and public life. You're likely drawn to professions involving writing, speaking, or making connections between people and ideas. Your versatile nature allows you to adapt to changing circumstances in your professional life."
          },
          {
            planet: "Moon",
            sign: "Virgo",
            house: "1",
            interpretation: "Your Moon in Virgo in the 1st House indicates that your emotional needs are tied to order, precision, and practical analysis. Your emotional reactions are methodical rather than spontaneous, and you process feelings through careful analysis. With the Moon in your 1st House, your emotional nature is visible to others, and you may be perceived as someone who is detail-oriented and practical."
          },
          {
            planet: "Mercury",
            sign: "Gemini",
            house: "10",
            interpretation: "Mercury in Gemini in the 10th House amplifies your communication skills, making you particularly effective in professional settings. Your mind works quickly, able to process and synthesize information rapidly. You may excel in careers requiring sharp intellect, adaptability, and excellent communication. This placement suggests success in fields like journalism, teaching, or any profession requiring mental agility."
          },
          {
            planet: "Venus",
            sign: "Taurus",
            house: "9",
            interpretation: "Venus in Taurus in the 9th House gives you a deep appreciation for beauty, comfort, and stability in your philosophical outlook and higher education. You may find pleasure in learning about different cultures, especially their artistic and aesthetic traditions. Your approach to relationships is steadfast and loyal, particularly with people from different backgrounds than your own."
          },
          {
            planet: "Mars",
            sign: "Aries",
            house: "8",
            interpretation: "Mars in Aries in the 8th House gives you tremendous drive and initiative in matters related to shared resources, intimacy, and transformation. You approach joint finances, sexuality, and psychological exploration with courage and directness. This placement can indicate a powerful sexual energy and a willingness to confront taboo subjects head-on."
          }
        ],
        houses: [
          {
            house: "1",
            sign: "Virgo",
            interpretation: "With Virgo on your 1st House cusp, you present yourself to the world as analytical, detail-oriented, and service-minded. Your approach to life involves organization, practicality, and improvement. Others may see you as methodical and precise, someone who notices details that others might miss."
          },
          {
            house: "10",
            sign: "Gemini",
            interpretation: "Gemini on the 10th House cusp suggests a career path involving communication, versatility, and intellectual exchange. You may thrive in occupations requiring adaptability and the ability to process information quickly. Your public image is likely that of someone clever, articulate, and mentally agile."
          }
        ],
        aspects: [
          {
            aspect: "Sun trine Moon",
            interpretation: "The trine between your Sun and Moon indicates a harmonious flow between your conscious will (Sun) and emotional needs (Moon). Despite the different natures of Gemini and Virgo, there's a supportive connection between your core identity and your feelings, allowing you to integrate different parts of your personality smoothly."
          },
          {
            aspect: "Sun conjunct Mercury",
            interpretation: "With your Sun conjunct Mercury, your thinking and communication style are closely aligned with your core identity. This strengthens your Gemini traits, enhancing your intellectual curiosity and communication skills. You express yourself authentically and think clearly about who you are."
          }
        ]
      }
    };

    // Combine the birth chart and interpretation data
    const combinedResponse = {
      user: {
        email,
        birth_date,
        birth_time,
        birth_place_zip
      },
      birth_chart: birthChartResponse.data,
      interpretation: interpretationResponse.data
    };

    return NextResponse.json(combinedResponse);
  } catch (error) {
    console.error('Error processing birth chart request:', error);
    return NextResponse.json(
      { error: "Failed to process request" },
      { status: 500 }
    );
  }
} 
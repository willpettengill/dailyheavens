// Astrological symbols for planets and signs used throughout the application

export const planetIcons: { [key: string]: string } = {
  sun: "☀️",
  moon: "☽",
  mercury: "☿",
  venus: "♀",
  mars: "♂",
  jupiter: "♃",
  saturn: "♄",
  uranus: "♅",
  neptune: "♆",
  pluto: "♇",
  north_node: "☊",
  south_node: "☋",
  chiron: "⚷",
  ascendant: "↑"
}

export const signIcons: { [key: string]: string } = {
  aries: "♈",
  taurus: "♉",
  gemini: "♊",
  cancer: "♋",
  leo: "♌",
  virgo: "♍",
  libra: "♎",
  scorpio: "♏",
  sagittarius: "♐",
  capricorn: "♑",
  aquarius: "♒",
  pisces: "♓",
}

export const houseIcons: { [key: string]: string } = {
  "1": "👤", // Self
  "2": "💰", // Resources
  "3": "✍️", // Communication
  "4": "🏠", // Home
  "5": "🎨", // Creativity
  "6": "⚕️", // Health
  "7": "🤝", // Relationships
  "8": "🔄", // Transformation
  "9": "🌎", // Philosophy
  "10": "👑", // Career
  "11": "👥", // Community
  "12": "🌌", // Spirituality
}

// Descriptions for planets that can be used for tooltips or informational displays
export const planetDescriptions: { [key: string]: string } = {
  sun: "Core identity and life purpose",
  moon: "Emotional nature and instincts",
  mercury: "Communication and thinking style",
  venus: "Love, beauty, and values",
  mars: "Drive, energy, and assertion",
  jupiter: "Growth, expansion, and wisdom",
  saturn: "Structure, responsibility, and limitations",
  uranus: "Innovation, freedom, and change",
  neptune: "Spirituality, imagination, and dreams",
  pluto: "Transformation and power",
  north_node: "Life direction and growth",
  south_node: "Past patterns and comfort zone",
  chiron: "Healing journey and wounds",
  ascendant: "Self-expression and outer personality (Rising Sign)"
}

// Descriptions for houses used for tooltips or informational displays
export const houseDescriptions: { [key: string]: string } = {
  "1": "Identity and self-expression",
  "2": "Values, possessions, and resources",
  "3": "Communication, learning, and siblings",
  "4": "Home, family, and emotional foundation",
  "5": "Creativity, pleasure, and self-expression",
  "6": "Work, health, and daily routines",
  "7": "Partnerships and relationships",
  "8": "Transformation, shared resources, and mystery",
  "9": "Higher learning, travel, and philosophy",
  "10": "Career, public image, and achievement",
  "11": "Friends, groups, and aspirations",
  "12": "Spirituality, unconscious, and hidden matters"
} 
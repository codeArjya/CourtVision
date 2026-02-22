export const COLORS = {
  bg: "#0D0D0D",
  surface: "#1A1A1A",
  surfaceHigh: "#242424",
  border: "#2E2E2E",
  orange: "#E87722",
  orangeLight: "#FF9A45",
  orangeDim: "#3D2200",
  white: "#F0F0F0",
  gray: "#9A9A9A",
  grayDim: "#555555",
  green: "#27AE60",
  red: "#E74C3C",
  yellow: "#F1C40F",
} as const;

export interface TeamBrand {
  primary: string;
  secondary: string;
  name: string;
}

export const NBA_TEAM_COLORS: Record<string, TeamBrand> = {
  ATL: { primary: "#E03A3E", secondary: "#C1D32F", name: "Atlanta Hawks" },
  BKN: { primary: "#AAAAAA", secondary: "#FFFFFF", name: "Brooklyn Nets" },
  BOS: { primary: "#007A33", secondary: "#BA9653", name: "Boston Celtics" },
  CHA: { primary: "#1D1160", secondary: "#00788C", name: "Charlotte Hornets" },
  CHI: { primary: "#CE1141", secondary: "#000000", name: "Chicago Bulls" },
  CLE: { primary: "#860038", secondary: "#FDBB30", name: "Cleveland Cavaliers" },
  DAL: { primary: "#00538C", secondary: "#B8C4CA", name: "Dallas Mavericks" },
  DEN: { primary: "#8B6914", secondary: "#FEC524", name: "Denver Nuggets" },
  DET: { primary: "#C8102E", secondary: "#1D42BA", name: "Detroit Pistons" },
  GSW: { primary: "#1D428A", secondary: "#FFC72C", name: "Golden State Warriors" },
  HOU: { primary: "#CE1141", secondary: "#C4CED4", name: "Houston Rockets" },
  IND: { primary: "#002D62", secondary: "#FDBB30", name: "Indiana Pacers" },
  LAC: { primary: "#C8102E", secondary: "#1D428A", name: "LA Clippers" },
  LAL: { primary: "#552583", secondary: "#FDB927", name: "Los Angeles Lakers" },
  MEM: { primary: "#5D76A9", secondary: "#12173F", name: "Memphis Grizzlies" },
  MIA: { primary: "#98002E", secondary: "#F9A01B", name: "Miami Heat" },
  MIL: { primary: "#00471B", secondary: "#EEE1C6", name: "Milwaukee Bucks" },
  MIN: { primary: "#0C2340", secondary: "#236192", name: "Minnesota Timberwolves" },
  NOP: { primary: "#0C2340", secondary: "#C8102E", name: "New Orleans Pelicans" },
  NYK: { primary: "#006BB6", secondary: "#F58426", name: "New York Knicks" },
  OKC: { primary: "#007AC1", secondary: "#EF3B24", name: "Oklahoma City Thunder" },
  ORL: { primary: "#0077C0", secondary: "#C4CED4", name: "Orlando Magic" },
  PHI: { primary: "#006BB6", secondary: "#ED174C", name: "Philadelphia 76ers" },
  PHX: { primary: "#1D1160", secondary: "#E56020", name: "Phoenix Suns" },
  POR: { primary: "#E03A3E", secondary: "#000000", name: "Portland Trail Blazers" },
  SAC: { primary: "#5A2D81", secondary: "#63727A", name: "Sacramento Kings" },
  SAS: { primary: "#C4CED4", secondary: "#000000", name: "San Antonio Spurs" },
  TOR: { primary: "#CE1141", secondary: "#000000", name: "Toronto Raptors" },
  UTA: { primary: "#F9A01B", secondary: "#000000", name: "Utah Jazz" },
  WAS: { primary: "#002B5C", secondary: "#E31837", name: "Washington Wizards" },
};

export function getTeamColor(abbr: string): TeamBrand {
  return (
    NBA_TEAM_COLORS[abbr] ?? {
      primary: "#E87722",
      secondary: "#9A9A9A",
      name: abbr,
    }
  );
}

export function getTeamLogoUrl(abbr: string): string {
  return `https://a.espncdn.com/i/teamlogos/nba/500/${abbr.toLowerCase()}.png`;
}

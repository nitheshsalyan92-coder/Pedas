/**
 * Sample records for the hackathon demo.
 * Replace these exports later with API responses. Keep the same field names.
 * Nothing in this file is a live camera detection or a real incident report.
 */

export const project = {
  name: "Urban Pedestrian Risk Prediction and Conflict Detection System",
  shortName: "PedSafe",
  city: "Demo overlay",
  note: "Zone names are fictional. The map background is OpenStreetMap, so real neighborhood names can appear underneath. Counts, scores, and conflicts are sample data, not reports about those places.",
};

export const zones = [
  {
    id: "z1",
    name: "Harbor School Crossing",
    area: "Ward 4",
    lat: 12.9814,
    lng: 77.5902,
    level: "High",
    riskPercent: 86,
    pedestrians: 248,
    vehicles: 620,
    factors: {
      trafficDensity: 88,
      pedestrianDensity: 81,
      roadConditions: 64,
      lighting: 72,
    },
    note: "Sample pattern: school arrival overlaps with heavy turning traffic.",
  },
  {
    id: "z2",
    name: "Central Market Junction",
    area: "Ward 2",
    lat: 12.9758,
    lng: 77.6034,
    level: "High",
    riskPercent: 81,
    pedestrians: 312,
    vehicles: 540,
    factors: {
      trafficDensity: 84,
      pedestrianDensity: 92,
      roadConditions: 58,
      lighting: 40,
    },
    note: "Sample pattern: crowded informal crossings at the market edge.",
  },
  {
    id: "z3",
    name: "Riverside Bus Terminal",
    area: "Ward 6",
    lat: 12.9689,
    lng: 77.5868,
    level: "High",
    riskPercent: 78,
    pedestrians: 196,
    vehicles: 710,
    factors: {
      trafficDensity: 91,
      pedestrianDensity: 70,
      roadConditions: 49,
      lighting: 55,
    },
    note: "Sample pattern: buses and people share a wide, unmarked exit.",
  },
  {
    id: "z4",
    name: "Civic Hospital Approach",
    area: "Ward 5",
    lat: 12.9862,
    lng: 77.6115,
    level: "High",
    riskPercent: 74,
    pedestrians: 154,
    vehicles: 430,
    factors: {
      trafficDensity: 69,
      pedestrianDensity: 66,
      roadConditions: 73,
      lighting: 48,
    },
    note: "Sample pattern: slower walking speeds near the hospital gate.",
  },
  {
    id: "z5",
    name: "Oak Avenue Metro Exit",
    area: "Ward 3",
    lat: 12.9712,
    lng: 77.6168,
    level: "Medium",
    riskPercent: 58,
    pedestrians: 188,
    vehicles: 360,
    factors: {
      trafficDensity: 61,
      pedestrianDensity: 74,
      roadConditions: 36,
      lighting: 44,
    },
    note: "Sample pattern: evening surge when the metro lets out.",
  },
  {
    id: "z6",
    name: "Stadium Ring Road",
    area: "Ward 8",
    lat: 12.9624,
    lng: 77.5991,
    level: "Medium",
    riskPercent: 52,
    pedestrians: 121,
    vehicles: 480,
    factors: {
      trafficDensity: 77,
      pedestrianDensity: 42,
      roadConditions: 33,
      lighting: 38,
    },
    note: "Sample pattern: risk rises only on event evenings.",
  },
  {
    id: "z7",
    name: "Old Town Footbridge",
    area: "Ward 1",
    lat: 12.9895,
    lng: 77.5982,
    level: "Low",
    riskPercent: 28,
    pedestrians: 96,
    vehicles: 140,
    factors: {
      trafficDensity: 30,
      pedestrianDensity: 48,
      roadConditions: 22,
      lighting: 26,
    },
    note: "Sample pattern: most people use the footbridge.",
  },
  {
    id: "z8",
    name: "Library Park Edge",
    area: "Ward 7",
    lat: 12.9661,
    lng: 77.6122,
    level: "Low",
    riskPercent: 24,
    pedestrians: 84,
    vehicles: 110,
    factors: {
      trafficDensity: 26,
      pedestrianDensity: 39,
      roadConditions: 18,
      lighting: 21,
    },
    note: "Sample pattern: low vehicle speed and a marked crossing.",
  },
];

export const conflicts = [
  {
    id: "C-1048",
    date: "2026-11-05",
    time: "08:14",
    location: "Harbor School Crossing",
    area: "Ward 4",
    severity: "High",
    type: "Turning vehicle / pedestrian",
    summary: "Sample: a person is in the crossing while a vehicle turns across it.",
  },
  {
    id: "C-1047",
    date: "2026-11-05",
    time: "08:02",
    location: "Harbor School Crossing",
    area: "Ward 4",
    severity: "Medium",
    type: "Close passing",
    summary: "Sample: a vehicle passes close to people waiting at the curb.",
  },
  {
    id: "C-1044",
    date: "2026-11-05",
    time: "07:41",
    location: "Riverside Bus Terminal",
    area: "Ward 6",
    severity: "High",
    type: "Bus exit conflict",
    summary: "Sample: pedestrians cross the bus exit during a departure.",
  },
  {
    id: "C-1039",
    date: "2026-11-04",
    time: "18:26",
    location: "Central Market Junction",
    area: "Ward 2",
    severity: "High",
    type: "Mid-block crossing",
    summary: "Sample: a group crosses between slow-moving vehicles.",
  },
  {
    id: "C-1036",
    date: "2026-11-04",
    time: "18:11",
    location: "Oak Avenue Metro Exit",
    area: "Ward 3",
    severity: "Medium",
    type: "Crowd spillover",
    summary: "Sample: the exit crowd reaches the roadway edge.",
  },
  {
    id: "C-1031",
    date: "2026-11-04",
    time: "13:05",
    location: "Civic Hospital Approach",
    area: "Ward 5",
    severity: "Medium",
    type: "Slow crossing",
    summary: "Sample: a slow crossing overlaps with a vehicle approach.",
  },
  {
    id: "C-1028",
    date: "2026-11-03",
    time: "21:18",
    location: "Stadium Ring Road",
    area: "Ward 8",
    severity: "Low",
    type: "Event-night crossing",
    summary: "Sample: extra foot traffic at a signalized crossing.",
  },
  {
    id: "C-1022",
    date: "2026-11-03",
    time: "09:47",
    location: "Central Market Junction",
    area: "Ward 2",
    severity: "High",
    type: "Unmarked crossing",
    summary: "Sample: people cross away from the marked lines.",
  },
  {
    id: "C-1018",
    date: "2026-11-02",
    time: "17:33",
    location: "Riverside Bus Terminal",
    area: "Ward 6",
    severity: "Medium",
    type: "Curbside conflict",
    summary: "Sample: boarding passengers step out as a car pulls in.",
  },
  {
    id: "C-1014",
    date: "2026-11-02",
    time: "08:22",
    location: "Harbor School Crossing",
    area: "Ward 4",
    severity: "Low",
    type: "Yield delay",
    summary: "Sample: vehicles stop late but do stop.",
  },
  {
    id: "C-1009",
    date: "2026-11-01",
    time: "19:02",
    location: "Oak Avenue Metro Exit",
    area: "Ward 3",
    severity: "Low",
    type: "Lighting concern",
    summary: "Sample: dim corner flagged with a low-severity note.",
  },
  {
    id: "C-1004",
    date: "2026-10-31",
    time: "16:40",
    location: "Civic Hospital Approach",
    area: "Ward 5",
    severity: "Medium",
    type: "Turning vehicle / pedestrian",
    summary: "Sample: a turning vehicle meets a person leaving the gate.",
  },
];

export const dailyActivity = [
  { day: "Mon", pedestrians: 1180, conflicts: 2 },
  { day: "Tue", pedestrians: 1264, conflicts: 3 },
  { day: "Wed", pedestrians: 1210, conflicts: 1 },
  { day: "Thu", pedestrians: 1396, conflicts: 4 },
  { day: "Fri", pedestrians: 1486, conflicts: 3 },
  { day: "Sat", pedestrians: 980, conflicts: 2 },
  { day: "Sun", pedestrians: 760, conflicts: 1 },
];

export const weeklyActivity = [
  { day: "Week 1", pedestrians: 7420, conflicts: 9 },
  { day: "Week 2", pedestrians: 8010, conflicts: 12 },
  { day: "Week 3", pedestrians: 7760, conflicts: 11 },
  { day: "Week 4", pedestrians: 8276, conflicts: 14 },
];

export const hourlyMovement = [
  { hour: "06", people: 40 },
  { hour: "07", people: 120 },
  { hour: "08", people: 260 },
  { hour: "09", people: 180 },
  { hour: "12", people: 150 },
  { hour: "16", people: 170 },
  { hour: "18", people: 290 },
  { hour: "20", people: 110 },
];

export const safetyScore = 72;

export function riskCounts(items = zones) {
  return ["High", "Medium", "Low"].map((level) => ({
    level,
    count: items.filter((item) => item.level === level).length,
  }));
}

export const summary = {
  pedestrianCount: zones.reduce((total, zone) => total + zone.pedestrians, 0),
  conflicts: conflicts.length,
  highRiskZones: zones.filter((zone) => zone.level === "High").length,
  safetyScore,
  status: "Sample status: standby",
};

export const features = [
  {
    title: "Safety dashboard",
    text: "See pedestrian volume, potential conflicts, high-risk zones, and a sample safety score in one view.",
  },
  {
    title: "Zone risk map",
    text: "Color zones so a reviewer can compare high, medium, and low risk without reading a spreadsheet.",
  },
  {
    title: "Conflict log",
    text: "List potential pedestrian–vehicle conflicts with time, place, and severity for the demo story.",
  },
  {
    title: "Risk factors",
    text: "Show how traffic, people, road condition, and lighting contribute in the sample records.",
  },
  {
    title: "Analytics",
    text: "Compare daily and weekly movement, traffic density, and zone risk with simple charts.",
  },
  {
    title: "Ready for live data",
    text: "Screens read one shared data shape so a later API can replace the sample file.",
  },
];

export const workflow = [
  { step: "01", title: "Observe the street", text: "A traffic video or sensor feed is the planned input. This demo does not upload a live video yet." },
  { step: "02", title: "Detect and track", text: "The vision module is planned to find pedestrians and vehicles and keep an identity for each one." },
  { step: "03", title: "Flag potential conflicts", text: "The risk module looks for movements that could conflict. It does not claim an accident will happen." },
  { step: "04", title: "Explain the zone", text: "Results return counts, a risk level, alerts, and the factors behind the sample score." },
  { step: "05", title: "Show it clearly", text: "This website turns those fields into cards, a map, a table, and charts." },
];

export const benefits = [
  "Gives a city team one place to review pedestrian safety instead of separate clips and sheets.",
  "Makes high-risk crossings easy to spot during a demonstration.",
  "Keeps language careful: potential conflict, not a guaranteed accident.",
  "Leaves a clean path for the backend and model teams to connect later.",
];

export const team = [
  { role: "Member 1", focus: "Frontend and user interface", detail: "Screens, navigation, charts, and the map in this demo." },
  { role: "Member 2", focus: "Backend and APIs", detail: "Planned upload, processing status, and result routes." },
  { role: "Member 3", focus: "Detection and tracking", detail: "Planned pedestrian and vehicle detection with tracking." },
  { role: "Member 4", focus: "Risk analysis", detail: "Planned conflict rules and Low / Medium / High scoring." },
];

export const technologies = [
  { group: "This website", items: ["React", "Vite", "Tailwind CSS", "Recharts", "Leaflet / OpenStreetMap"] },
  { group: "Planned later", items: ["Python Flask", "SQLite", "OpenCV", "A pretrained detector", "JSON shared between modules"] },
];

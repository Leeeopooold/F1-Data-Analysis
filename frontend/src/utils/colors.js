// F1 2024 车手专属颜色及备用配色轮询

const DRIVER_COLORS = {
  // Red Bull Racing
  VER: "#3671C6",
  PER: "#1432CC",

  // Ferrari
  LEC: "#E8002D",
  SAI: "#900000",
  BEA: "#FF2800",

  // McLaren
  NOR: "#FF8000",
  PIA: "#FF9E24",

  // Mercedes
  HAM: "#27F4D2",
  RUS: "#00A19C",

  // Aston Martin
  ALO: "#2293D1",
  STR: "#005A49",

  // Alpine
  GAS: "#0093CC",
  OCO: "#FF66B2",

  // Williams
  ALB: "#64C4FF",
  SAR: "#00A0DE",
  COL: "#005AFF",

  // RB (Visa Cash App RB)
  TSU: "#6692FF",
  RIC: "#469BFF",
  LAW: "#3673F5",

  // Haas
  HUL: "#B6BABD",
  MAG: "#999999",

  // Kick Sauber
  BOT: "#52E252",
  ZHO: "#00E700",
};

const FALLBACK_PALETTE = [
  "#E10600",
  "#00D2BE",
  "#FF8700",
  "#2B4562",
  "#52E252",
  "#FF66B2",
  "#64C4FF",
  "#FFD700",
  "#9932CC",
  "#00E5FF",
];

/**
 * 获取车手专属颜色。如果未预设，则基于名字 Hash 自动匹配告别纯白 fallback。
 */
export const getDriverColor = (driver) => {
  if (!driver) return "#FFFFFF";
  const code = driver.toUpperCase().trim();
  if (DRIVER_COLORS[code]) {
    return DRIVER_COLORS[code];
  }

  // 字符串 Hash，确定性衍生颜色，避免未知车手重名/纯白问题
  let hash = 0;
  for (let i = 0; i < code.length; i++) {
    hash = code.charCodeAt(i) + ((hash << 5) - hash);
  }
  const index = Math.abs(hash) % FALLBACK_PALETTE.length;
  return FALLBACK_PALETTE[index];
};

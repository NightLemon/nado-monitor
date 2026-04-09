/**
 * Convert a UTC datetime string to a local Date object.
 */
export function toDisplayTime(utcString: string): Date {
  return new Date(utcString.endsWith("Z") ? utcString : utcString + "Z");
}

/**
 * Format a UTC timestamp for short time display (HH:MM).
 */
export function formatTime(utcString: string, long = false): string {
  const d = toDisplayTime(utcString);
  if (long) {
    const month = d.toLocaleString("en", { month: "short" });
    const day = d.getDate();
    const h = d.getHours().toString().padStart(2, "0");
    const m = d.getMinutes().toString().padStart(2, "0");
    return `${month} ${day} ${h}:${m}`;
  }
  const h = d.getHours().toString().padStart(2, "0");
  const m = d.getMinutes().toString().padStart(2, "0");
  return `${h}:${m}`;
}

/**
 * Format a UTC timestamp for full datetime display.
 */
export function formatDateTime(utcString: string): string {
  const d = toDisplayTime(utcString);
  const y = d.getFullYear();
  const month = (d.getMonth() + 1).toString().padStart(2, "0");
  const day = d.getDate().toString().padStart(2, "0");
  const h = d.getHours().toString().padStart(2, "0");
  const m = d.getMinutes().toString().padStart(2, "0");
  const s = d.getSeconds().toString().padStart(2, "0");
  return `${y}-${month}-${day} ${h}:${m}:${s}`;
}

/**
 * Format an hour string from the token usage API (now in UTC).
 * Converts to local timezone for display.
 */
export function formatHourLabel(hourStr: string, hours: number): string {
  // hourStr is like "2026-04-08T19:00:00" — now in UTC, convert to local
  const d = toDisplayTime(hourStr);
  const h = d.getHours().toString().padStart(2, "0");
  const m = d.getMinutes().toString().padStart(2, "0");
  const time = `${h}:${m}`;
  if (hours <= 24) return time;
  const monthNames = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
  ];
  return `${monthNames[d.getMonth()]} ${d.getDate()} ${time}`;
}

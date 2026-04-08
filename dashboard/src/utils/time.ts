let cachedOffset: number | null = null;

export async function fetchTimezoneOffset(): Promise<number> {
  if (cachedOffset !== null) return cachedOffset;
  try {
    const res = await fetch(
      (import.meta.env.VITE_API_BASE_URL || "/api") + "/config/public",
    );
    const data = await res.json();
    cachedOffset = (data.timezone_offset as number) ?? 8;
  } catch {
    cachedOffset = 8; // fallback
  }
  return cachedOffset;
}

export function getTimezoneOffset(): number {
  return cachedOffset ?? 8;
}

/**
 * Convert a UTC datetime string to display timezone.
 * Returns a Date object shifted by the configured offset.
 */
export function toDisplayTime(utcString: string): Date {
  const d = new Date(
    utcString.endsWith("Z") ? utcString : utcString + "Z",
  );
  const offset = getTimezoneOffset();
  return new Date(d.getTime() + offset * 3600_000);
}

/**
 * Format a UTC timestamp for short time display (HH:MM).
 */
export function formatTime(utcString: string, long = false): string {
  const d = toDisplayTime(utcString);
  if (long) {
    const month = d.toLocaleString("en", { month: "short", timeZone: "UTC" });
    const day = d.getUTCDate();
    const h = d.getUTCHours().toString().padStart(2, "0");
    const m = d.getUTCMinutes().toString().padStart(2, "0");
    return `${month} ${day} ${h}:${m}`;
  }
  const h = d.getUTCHours().toString().padStart(2, "0");
  const m = d.getUTCMinutes().toString().padStart(2, "0");
  return `${h}:${m}`;
}

/**
 * Format a UTC timestamp for full datetime display.
 */
export function formatDateTime(utcString: string): string {
  const d = toDisplayTime(utcString);
  const y = d.getUTCFullYear();
  const month = (d.getUTCMonth() + 1).toString().padStart(2, "0");
  const day = d.getUTCDate().toString().padStart(2, "0");
  const h = d.getUTCHours().toString().padStart(2, "0");
  const m = d.getUTCMinutes().toString().padStart(2, "0");
  const s = d.getUTCSeconds().toString().padStart(2, "0");
  return `${y}-${month}-${day} ${h}:${m}:${s}`;
}

/**
 * Format an hour string from the token usage API (already timezone-adjusted).
 * Just extract HH:00 from the string directly.
 */
export function formatHourLabel(hourStr: string, hours: number): string {
  // hourStr is like "2026-04-08T19:00:00" — already in display timezone
  const parts = hourStr.split("T");
  if (parts.length < 2) return hourStr;
  const time = parts[1].substring(0, 5); // "19:00"
  if (hours <= 24) return time;
  const dateParts = parts[0].split("-");
  const month = parseInt(dateParts[1]);
  const day = parseInt(dateParts[2]);
  const monthNames = [
    "", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
  ];
  return `${monthNames[month]} ${day} ${time}`;
}

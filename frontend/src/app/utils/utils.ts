// utils.ts

export function parseArrayOrNull(s: string | null | undefined): (number | null)[] {
  if (!s) return [];
  try {
    const a = JSON.parse(s);
    if (!Array.isArray(a)) return [];
    return a.map((v: unknown) =>
      v === null ? null : Number.isFinite(v as number) ? (v as number) : null
    );
  } catch {
    return [];
  }
}

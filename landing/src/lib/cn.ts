type ClassValue = string | number | boolean | null | undefined | ClassValue[];

function flatten(values: ClassValue[], out: string[]): string[] {
  for (const value of values) {
    if (!value) continue;
    if (Array.isArray(value)) flatten(value, out);
    else if (typeof value === 'string' || typeof value === 'number') out.push(String(value));
  }
  return out;
}

export function cn(...inputs: ClassValue[]): string {
  return flatten(inputs, []).join(' ');
}

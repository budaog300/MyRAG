import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}


export const formatDate = (value: string): string => {
  const dt = new Date(value);
  return dt.toLocaleString();
};


export const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} Б`;

  const kb = bytes / 1024;
  if (kb < 1024) return `${kb.toFixed(2)} КБ`;

  const mb = kb / 1024;
  if (mb < 1024) return `${mb.toFixed(2)} МБ`;

  const gb = mb / 1024;
  return `${gb.toFixed(2)} ГБ`;
}


export const pluralize = (
  count: number,
  one: string,
  few: string,
  many: string,
): string => {
  const mod10 = count % 10;
  const mod100 = count % 100;

  if (mod10 === 1 && mod100 !== 11) {
    return one;
  }

  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) {
    return few;
  }

  return many;
};

import { validationMessages } from '../data/contact';
import type { ContactFormData, ContactFormErrors } from '../types/contact';

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

export function validateContactField(
  field: keyof ContactFormData,
  value: string,
): string | undefined {
  const trimmed = value.trim();

  switch (field) {
    case 'name':
      if (!trimmed) return validationMessages.nameRequired;
      if (trimmed.length < 2) return validationMessages.nameTooShort;
      return undefined;
    case 'email':
      if (!trimmed) return validationMessages.emailRequired;
      if (!EMAIL_RE.test(trimmed)) return validationMessages.emailInvalid;
      return undefined;
    case 'message':
      if (!trimmed) return validationMessages.messageRequired;
      if (trimmed.length < 10) return validationMessages.messageTooShort;
      return undefined;
    default:
      return undefined;
  }
}

export function validateContactForm(values: ContactFormData): ContactFormErrors {
  const errors: ContactFormErrors = {};
  for (const field of ['name', 'email', 'message'] as const) {
    const error = validateContactField(field, values[field]);
    if (error) errors[field] = error;
  }
  return errors;
}

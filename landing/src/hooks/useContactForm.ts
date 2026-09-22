import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { submitContactForm } from '../api/contact';
import { validationMessages } from '../data/contact';
import { validateContactField, validateContactForm } from '../lib/validation';
import type { ApiError, ContactFormData, ContactFormErrors } from '../types/contact';

export type ContactFormStatus = 'idle' | 'submitting' | 'success' | 'error';

const EMPTY_VALUES: ContactFormData = { name: '', email: '', company: '', message: '' };

export function useContactForm() {
  const [values, setValues] = useState<ContactFormData>(EMPTY_VALUES);
  const [errors, setErrors] = useState<ContactFormErrors>({});
  const [touched, setTouched] = useState<Partial<Record<keyof ContactFormData, boolean>>>({});
  const [status, setStatus] = useState<ContactFormStatus>('idle');
  const [apiError, setApiError] = useState<ApiError | undefined>(undefined);

  const valuesRef = useRef(values);
  useEffect(() => {
    valuesRef.current = values;
  }, [values]);

  const isValid = useMemo(() => Object.keys(validateContactForm(values)).length === 0, [values]);

  const setValue = useCallback((field: keyof ContactFormData, value: string) => {
    setValues((prev) => ({ ...prev, [field]: value }));
    setErrors((prev) => {
      if (!prev[field]) return prev;
      const next = { ...prev };
      delete next[field];
      return next;
    });
  }, []);

  const blurField = useCallback((field: keyof ContactFormData) => {
    setTouched((prev) => ({ ...prev, [field]: true }));
    const error = validateContactField(field, valuesRef.current[field]);
    setErrors((prev) => (error ? { ...prev, [field]: error } : prev));
  }, []);

  const reset = useCallback(() => {
    setValues(EMPTY_VALUES);
    setErrors({});
    setTouched({});
    setStatus('idle');
    setApiError(undefined);
  }, []);

  const submit = useCallback(async () => {
    const nextErrors = validateContactForm(valuesRef.current);
    setErrors(nextErrors);
    setTouched({ name: true, email: true, company: true, message: true });
    if (Object.keys(nextErrors).length > 0) return;

    setStatus('submitting');
    setApiError(undefined);
    try {
      const result = await submitContactForm({
        name: valuesRef.current.name.trim(),
        email: valuesRef.current.email.trim(),
        company: valuesRef.current.company.trim(),
        message: valuesRef.current.message.trim(),
      });
      setStatus(result.success ? 'success' : 'error');
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : validationMessages.genericError;
      setApiError({ message });
      setStatus('error');
    }
  }, []);

  return {
    values,
    errors,
    touched,
    status,
    apiError,
    isValid,
    setValue,
    blurField,
    submit,
    reset,
  };
}

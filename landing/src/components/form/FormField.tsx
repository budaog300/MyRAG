import type { InputHTMLAttributes, TextareaHTMLAttributes } from 'react';
import { AlertCircle } from 'lucide-react';
import { cn } from '../../lib/cn';

type BaseFieldProps = {
  id: string;
  label: string;
  optionalLabel?: string;
  error?: string;
};

type InputFieldProps = BaseFieldProps & InputHTMLAttributes<HTMLInputElement> & { multiline?: false };
type TextareaFieldProps = BaseFieldProps & TextareaHTMLAttributes<HTMLTextAreaElement> & { multiline: true };

export type FormFieldProps = InputFieldProps | TextareaFieldProps;

const controlClasses =
  'w-full rounded-xl border bg-white px-4 py-3 text-sm text-slate-900 placeholder:text-slate-400 transition-colors duration-200 focus:outline-none';

function errorClasses(hasError: boolean): string {
  return hasError
    ? 'border-red-400 focus:border-red-500'
    : 'border-slate-200 focus:border-accent-500';
}

export function FormField(props: FormFieldProps) {
  const { id, label, optionalLabel, error, multiline, className, ...rest } = props;
  const describedBy = error ? `${id}-error` : undefined;

  return (
    <div className={cn('min-w-0', className)}>
      <label htmlFor={id} className="flex items-baseline justify-between text-sm font-medium text-slate-800">
        <span>{label}</span>
        {optionalLabel ? <span className="text-xs font-normal text-slate-400">{optionalLabel}</span> : null}
      </label>
      {multiline ? (
        <textarea
          id={id}
          aria-invalid={Boolean(error)}
          aria-describedby={describedBy}
          className={cn(controlClasses, errorClasses(Boolean(error)), 'mt-2 min-h-32 resize-y')}
          {...(rest as TextareaHTMLAttributes<HTMLTextAreaElement>)}
        />
      ) : (
        <input
          id={id}
          aria-invalid={Boolean(error)}
          aria-describedby={describedBy}
          className={cn(controlClasses, errorClasses(Boolean(error)), 'mt-2')}
          {...(rest as InputHTMLAttributes<HTMLInputElement>)}
        />
      )}
      {error ? (
        <p id={`${id}-error`} role="alert" className="mt-1.5 flex items-center gap-1.5 text-xs font-medium text-red-600">
          <AlertCircle className="h-3.5 w-3.5 shrink-0" aria-hidden="true" />
          {error}
        </p>
      ) : null}
    </div>
  );
}

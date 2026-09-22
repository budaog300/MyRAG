import { CircleCheck, LoaderCircle, TriangleAlert } from 'lucide-react';
import { contactFormCopy } from '../../data/contact';
import { useContactForm } from '../../hooks/useContactForm';
import { Button } from '../ui/Button';
import { FormField } from './FormField';

/**
 * Форма заявки. Отправка инкапсулирована в useContactForm → api/contact → axios.
 * Внутри компонента нет ни axios, ни текстов: только props-разметка и данные хука.
 */
export function ContactForm() {
  const { values, errors, touched, status, setValue, blurField, submit, reset } =
    useContactForm();

  const isSubmitting = status === 'submitting';

  if (status === 'success') {
    return (
      <div
        role="status"
        className="demo-in flex flex-col items-start rounded-2xl border border-accent-200 bg-accent-50 p-6 sm:p-8"
      >
        <span className="flex h-11 w-11 items-center justify-center rounded-full bg-accent-600 text-white">
          <CircleCheck className="h-5 w-5" aria-hidden="true" />
        </span>
        <h3 className="mt-4 text-lg font-semibold text-slate-900">{contactFormCopy.successTitle}</h3>
        <p className="mt-2 text-sm leading-relaxed text-slate-600">
          {contactFormCopy.successDescription}
        </p>
        <Button variant="secondary" className="mt-6" onClick={reset}>
          {contactFormCopy.successResetLabel}
        </Button>
      </div>
    );
  }

  return (
    <form
      noValidate
      onSubmit={(event) => {
        event.preventDefault();
        void submit();
      }}
      className="rounded-2xl border border-slate-200 bg-white p-5 shadow-[0_18px_50px_-30px_rgba(10,17,32,0.25)] sm:p-8"
    >
      <fieldset disabled={isSubmitting} className="space-y-5">
        <div className="grid gap-5 sm:grid-cols-2">
          <FormField
            id="contact-name"
            label={contactFormCopy.nameLabel}
            value={values.name}
            placeholder={contactFormCopy.namePlaceholder}
            autoComplete="name"
            onChange={(event) => setValue('name', event.target.value)}
            onBlur={() => blurField('name')}
            error={touched.name ? errors.name : undefined}
          />
          <FormField
            id="contact-email"
            type="email"
            label={contactFormCopy.emailLabel}
            value={values.email}
            placeholder={contactFormCopy.emailPlaceholder}
            autoComplete="email"
            onChange={(event) => setValue('email', event.target.value)}
            onBlur={() => blurField('email')}
            error={touched.email ? errors.email : undefined}
          />
        </div>

        <FormField
          id="contact-company"
          label={contactFormCopy.companyLabel}
          value={values.company}
          placeholder={contactFormCopy.companyPlaceholder}
          autoComplete="organization"
          onChange={(event) => setValue('company', event.target.value)}
          onBlur={() => blurField('company')}
        />

        <FormField
          id="contact-message"
          multiline
          label={contactFormCopy.messageLabel}
          value={values.message}
          placeholder={contactFormCopy.messagePlaceholder}
          rows={5}
          onChange={(event) => setValue('message', event.target.value)}
          onBlur={() => blurField('message')}
          error={touched.message ? errors.message : undefined}
        />
      </fieldset>

      {status === 'error' ? (
        <div
          role="alert"
          className="mt-5 flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4"
        >
          <TriangleAlert className="mt-0.5 h-4 w-4 shrink-0 text-red-600" aria-hidden="true" />
          <div>
            <p className="text-sm font-semibold text-red-800">{contactFormCopy.errorTitle}</p>
            <p className="mt-1 text-xs leading-relaxed text-red-700">
              {contactFormCopy.errorDescription}
            </p>
          </div>
        </div>
      ) : null}

      <div className="mt-6">
        <Button
          type="submit"
          size="lg"
          className="w-full sm:w-auto sm:min-w-48"
          disabled={isSubmitting}
          aria-busy={isSubmitting}
        >
          {isSubmitting ? (
            <>
              <LoaderCircle className="h-4 w-4 animate-spin" aria-hidden="true" />
              {contactFormCopy.submittingLabel}
            </>
          ) : (
            contactFormCopy.submitLabel
          )}
        </Button>
      </div>
    </form>
  );
}

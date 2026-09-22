export type ContactFormData = {
  name: string;
  email: string;
  company: string;
  message: string;
};

export type ContactFormErrors = Partial<Record<keyof ContactFormData, string>>;

export type ApiError = {
  message: string;
  details?: string;
};

export type ContactFormResponse = {
  success: boolean;
  message: string;
};

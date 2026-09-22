import axios from 'axios';
import { apiClient } from './client';
import type { ContactFormData, ContactFormResponse } from '../types/contact';

export async function submitContactForm(data: ContactFormData): Promise<ContactFormResponse> {
  try {
    const response = await apiClient.post<ContactFormResponse>('/contact', data);
    return response.data;
  } catch (error: unknown) {
    if (axios.isAxiosError(error) && error.response?.data?.message) {
      throw new Error(String(error.response.data.message));
    }
    throw error;
  }
}

import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';

export interface LoginParams {
  email: string;
  password: string;
}

export interface RegisterParams {
  email: string;
  password: string;
  full_name: string;
  role: 'patient' | 'doctor';
}

export interface AuthResponse {
  access_token?: string;
  role?: string;
  message?: string;
}

export const loginUser = async (params: LoginParams): Promise<AuthResponse> => {
  const response = await axios.post<AuthResponse>(`${API_BASE_URL}/auth/login`, params);
  return response.data;
};

export const registerUser = async (params: RegisterParams): Promise<AuthResponse> => {
  const response = await axios.post<AuthResponse>(`${API_BASE_URL}/auth/register`, params);
  return response.data;
};

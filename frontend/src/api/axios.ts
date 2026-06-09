import axios, { AxiosInstance } from 'axios';

const setupInterceptors = (instance: AxiosInstance) => {
  instance.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });

  instance.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('userRole');
      }
      return Promise.reject(error);
    }
  );
};

const api = axios.create({
  baseURL: 'http://localhost:8000',
});

const authApi = axios.create({
  baseURL: 'http://localhost:8001',
});

setupInterceptors(api);
setupInterceptors(authApi);

export { authApi };
export default api;

/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import api, { authApi } from './axios';

describe('Axios Client', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
    // Mock window.location.href
    delete (window as any).location;
    window.location = { href: '' } as any;
  });

  describe('api instance', () => {
    it('should have correct baseURL', () => {
      expect(api.defaults.baseURL).toBe('http://localhost:8000');
    });

    it('should add Authorization header if token exists in localStorage', async () => {
      localStorage.setItem('token', 'test-token');
      
      const config: any = { headers: {} };
      // @ts-ignore - accessing internal interceptor handler
      const requestInterceptor = api.interceptors.request.handlers[0].fulfilled;
      
      const result = await requestInterceptor(config);
      expect(result.headers.Authorization).toBe('Bearer test-token');
    });

    it('should not add Authorization header if token does not exist', async () => {
      const config: any = { headers: {} };
      // @ts-ignore
      const requestInterceptor = api.interceptors.request.handlers[0].fulfilled;
      
      const result = await requestInterceptor(config);
      expect(result.headers.Authorization).toBeUndefined();
    });

    it('should handle 401 response and clear localStorage', async () => {
      // @ts-ignore
      const responseInterceptorError = api.interceptors.response.handlers[0].rejected;
      
      const error = {
        response: {
          status: 401
        }
      };

      localStorage.setItem('token', 'test-token');
      localStorage.setItem('userRole', 'admin');

      try {
        await responseInterceptorError(error);
      } catch (e) {
        // Expected to reject
      }

      expect(localStorage.getItem('token')).toBeNull();
      expect(localStorage.getItem('userRole')).toBeNull();
    });
  });

  describe('authApi instance', () => {
    it('should be defined', () => {
      expect(authApi).toBeDefined();
    });

    it('should have correct baseURL', () => {
      expect(authApi.defaults.baseURL).toBe('http://localhost:8001');
    });

    it('should add Authorization header if token exists in localStorage', async () => {
      localStorage.setItem('token', 'auth-test-token');
      
      const config: any = { headers: {} };
      // @ts-ignore
      const requestInterceptor = authApi.interceptors.request.handlers[0].fulfilled;
      
      const result = await requestInterceptor(config);
      expect(result.headers.Authorization).toBe('Bearer auth-test-token');
    });

    it('should handle 401 response and clear localStorage', async () => {
      // @ts-ignore
      const responseInterceptorError = authApi.interceptors.response.handlers[0].rejected;
      
      const error = {
        response: {
          status: 401
        }
      };

      localStorage.setItem('token', 'auth-token');

      try {
        await responseInterceptorError(error);
      } catch (e) {
        // Expected to reject
      }

      expect(localStorage.getItem('token')).toBeNull();
    });
  });
});

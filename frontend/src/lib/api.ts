// API Configuration
// IMPORTANT: Set NEXT_PUBLIC_API_URL environment variable
// - For local development: http://localhost:8000
// - For production (Vercel): Set in Vercel dashboard to your backend URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  // Health
  health: `${API_BASE_URL}/health`,
  root: `${API_BASE_URL}/`,
  
  // Auth
  register: `${API_BASE_URL}/api/v1/auth/register`,
  login: `${API_BASE_URL}/api/v1/auth/login`,
  
  // Phishing Detection
  analyzePhishing: `${API_BASE_URL}/api/v1/phishing/analyze`,
  
  // Deepfake Detection
  analyzeImageDeepfake: `${API_BASE_URL}/api/v1/deepfake/analyze-image`,
  analyzeVideoDeepfake: `${API_BASE_URL}/api/v1/deepfake/analyze-video`,
  
  // Test (No auth required)
  quickScan: `${API_BASE_URL}/api/v1/test/quick-scan`,
  testHealth: `${API_BASE_URL}/api/v1/test/health`,
};

// API Client
export class ApiClient {
  private baseURL: string;
  private token: string | null = null;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('auth_token');
    }
  }

  setToken(token: string) {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
  }

  clearToken() {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  }

  private async request(endpoint: string, options: RequestInit = {}) {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(endpoint, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Unknown error' }));
      throw new Error(error.message || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Auth Methods
  async register(email: string, password: string, fullName: string) {
    return this.request(API_ENDPOINTS.register, {
      method: 'POST',
      body: JSON.stringify({ email, password, full_name: fullName }),
    });
  }

  async login(email: string, password: string) {
    const response = await this.request(API_ENDPOINTS.login, {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    if (response.data?.access_token) {
      this.setToken(response.data.access_token);
    }
    return response;
  }

  // Quick Scan (No auth)
  async quickScan(url: string, content?: string) {
    return this.request(API_ENDPOINTS.quickScan, {
      method: 'POST',
      body: JSON.stringify({ url, content }),
    });
  }

  // Phishing Analysis (Requires auth)
  async analyzePhishing(url: string, content?: string, domain?: string) {
    return this.request(API_ENDPOINTS.analyzePhishing, {
      method: 'POST',
      body: JSON.stringify({ url, content, domain }),
    });
  }

  // Health Check
  async healthCheck() {
    return this.request(API_ENDPOINTS.health);
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

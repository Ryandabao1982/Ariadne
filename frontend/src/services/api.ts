// API client for Ariadne frontend

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Health check
  async healthCheck() {
    return this.request('/health');
  }

  // Research endpoints
  async searchResearch(query: any) {
    return this.request('/api/v1/research/search', {
      method: 'POST',
      body: JSON.stringify(query),
    });
  }

  async analyzeContent(content: any) {
    return this.request('/api/v1/research/analyze', {
      method: 'POST',
      body: JSON.stringify(content),
    });
  }

  // User endpoints
  async getUserProfile() {
    return this.request('/api/v1/users/profile');
  }

  async updateUserProfile(data: any) {
    return this.request('/api/v1/users/update', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Tapestry endpoints
  async listTapestries() {
    return this.request('/api/v1/tapestries/list');
  }

  async createTapestry(data: any) {
    return this.request('/api/v1/tapestries/create', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getTapestry(tapestryId: string) {
    return this.request(`/api/v1/tapestries/${tapestryId}`);
  }
}

export const apiClient = new ApiClient();
export default ApiClient;

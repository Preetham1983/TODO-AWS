/* =============================================================================
   ApiClient – Base HTTP client for all services.
   
   Centralised fetch wrapper with error handling.
   ============================================================================= */

const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

/**
 * Generic API client class used by all service modules.
 * Follows the Single Responsibility Principle – only handles HTTP.
 */
class ApiClient {
  constructor(basePath) {
    this.basePath = `${API_BASE}${basePath}`;
  }

  async request(path, options = {}) {
    const url = `${this.basePath}${path}`;
    const config = {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    };

    // Remove Content-Type for FormData (browser sets it with boundary)
    if (options.body instanceof FormData) {
      delete config.headers["Content-Type"];
    }

    const response = await fetch(url, config);

    if (!response.ok) {
      const errorBody = await response.json().catch(() => ({}));
      throw new Error(
        errorBody.detail || `HTTP ${response.status}: ${response.statusText}`
      );
    }

    // 204 No Content
    if (response.status === 204) {
      return null;
    }

    return response.json();
  }

  async get(path = "") {
    return this.request(path, { method: "GET" });
  }

  async post(path = "", body = {}) {
    return this.request(path, {
      method: "POST",
      body: JSON.stringify(body),
    });
  }

  async put(path = "", body = {}) {
    return this.request(path, {
      method: "PUT",
      body: JSON.stringify(body),
    });
  }

  async delete(path = "") {
    return this.request(path, { method: "DELETE" });
  }

  async postFormData(path = "", formData) {
    return this.request(path, {
      method: "POST",
      body: formData,
    });
  }
}

export default ApiClient;

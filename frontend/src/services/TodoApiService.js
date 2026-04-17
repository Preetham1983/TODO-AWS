/* =============================================================================
   TodoApiService – Communicates with the Todo microservice.
   ============================================================================= */

import ApiClient from "./ApiClient";

const client = new ApiClient("/api/v1/todos");

/**
 * Static service class for TODO CRUD operations.
 */
export class TodoApiService {
  static async getAll() {
    return client.get();
  }

  static async getById(id) {
    return client.get(`/${id}`);
  }

  static async search(query) {
    return client.get(`/search?q=${encodeURIComponent(query)}`);
  }

  static async create(payload) {
    return client.post("", payload);
  }

  static async update(id, payload) {
    return client.put(`/${id}`, payload);
  }

  static async delete(id) {
    return client.delete(`/${id}`);
  }

  static async addAttachment(todoId, attachmentId) {
    return client.post(`/${todoId}/attachments/${attachmentId}`);
  }

  static async removeAttachment(todoId, attachmentId) {
    return client.delete(`/${todoId}/attachments/${attachmentId}`);
  }
}

/* =============================================================================
   AttachmentApiService – Communicates with the Attachment microservice.
   ============================================================================= */

import ApiClient from "./ApiClient";

const client = new ApiClient("/api/v1/attachments");

/**
 * Static service class for attachment (S3) operations.
 */
export class AttachmentApiService {
  static async upload(todoId, file) {
    const formData = new FormData();
    formData.append("file", file);
    return client.postFormData(`/upload/${todoId}`, formData);
  }

  static async listForTodo(todoId) {
    return client.get(`/todo/${todoId}`);
  }

  static async getById(attachmentId) {
    return client.get(`/${attachmentId}`);
  }

  static async delete(attachmentId) {
    return client.delete(`/${attachmentId}`);
  }

  static getDownloadUrl(attachmentId) {
    const base = import.meta.env.VITE_API_BASE_URL || "";
    return `${base}/api/v1/attachments/${attachmentId}/download`;
  }
}

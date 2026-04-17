/* =============================================================================
   NotificationApiService – Communicates with the Notification microservice.
   ============================================================================= */

import ApiClient from "./ApiClient";

const client = new ApiClient("/api/v1/notifications");

/**
 * Static service class for notification (SES) operations.
 */
export class NotificationApiService {
  static async send(payload) {
    return client.post("/send", payload);
  }

  static async getAll() {
    return client.get();
  }

  static async getById(id) {
    return client.get(`/${id}`);
  }

  static async getVerifiedIdentities() {
    return client.get("/identities");
  }
}

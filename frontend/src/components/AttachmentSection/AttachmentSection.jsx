import React, { useState, useEffect, useCallback, useRef } from "react";
import { AttachmentApiService } from "../../services/AttachmentApiService";
import "./AttachmentSection.css";

/**
 * AttachmentSection – File upload/download panel per TODO.
 */
function AttachmentSection({ todoId }) {
  const [attachments, setAttachments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);

  const fetchAttachments = useCallback(async () => {
    try {
      const data = await AttachmentApiService.listForTodo(todoId);
      setAttachments(data.items || []);
    } catch (err) {
      console.error("Failed to fetch attachments", err);
    }
  }, [todoId]);

  useEffect(() => {
    fetchAttachments();
  }, [fetchAttachments]);

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setUploading(true);
      await AttachmentApiService.upload(todoId, file);
      await fetchAttachments();
    } catch (err) {
      console.error("Upload failed", err);
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleDelete = async (attachmentId) => {
    try {
      await AttachmentApiService.delete(attachmentId);
      setAttachments((prev) => prev.filter((a) => a.id !== attachmentId));
    } catch (err) {
      console.error("Delete failed", err);
    }
  };

  const formatSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1048576).toFixed(1)} MB`;
  };

  return (
    <div className="attachment-section">
      <div className="attachment-section__header">
        <h4>Attachments</h4>
        <label className="attachment-section__upload-btn">
          {uploading ? "Uploading…" : "＋ Upload"}
          <input
            ref={fileInputRef}
            type="file"
            onChange={handleUpload}
            disabled={uploading}
            hidden
          />
        </label>
      </div>

      {attachments.length === 0 ? (
        <p className="attachment-section__empty">No files attached</p>
      ) : (
        <ul className="attachment-section__list">
          {attachments.map((att) => (
            <li key={att.id} className="attachment-section__item">
              <div className="attachment-section__info">
                <span className="attachment-section__filename">{att.filename}</span>
                <span className="attachment-section__size">{formatSize(att.size_bytes)}</span>
              </div>
              <div className="attachment-section__item-actions">
                <a
                  href={AttachmentApiService.getDownloadUrl(att.id)}
                  className="attachment-section__download"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  ↓
                </a>
                <button
                  className="attachment-section__delete"
                  onClick={() => handleDelete(att.id)}
                >
                  ✕
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default AttachmentSection;

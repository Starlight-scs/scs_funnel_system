(function () {
  function getCsrfToken() {
    const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return csrfInput ? csrfInput.value : "";
  }

  function setText(node, value) {
    if (node) {
      node.textContent = value;
    }
  }

  async function parseJsonResponse(response) {
    const contentType = response.headers.get("content-type") || "";
    const text = await response.text();

    if (contentType.includes("application/json")) {
      try {
        return JSON.parse(text);
      } catch (_error) {
        return {
          error: "The server returned invalid JSON.",
          raw: text,
        };
      }
    }

    return {
      error: text.replace(/<[^>]*>/g, " ").replace(/\s+/g, " ").trim() || "The server returned an unexpected response.",
      raw: text,
    };
  }

  function initializeWidget(widget) {
    if (widget.dataset.initialized === "true") {
      return;
    }
    widget.dataset.initialized = "true";

    const fileInput = widget.querySelector(".ut-admin-widget__file-input");
    const uploadButton = widget.querySelector(".ut-admin-widget__upload-button");
    const deleteButton = widget.querySelector(".ut-admin-widget__delete-button");
    const fileName = widget.querySelector(".ut-admin-widget__file-name");
    const progress = widget.querySelector(".ut-admin-widget__progress");
    const progressFill = widget.querySelector(".ut-admin-widget__progress-fill");
    const progressValue = widget.querySelector(".ut-admin-widget__progress-value");
    const success = widget.querySelector(".ut-admin-widget__success");
    const error = widget.querySelector(".ut-admin-widget__error");
    const prepareUrl = widget.dataset.prepareUrl;
    const deleteUrl = widget.dataset.deleteUrl;
    const targetFieldName = widget.dataset.targetFieldName;

    const form = widget.closest("form");
    const scope =
      widget.closest("tr") ||
      widget.closest(".inline-related") ||
      widget.closest(".form-row") ||
      form;
    function findTargetField(searchRoot) {
      if (!searchRoot) {
        return null;
      }
      return Array.from(searchRoot.querySelectorAll("input, textarea, select")).find(function (field) {
        return field.name === targetFieldName || field.name.endsWith(`-${targetFieldName}`);
      }) || null;
    }

    const targetField = findTargetField(scope) || findTargetField(form);

    let activeRequest = null;

    function setProgress(percent) {
      const safePercent = Math.max(0, Math.min(100, percent));
      progress.hidden = false;
      progressFill.style.width = `${safePercent}%`;
      setText(progressValue, `${Math.round(safePercent)}%`);
    }

    function resetFeedback() {
      error.hidden = true;
      error.textContent = "";
      success.hidden = true;
      uploadButton.classList.remove("ut-admin-widget__upload-button--success");
      uploadButton.textContent = "Upload";
    }

    function syncDeleteButton() {
      deleteButton.disabled = !(targetField && targetField.value);
    }

    function clearWidgetState() {
      if (targetField) {
        targetField.value = "";
        targetField.dispatchEvent(new Event("change", { bubbles: true }));
      }
      fileInput.value = "";
      setText(fileName, "No file selected");
      progress.hidden = true;
      setProgress(0);
      resetFeedback();
      syncDeleteButton();
    }

    syncDeleteButton();

    fileInput.addEventListener("change", function () {
      const file = fileInput.files && fileInput.files[0];
      resetFeedback();
      setProgress(0);
      progress.hidden = true;

      if (!file) {
        setText(fileName, "No file selected");
        uploadButton.disabled = true;
        return;
      }

      setText(fileName, file.name);
      uploadButton.disabled = false;
    });

    window.addEventListener("beforeunload", function (event) {
      if (!activeRequest) {
        return;
      }
      event.preventDefault();
      event.returnValue = "";
    });

    uploadButton.addEventListener("click", async function () {
      const file = fileInput.files && fileInput.files[0];
      if (!file || !targetField) {
        return;
      }

      resetFeedback();
      uploadButton.disabled = true;
      fileInput.disabled = true;
      setProgress(0);

      try {
        const prepareResponse = await fetch(prepareUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCsrfToken(),
          },
          body: JSON.stringify({
            file_name: file.name,
            file_size: file.size,
            file_type: file.type || "video/mp4",
          }),
        });

        const preparePayload = await parseJsonResponse(prepareResponse);
        if (!prepareResponse.ok) {
          throw new Error(preparePayload.error || "Could not prepare the upload.");
        }

        const formData = new FormData();
        formData.append("file", file);

        const uploadUrl = preparePayload.upload_url;
        const publicUrl = preparePayload.public_url;
        const uploadVersion = preparePayload.version;

        await new Promise(function (resolve, reject) {
          const xhr = new XMLHttpRequest();
          activeRequest = xhr;
          xhr.open("PUT", uploadUrl, true);
          xhr.responseType = "json";
          xhr.setRequestHeader("Range", "bytes=0-");
          xhr.setRequestHeader("x-uploadthing-version", uploadVersion);

          xhr.upload.addEventListener("progress", function (event) {
            if (!event.lengthComputable || event.total === 0) {
              return;
            }
            setProgress((event.loaded / event.total) * 100);
          });

          xhr.addEventListener("load", function () {
            activeRequest = null;
            if (xhr.status >= 200 && xhr.status < 300) {
              resolve();
              return;
            }
            const responseMessage =
              xhr.response && xhr.response.message
                ? xhr.response.message
                : xhr.responseText || "Upload failed.";
            reject(new Error(responseMessage));
          });

          xhr.addEventListener("error", function () {
            activeRequest = null;
            reject(new Error("Network error during upload."));
          });

          xhr.addEventListener("abort", function () {
            activeRequest = null;
            reject(new Error("Upload was cancelled."));
          });

          xhr.send(formData);
        });

        if (!publicUrl) {
          throw new Error("Upload finished but no public URL was returned.");
        }

        targetField.value = publicUrl;
        targetField.dispatchEvent(new Event("change", { bubbles: true }));
        setProgress(100);
        success.hidden = false;
        uploadButton.classList.add("ut-admin-widget__upload-button--success");
        uploadButton.textContent = "Uploaded";
        syncDeleteButton();
      } catch (err) {
        error.hidden = false;
        error.textContent = err && err.message ? err.message : "Upload failed.";
        uploadButton.disabled = false;
      } finally {
        fileInput.disabled = false;
      }
    });

    deleteButton.addEventListener("click", async function () {
      if (!targetField || !targetField.value) {
        clearWidgetState();
        return;
      }

      resetFeedback();
      deleteButton.disabled = true;
      uploadButton.disabled = true;
      fileInput.disabled = true;

      try {
        const deleteResponse = await fetch(deleteUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCsrfToken(),
          },
          body: JSON.stringify({
            file_url: targetField.value,
          }),
        });

        const deletePayload = await parseJsonResponse(deleteResponse);
        if (!deleteResponse.ok) {
          throw new Error(deletePayload.error || "Could not delete the upload.");
        }

        clearWidgetState();
      } catch (err) {
        error.hidden = false;
        error.textContent = err && err.message ? err.message : "Delete failed.";
      } finally {
        fileInput.disabled = false;
        uploadButton.disabled = !fileInput.files || fileInput.files.length === 0;
        syncDeleteButton();
      }
    });
  }

  function initializeAll() {
    document.querySelectorAll(".ut-admin-widget").forEach(initializeWidget);
  }

  document.addEventListener("DOMContentLoaded", initializeAll);
})();

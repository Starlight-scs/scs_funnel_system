import base64
import json
import mimetypes
import os

import httpx


class UploadThingUploadError(Exception):
    """Raised when UploadThing upload preparation or transfer fails."""


UPLOADTHING_VERSION = "7.7.4"


def get_uploadthing_api_key():
    """Get the API key from UPLOADTHING_TOKEN."""
    token = os.getenv("UPLOADTHING_TOKEN")
    if not token:
        raise ValueError("UPLOADTHING_TOKEN environment variable is not set")

    try:
        decoded = base64.b64decode(token).decode("utf-8")
        token_data = json.loads(decoded)
        api_key = token_data.get("apiKey")
        if not api_key:
            raise ValueError("No apiKey found in token")
        return api_key
    except Exception as exc:
        raise ValueError(f"Failed to decode UPLOADTHING_TOKEN: {exc}") from exc


def _build_upload_headers(api_key):
    return {
        "x-uploadthing-api-key": api_key,
        "x-uploadthing-be-adapter": "django@1.0.0",
        "x-uploadthing-version": UPLOADTHING_VERSION,
        "Content-Type": "application/json",
    }


def _extract_presigned_payload(resp_json):
    if "data" in resp_json and isinstance(resp_json["data"], list):
        presigned = resp_json["data"][0]
    elif "data" in resp_json:
        presigned = resp_json["data"]
    else:
        presigned = resp_json

    upload_url = presigned.get("url")
    fields = presigned.get("fields", {})
    file_url = presigned.get("fileUrl")
    file_key = presigned.get("key")

    if not upload_url:
        raise UploadThingUploadError(f"No upload URL in response: {resp_json}")

    return upload_url, fields, file_url, file_key


def prepare_uploadthing_upload(file_name, file_size, mime_type=None):
    """Prepare a direct browser upload and return the presigned UploadThing payload."""
    api_key = get_uploadthing_api_key()
    resolved_mime_type = mime_type or mimetypes.guess_type(file_name)[0] or "video/mp4"

    payload = {
        "fileName": file_name,
        "fileSize": file_size,
        "fileType": resolved_mime_type,
        "contentDisposition": "inline",
        "acl": "public-read",
    }

    timeout = httpx.Timeout(connect=10.0, read=60.0, write=60.0, pool=10.0)

    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.post(
                "https://api.uploadthing.com/v7/prepareUpload",
                json=payload,
                headers=_build_upload_headers(api_key),
            )
            response.raise_for_status()
            upload_url, _fields, file_url, file_key = _extract_presigned_payload(response.json())
            return {
                "upload_url": upload_url,
                "file_url": file_url,
                "file_key": file_key,
                "public_url": file_url or (f"https://utfs.io/f/{file_key}" if file_key else ""),
                "version": UPLOADTHING_VERSION,
            }
    except httpx.TimeoutException as exc:
        raise UploadThingUploadError("Preparing the UploadThing upload timed out") from exc
    except httpx.HTTPStatusError as exc:
        raise UploadThingUploadError(
            f"UploadThing prepare request failed with status {exc.response.status_code}"
        ) from exc
    except httpx.HTTPError as exc:
        raise UploadThingUploadError(f"UploadThing network error: {exc}") from exc


def extract_uploadthing_file_key(file_url):
    """Extract the UploadThing file key from a public file URL."""
    if not file_url:
        return None

    marker = "/f/"
    if marker not in file_url:
        return None

    key = file_url.split(marker, 1)[1].split("?", 1)[0].strip("/")
    return key or None


def delete_uploadthing_file(file_url):
    """Delete an UploadThing file if the URL contains a file key."""
    file_key = extract_uploadthing_file_key(file_url)
    if not file_key:
        return False

    timeout = httpx.Timeout(connect=10.0, read=60.0, write=60.0, pool=10.0)

    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.post(
                "https://api.uploadthing.com/v6/deleteFiles",
                json={"fileKeys": [file_key]},
                headers=_build_upload_headers(get_uploadthing_api_key()),
            )
            response.raise_for_status()
            return True
    except httpx.TimeoutException as exc:
        raise UploadThingUploadError("Deleting the UploadThing file timed out") from exc
    except httpx.HTTPStatusError as exc:
        raise UploadThingUploadError(
            f"UploadThing delete request failed with status {exc.response.status_code}"
        ) from exc
    except httpx.HTTPError as exc:
        raise UploadThingUploadError(f"UploadThing network error: {exc}") from exc


def upload_to_uploadthing(file_content, file_name):
    """Upload file content to UploadThing and return the URL."""
    api_key = get_uploadthing_api_key()
    file_size = len(file_content)
    mime_type, _ = mimetypes.guess_type(file_name)
    if not mime_type:
        mime_type = "video/mp4"

    payload = {
        "fileName": file_name,
        "fileSize": file_size,
        "fileType": mime_type,
        "contentDisposition": "inline",
        "acl": "public-read",
    }

    timeout = httpx.Timeout(connect=10.0, read=60.0, write=300.0, pool=10.0)

    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.post(
                "https://api.uploadthing.com/v7/prepareUpload",
                json=payload,
                headers=_build_upload_headers(api_key),
            )
            response.raise_for_status()

            upload_url, fields, file_url, file_key = _extract_presigned_payload(response.json())

            upload_response = client.put(
                upload_url,
                files={"file": (file_name, file_content, mime_type)},
                headers={
                    "Range": "bytes=0-",
                    "x-uploadthing-version": UPLOADTHING_VERSION,
                },
            )

            if upload_response.status_code not in [200, 201, 204]:
                raise UploadThingUploadError(
                    f"UploadThing rejected the upload ({upload_response.status_code}): {upload_response.text}"
                )

            if file_url:
                return file_url
            if file_key:
                return f"https://utfs.io/f/{file_key}"

            raise UploadThingUploadError("UploadThing did not return a file URL or key")
    except httpx.TimeoutException as exc:
        raise UploadThingUploadError("Upload to UploadThing timed out") from exc
    except httpx.HTTPStatusError as exc:
        raise UploadThingUploadError(
            f"UploadThing request failed with status {exc.response.status_code}"
        ) from exc
    except httpx.HTTPError as exc:
        raise UploadThingUploadError(f"UploadThing network error: {exc}") from exc


def upload_file_path_to_uploadthing(file_path, file_name):
    """Upload a local file to UploadThing and return the public URL."""
    with open(file_path, "rb") as file_handle:
        return upload_to_uploadthing(file_handle.read(), file_name)

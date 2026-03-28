import os
import threading

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Branch, Campaign, VideoUploadState
from .upload_utils import UploadThingUploadError, upload_file_path_to_uploadthing


def _process_video_upload(model_class, instance_id, url_field_name):
    instance = model_class.objects.filter(pk=instance_id).first()
    if not instance or not instance.video_upload:
        return

    updated = model_class.objects.filter(
        pk=instance_id,
        video_upload_status=VideoUploadState.PENDING,
    ).update(
        video_upload_status=VideoUploadState.UPLOADING,
        video_upload_error="",
    )
    if not updated:
        return

    instance.refresh_from_db()
    stored_name = instance.video_upload.name
    file_path = instance.video_upload.path
    file_name = os.path.basename(stored_name)

    try:
        uploaded_url = upload_file_path_to_uploadthing(file_path, file_name)

        if instance.video_upload and instance.video_upload.name == stored_name:
            instance.video_upload.delete(save=False)

        model_class.objects.filter(pk=instance_id).update(
            **{
                url_field_name: uploaded_url,
                "video_upload": "",
                "video_upload_status": VideoUploadState.COMPLETE,
                "video_upload_error": "",
            }
        )
    except (UploadThingUploadError, OSError, ValueError) as exc:
        model_class.objects.filter(pk=instance_id).update(
            video_upload_status=VideoUploadState.FAILED,
            video_upload_error=str(exc),
        )


def _start_upload_worker(model_class, instance_id, url_field_name):
    worker = threading.Thread(
        target=_process_video_upload,
        args=(model_class, instance_id, url_field_name),
        daemon=True,
    )
    worker.start()


def _schedule_upload(instance, model_class, url_field_name):
    if not instance.pk or not instance.video_upload:
        return
    if instance.video_upload_status != VideoUploadState.PENDING:
        return

    transaction.on_commit(
        lambda: _start_upload_worker(model_class, instance.pk, url_field_name)
    )


@receiver(post_save, sender=Campaign)
def schedule_campaign_video_upload(sender, instance, **kwargs):
    _schedule_upload(instance, Campaign, "intro_video_url")


@receiver(post_save, sender=Branch)
def schedule_branch_video_upload(sender, instance, **kwargs):
    _schedule_upload(instance, Branch, "video_url")

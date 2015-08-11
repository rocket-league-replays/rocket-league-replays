from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver

from .models import ReplayPack


@receiver(pre_delete, sender=ReplayPack)
def replaypack_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.file.delete(False)

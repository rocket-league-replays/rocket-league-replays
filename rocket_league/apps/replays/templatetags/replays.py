from django import template

from ..models import Replay

register = template.Library()


@register.assignment_tag
def get_replay_by_pk(pk):
    try:
        return Replay.objects.get(pk=pk)
    except Replay.DoesNotExist:
        return None

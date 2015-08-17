from django import template

from ..models import Profile


register = template.Library()


@register.assignment_tag(takes_context=True)
def league_data(context):
    # Does this user have their Steam account connected?
    user = context.request.user

    if not user.is_authenticated():
        return

    try:
        assert user.profile
    except Exception as e:
        print e.__class__.__name__

        if e.__class__.__name__ == 'RelatedObjectDoesNotExist':
            Profile.objects.create(
                user=user
            )

    return user.profile.latest_ratings()

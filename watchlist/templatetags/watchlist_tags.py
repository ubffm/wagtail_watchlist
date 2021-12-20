from django import template
from django.db.models import Q

from ..models import Bookmark


register = template.Library()


@register.inclusion_tag('watchlist.html')
def get_watchlist(user):

    watchlist = Bookmark.objects.filter(user=user)

    return {'watchlist':watchlist}


@register.inclusion_tag('bookmark.html')
def bookmark(uri,page_id=None,user=None):

    if user is not None:
        if page_id is not None:
            q = Q(user=user) & Q(page__id=page_id) & Q(uri=uri)
        else:
            q = Q(user=user) & Q(uri=uri)

        try:
            bookmark_id = Bookmark.objects.get(q).id
        except Bookmark.DoesNotExist:
            bookmark_id = None

        return {'page_id':page_id,'uri':uri,'bookmark_id':bookmark_id}
    else:
        return {'page_id':page_id,'uri':uri,'bookmark_id':None}


@register.inclusion_tag('bookmark.html')
def bookmark_nopage(uri,user=None):

    if user is not None:
        q = Q(user=user) & Q(uri=uri)

        try:
            bookmark_id = Bookmark.objects.get(q).id
        except Bookmark.DoesNotExist:
            bookmark_id = None

        return {'uri':uri,'bookmark_id':bookmark_id}
    else:
        return {'uri':uri,'bookmark_id':None}

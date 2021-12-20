
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from io import BytesIO

from django.http import FileResponse

from watchlist.models import Bookmark

# replace Page-model for use in other Django-CMS'
from wagtail.core.models import Page

from watchlist import helpers

import json

# Create your views here.


@login_required
def add(request):

    if request.method == 'GET':
        page_id = request.GET.get('page',None)
        uri = request.GET.get('uri',None)

        if Bookmark.objects.filter(user=request.user).count() > 500:
            context = {'back':request.META.get('HTTP_REFERER')}
            return render(request,'watchlist_full.html',context)

        if page_id is not None:
            try:
                page = Page.objects.live().get(pk=page_id).specific

                if page.meta_data:
                    bookmark = Bookmark(user=request.user, page=page, uri=uri, keywords='',comments='')
                    bookmark.save()

            except Bookmark.DoesNotExist:
                pass
        else:
            # get external metadata and store them in bookmark
            bookmark = Bookmark(user=request.user, page=None, uri=uri, keywords='',comments='')
            bookmark.save()

    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def remove(request):

    if request.method == 'GET':
        bookmark_id = request.GET.get('bookmark_id')

        try:
            bookmark = Bookmark.objects.get(pk=bookmark_id, user=request.user)
            bookmark.delete()
        except Bookmark.DoesNotExist:
            pass

    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def update(request):

    if request.method == 'POST':
        bookmark_id = request.POST.get('bookmark_id')
        keywords = request.POST.get('keywords',None)
        comments = request.POST.get('comments',None)

        try:
            bookmark = Bookmark.objects.get(pk=bookmark_id, user=request.user)
            page = Page.objects.get(pk=bookmark.page.id).specific
            bookmark.meta_data = json.loads(page.get_metdata())
            bookmark.comments = comments
            bookmark.keywords = keywords

            bookmark.save()
        except Bookmark.DoesNotExist:
            pass

    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def export(request):
    '''
        TODO: Implement a function that iterates over the index for the watchlist, fetches the full record and rexports them in a given format
    '''
    export_format = request.GET.get('format',None)

    watchlist = Bookmark.objects.filter(user=request.user)

    export = ''

    if export_format == 'BibTex':
        for item in watchlist:
            meta_data = item.meta_data
            if item.meta_data.get('placePublishedVerbose') is not None:
                meta_data['placePublished'] = item.meta_data['placePublishedVerbose']
            if item.keywords:
                meta_data['keywords'] = item.keywords
            export = export + helpers.bibtex_export(meta_data) + '\n'
    if export_format == 'Endnote':
        for item in watchlist:
            meta_data = item.meta_data
            if item.meta_data.get('placePublishedVerbose') is not None:
                meta_data['placePublished'] = item.meta_data['placePublishedVerbose']
            if item.keywords:
                meta_data['keywords'] = item.keywords
            export = export + helpers.endnote_export(meta_data) + '\n'
    if export_format == 'RIS':
        for item in watchlist:
            meta_data = item.meta_data
            if item.meta_data.get('placePublishedVerbose') is not None:
                meta_data['placePublished'] = item.meta_data['placePublishedVerbose']
            if item.keywords:
                meta_data['keywords'] = item.keywords
            export = export + helpers.ris_export(meta_data) + '\n'

    if export_format == 'Endnote':
        f = BytesIO(bytes(export,encoding='utf-8'))
        return FileResponse(f,as_attachment=True,filename='watchlist.endnote')
    elif export_format == 'RIS':
        f = BytesIO(bytes(export,encoding='utf-8'))
        return FileResponse(f,as_attachment=True,filename='watchlist.ris')
    elif export_format == 'BibTex':
        f = BytesIO(bytes(export,encoding='utf-8'))
        return FileResponse(f,as_attachment=True,filename='watchlist.bib')

    return redirect(request.META.get('HTTP_REFERER'))

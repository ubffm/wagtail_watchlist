from django.db import models

from django.contrib.auth.models import User

from wagtail.core.models import Page
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel

from watchlist.settings import base as settings

from urllib.parse import urlencode

import requests

import json


# Create your models here.
class BookmarkablePageMixin(models.Model):
    author = models.CharField(max_length=255, default='African Studies Library')
    date = models.DateField("Post date")
    publisher = models.CharField(max_length=100, blank=False, default='African Studies Library')
    placePublished = models.URLField(blank=False, default="http://d-nb.info/gnd/4018118-2")
    placePublishedVerbose = models.CharField(max_length=150, blank=False, default="Frankfurt (M)")
    language = models.CharField(max_length=3, blank=False, default="und")  # maybe choice field!

    content_panels = [
        MultiFieldPanel([
            FieldPanel('author', heading='Author, please enter the authors full name here. Defaults to: African Studies Library'),
            FieldPanel('date', heading='Date of Publication'),
            FieldPanel('language', heading='Language the resource is primarily written in. Use 3-character language-code. Default: und'),
            FieldPanel('publisher', heading='Publisher Default: African Studies Library'),
            FieldPanel('placePublished', heading='Authority URI for the place of Publication. This is mandatory and needs to be a URL! Default GND-Identifier for Frankfurt (M)'),
            FieldPanel('placePublishedVerbose', heading='Human readable name of for the place of Publication.'),
        ], heading='Metadata'),
    ]

    @property
    def meta_data(self):

        return json.dumps({
            "uri": self.full_url,
            "author": [self.author],
            "title": [self.title],
            "language": [self.language],
            "publisher": [self.publisher],
            "placePublished": [self.placePublished],
            "placePublishedVerbose": [self.placePublishedVerbose],
            "datePublished": [self.date.year]
        })

    def save(self, *args, **kwargs):

        super(BookmarkablePageMixin, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class BookmarkablePage(BookmarkablePageMixin, Page):

    class Meta:
        abstract = True


class Bookmark(models.Model):

    # The user associated with a bookmark
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # URI of an external resource
    uri = models.URLField(blank=True)
    # Page in the portal that was bookmarked
    page = models.OneToOneField(Page, on_delete=models.CASCADE, blank=True, null=True)
    # user defined keywords
    keywords = models.TextField(blank=True, default=None)
    # user defined comments
    comments = models.TextField(blank=True, default=None)

    @property
    def meta_data(self):
        """
            return either a Page Model's metadata or metadata taken from the index Update Index part according to your index!!
        """

        # reminder: .specific returns the BookmarkablePage or Mixin!!
        if self.page:
            return json.loads(self.page.specific.meta_data)
        else:
            # get metadata from index
            # CHANGE ACCORDING TO YOUR INDEX!!
            # http://localhost:8983/solr/afsl/select?q=id%3ADE-101-01080000X
            params = {'q': f'id:{self.uri.split("record/")[-1]}'}
            query_string = f'http://{settings.index_url}:8983/solr/{settings.index_name}/select?{urlencode(params)}'

            meta_data = requests.get(query_string).json()['response']['docs'][0]

            if meta_data.get('placePublishedVerbose') is None and meta_data.get('placePublished', []) != []:
                meta_data['placePublishedVerbose'] = meta_data['placePublished']

            if meta_data.get('datePublished') is None and meta_data.get('datePublishedVerbose', []) != []:
                meta_data['datePublished'] = meta_data['datePublishedVerbose']

            return meta_data

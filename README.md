# wagtail_watchlist
This app allows you to make Wagtail CMS pages bookmarkable and handles bookmarks in a discovery system.

It was developed for the [Specialized Information Service African Studies (African Studies Library)](https://africanstudieslibrary.org) and is in use for their portal.
As such it was developed to be used in conjunction with a specific discovery system and [Apache Solr](https://solr.apache.org/) index. With minimal patching it will run on any [Wagtail CMS](https://wagtail.io) project, as well as any discovery System utilizing Wagtail CMS.

This app adds all necessary models, template tags and export logic to allow users to bookmark Wagtail CMS pages, as well as records displayed in a discovery system. Bookmarks can be exported as BibTeX, Endnote and RIS formatted files to be added to your reference managing tool of choice. It also allows the export of a full watchlist.

Since this app was somewhat tailored to the African Studies Library discovery system, it needs some adjustment before use in different contexts.

# Installation

Clone this repository and place the ```watchlist``` directory in your Wagtail CMS Project. 

Enable the app by adding it to your ```INSTALLED_APPS``` list in your project's settings like so:

```python
INSTALLED_APPS = [
    ...,
    'watchlist'
    ...,
]
``` 

After you made all necessary adjustments (see below), run ```python manage.py makemigrations``` to create all migrations and ```python manage.py migrate``` to apply them to your database.

# Adjustments and configuration

This app works on the principle that meta data is queried live from your database and/or Solr index. This avoids stale metadata in your bookmarks, but also makes some adjustments necessary, if your data model deviates from the one used for the African Studies Library. Possible points of adjustment are listed below.

## Basic settings
You find the basic settings in ```watchlist/settings/base.py```. These will be filled by reading your environment variables, but can be adjusted by hand. The hostname of your Solr index, and the name of the index itself can be adjusted here. The defaults are shown below. 

```python
index_url = getenv('INDEX_URL','localhost')
index_name = getenv('INDEX_NAME','afsl')
```

## Models

The models for the individual bookmarks contain some defaults, you might want to change. The metadata will be entered by your content editors, but for the sake of corporate identity, you will likely want to change the defaults provided herein. Models can be found in ```watchlist/models.py```.

The meta data is added as a Mixin for your your Wagtail CMS pages and contains all necessary fields that are not already provided by [Wagtail's page model](https://docs.wagtail.io/en/stable/topics/pages.html), the added data is shown below. Change the defaults here to your project's.

```python
author = models.CharField(max_length=255, default='African Studies Library')
date = models.DateField("Post date")
publisher = models.CharField(max_length=100, blank=False, default='African Studies Library')
placePublished = models.URLField(blank=False, default="http://d-nb.info/gnd/4018118-2")
placePublishedVerbose = models.CharField(max_length=150, blank=False, default="Frankfurt (M)")
language = models.CharField(max_length=3, blank=False, default="und")
```

Bear in mind that ```placePublished``` references an authority record for your place of publication.


### Meta Data from a Solr index

As mentioned, this app also handles bookmarks for non-Wagtail pages, like records in the African Studies Library's discovery system. You might want to change the logic necessary to work with your database or index. Do so by editing the ```metadata``` property of the ```BookMark``` class.

```python
@property
def meta_data(self):
    """
        return either a Page Model's metadata or metadata taken from the index Update Index part according to your index!!
    """

    if self.page:
        return json.loads(self.page.specific.meta_data)
    else:
        params = {'q': f'id:{self.uri.split("record/")[-1]}'}
        query_string = f'http://{settings.index_url}:8983/solr/{settings.index_name}/select?{urlencode(params)}'

        meta_data = requests.get(query_string).json()['response']['docs'][0]

        if meta_data.get('placePublishedVerbose') is None and meta_data.get('placePublished', []) != []:
            meta_data['placePublishedVerbose'] = meta_data['placePublished']

        if meta_data.get('datePublished') is None and meta_data.get('datePublishedVerbose', []) != []:
            meta_data['datePublished'] = meta_data['datePublishedVerbose']

        return meta_data
```

Change the code in the ```else``` branch to reflect your needs, or delete for use with Wagtail Pages only.
In our example, records have a URI in the form of ```https://domain.tld/record/record-id```, so the id can be extracted from there. In the next step, an index is queried to find the respective document and use the metadata contained therein. Apart from ```placePublished``` the watchlist meta data scheme matches the one shown below.

### Data model

All bookmarks use a fixed meta data scheme to allow for conversion into Endnote, RIS and BibTex reference management formats. This meta data scheme is defined in the ```BookmarkablePageMixin``` as a class property (see below).

```python
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
```

The exporters expect these fields to be present (for a full list of expected fields have a look at ```watchlist/helpers.py```)! Metadata taken from an index pertaining to a discovery system will surely be more extensive, but it needs to contain these fields, or needs to be mapped to them. As an example, see the schema of the African Studies Library Index below:

```json
{
    // FieldName : Explanation
    "author": "author of a work",
    "editor": "editor of a work",
    "contributor": "contributor to a work",
    "title": "title of a work",
    "subtitle": "subtitle of a work",
    "placePublished": "placePublished (authority record)",
    "placePublishedVerbose": "placePublishedVerbose (literal)",
    "publisher": "publisher of a work",
    "isbn":"isbn of a work",
    "issn":"issn of a work",
    "language":"language of a work",
    "subject":"subject headings of a work",
    "type":"type of a work",
    "datePublishedValue":"datePublishedValue (numerical representation of datePublished)",
    "datePublishedVerbose":"datePublishedVerbose (human readable representation of datePublished",
    "views":"URLs of where the document can be found",
}
```

If your Solr index has the same field names, you're good. If not, map them to the schema shown above for the exporters to work. You can do this in the code section shown above (Meta Data from a Solr index).

# Usage

After you've done all the necessary adjustments and ran migrations you can now use the template tags provided with this app to have a bookmark icon on your page.
The templates to change the appearance of this bookmark can be found in ```watchlist/templates```. All templates rely on Bootstrap 5.

## Bookmark symbol
We offer two tags for making a bookmark: One for usage with Wagtail CMS pages, and one for non-Wagtail pages. See the example below.

```jinja2
{% load watchlist_tags %}

<html>
    ...

    <body>
        ...

        {# Bookmark for a Wagtail Page #}

        {% if user.is_authenticated%}
            {% bookmark page.full_url page.id user %}
        {% else %}
            {% bookmark page.full_url page.id %}
        {% endif %}

        {# Bookmark for a non-Wagtail Page #}

        {% if user.is_authenticated%}
            {% bookmark_nopage document.uri user=user %}
        {% else %}
            {% bookmark_nopage document.uri %}
        {% endif %}

        ...
    </body>
</html>
```

Since Bookmarks are tied to a logged in user, they are wrapped in the if statement shown. This is done so that there's always an empty bookmark symbol rendered if no user is logged in. If a logged in user visits a page they have bookmarked, a filled in bookmark symbol will be rendered.

## The watchlist itself

A user's watchlist can be inserted in any template (preferably a profile page), that a logged in user can access. It's simply inserted as a template tag as well. See the example below:

```jinja2
{% load watchlist_tags %}

<html>
    ...

    <body>
        ...

        {# Place user's watchlist here #}
        {% get_watchlist user %}

        ...
    </body>
</html>
```

The watchlist will be rendered, where you put the template tag, including buttons for exports, and textfields for adding comments and keywords to your bookmarks.

## Watchlist full

A user can store a maximum of 500 records in their watchlist. This is done to avoid cluttering the database. If a user tries to store more than that a view displaying the ```watchlist_full``` template will be rendered.

If you want to have users store more than 500 records, simply change the number in the ```add``` function found in ```watchlist/views.py```.

# Environment

This app has been tested on:
- Python 3.8, 3.9, 3.10
- Wagtail 2.13, 2.14, 2.15
- Django 3.1, 3.2

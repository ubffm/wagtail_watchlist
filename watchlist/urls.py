### URLS will go here###
from django.urls import path
from watchlist import views

urlpatterns = [
    path('bookmark', views.add, name='bookmark'),
    path('unbookmark', views.remove, name='unbookmark'),
    path('update', views.update, name='watchlist_update'),
    path('export', views.export, name='watchlist_export'),
]
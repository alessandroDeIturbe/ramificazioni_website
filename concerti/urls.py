from django.urls import path

from . import views

app_name = "concerti"

urlpatterns = [
    path("", views.home, name="home"),
    path("events/", views.events_list, name="events_list"),
    path("events/<slug:slug>/", views.event_detail, name="event_detail"),
    path("about/", views.about, name="about"),
    path("contributors/", views.contributors, name="contributors"),
    path("archivio/", views.archivio, name="archivio"),
    path("archivio/edizioni/", views.archivio_edizioni, name="archivio_edizioni"),
    path("archivio/commissioni/", views.archivio_commissioni, name="archivio_commissioni"),
    path("archivio/compositori/", views.archivio_compositori, name="archivio_compositori"),
    path("archivio/interpreti/", views.archivio_interpreti, name="archivio_interpreti"),
    path("archivio/photo-gallery/", views.archivio_gallery, name="archivio_gallery"),
    path("contacts/", views.contacts, name="contacts"),
    path("privacy/", views.privacy, name="privacy"),
    path("impressum/", views.impressum, name="impressum"),
    path("sostenitori/", views.sostenitori, name="sostenitori"),
    path("stagioni/<path:stagione>/", views.stagione_detail, name="stagione_detail"),
]

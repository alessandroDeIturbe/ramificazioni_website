from django.urls import path

from . import views

app_name = "concerti"

urlpatterns = [
    path("", views.home, name="home"),
    path("events/", views.events_list, name="events_list"),
    path("events/<slug:slug>/", views.event_detail, name="event_detail"),
    path("about/", views.about, name="about"),
    path("contributors/", views.contributors, name="contributors"),
    path("contacts/", views.contacts, name="contacts"),
]

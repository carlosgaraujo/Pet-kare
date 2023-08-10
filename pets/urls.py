from django.urls import path

from .views import PetsDetailsView, PetsView

urlpatterns = [
    path("pets/", PetsView.as_view()),
    path("pets/<int:pet_id>/", PetsDetailsView.as_view()),
]

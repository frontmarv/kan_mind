from django.urls import include, path

urlpatterns = [
    path('', include('authentication.api.urls')),
    path('', include('boards.api.urls')),
    path('', include('tasks.api.urls')),
]

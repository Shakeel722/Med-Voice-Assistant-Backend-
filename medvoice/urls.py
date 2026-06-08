from django.contrib import admin
from django.urls import include, path
from django.http import JsonResponse

def root_view(request):
    return JsonResponse({'message': 'Med Voice Assistant backend is running.'})

urlpatterns = [
    path('', root_view),
    path('admin/', admin.site.urls),
    path('api/', include('bookings.urls')),
]

from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/login/', permanent=False)),
    # path('admin/', admin.site.urls),
    path('login/', include(('login.urls', 'login'), namespace='login')),
    path('your_bank/', include(('your_bank.urls', 'your_bank'), namespace='your_bank')),   
]

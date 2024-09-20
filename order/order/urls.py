"""
URL configuration for order project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path


from order_place.controllers import auth
from order_place.controllers import main
from order_place.controllers import api_update
from order_place.controllers import api_delete
from order_place.controllers import api_id_check
from order_place.controllers import api_order_check
from order_place.controllers import api_create
from order_place.controllers import upload
from order_place.controllers import check_table
from order_place.controllers import modal
from order_place.controllers import generate_xml
from django.conf.urls.static import static
from django.conf import settings



urlpatterns = [
    path('admin', admin.site.urls),
    path('order', main.order_page, name = 'order'),
    path('api/order/get/',api_id_check.check),
    path('api/order/check/',api_order_check.check),
    path('api/order/create',api_create.create),
    path('api/order/update',api_update.update),
    path('api/order/delete', api_delete.delete),
    path('logout',auth.user_logout),
    path('', auth.auth, name = 'auth'),
    # path('upload', upload.upload_file),
    path('test_paysera', upload.test_paysera),
    path('check_table', check_table.check_table),
    path('modal', modal.modal),
    path('xml', generate_xml.generate_xml),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

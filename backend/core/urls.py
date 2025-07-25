from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path, include

from rest_framework import permissions

from dj_rest_auth.app_settings import api_settings
from users.views import CustomLoginView, CustomTokenRefreshView, CustomTokenVerifyView, CustomPasswordChangeView, CustomLogoutView

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="LegalAPI",
        default_version="v1",
        description="API",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

admin.site.site_header = "ialegal Admin"
admin.site.site_title = "ialegal Admin Portal"
admin.site.index_title = "Bienvenido al portal de ialegal"

urlpatterns = [
    re_path('adminailegal/', admin.site.urls),
    re_path(r'login/?$', CustomLoginView.as_view(), name='rest_login'),
    re_path(r'logout/?$', CustomLogoutView.as_view(), name='rest_logout'),
    re_path(r'password/change/?$', CustomPasswordChangeView.as_view(), name='rest_password_change'),
    re_path("docs<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    re_path("docs/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    re_path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    re_path('users/v1/', include('users.urls')),
    re_path('companies/v1/', include('companies.urls')),
    re_path('documents/v1/', include('documents.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if api_settings.USE_JWT:
    from rest_framework_simplejwt.views import TokenVerifyView

    from dj_rest_auth.jwt_auth import get_refresh_view

    urlpatterns += [
        re_path(r'token/verify/?$', CustomTokenVerifyView.as_view(), name='token_verify'),
        re_path(r'token/refresh/?$', CustomTokenRefreshView.as_view(), name='token_refresh'),
    ]

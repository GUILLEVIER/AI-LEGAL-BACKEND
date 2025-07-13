from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path, include

from rest_framework import permissions

from dj_rest_auth.app_settings import api_settings
from dj_rest_auth.views import LoginView, LogoutView, PasswordChangeView, UserDetailsView

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

urlpatterns = [
    re_path('admin/', admin.site.urls),
    re_path(r'login/?$', LoginView.as_view(), name='rest_login'),
    re_path(r'logout/?$', LogoutView.as_view(), name='rest_logout'),
    #re_path(r'user/?$', UserDetailsView.as_view(), name='rest_user_details'),
    re_path(r'password/change/?$', PasswordChangeView.as_view(), name='rest_password_change'),
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
        re_path(r'token/verify/?$', TokenVerifyView.as_view(), name='token_verify'),
        re_path(r'token/refresh/?$', get_refresh_view().as_view(), name='token_refresh'),
    ]

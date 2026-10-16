from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def home(request):

    return JsonResponse(
        {
            "application":
            "Unique Bid API",

            "status":
            "running",

            "version":
            "1.0",

            "endpoints": {
                "health":
                "/api/health/",

                "products":
                "/api/products/",

                "auctions":
                "/api/auctions/",

                "auth":
                "/api/auth/",

                "admin":
                "/admin/",
            },
        }
    )


urlpatterns = [

    path(
        "",
        home,
        name="home",
    ),

    path(
        "admin/",
        admin.site.urls,
    ),

    path(
        "api/",
        include("core.urls"),
    ),

    path(
        "api/auth/",
        include("accounts.urls"),
    ),

    path(
        "api/products/",
        include("products.urls"),
    ),

    path(
        "api/",
        include("auctions.urls"),
    ),
    path(
        "api/wallet/",
        include("wallets.urls"),
    ),
]


if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
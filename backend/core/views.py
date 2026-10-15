from django.db import connection
from django.http import JsonResponse


def health_check(request):
    """
    Verify that both Django and PostgreSQL are operational.
    """

    database_status = "ok"

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            cursor.fetchone()

    except Exception:
        database_status = "error"

    status_code = 200 if database_status == "ok" else 503

    return JsonResponse(
        {
            "status": "ok" if database_status == "ok" else "error",
            "application": "Unique Bid API",
            "database": database_status,
        },
        status=status_code,
    )
# SomaSafe

Sistema informático de gestión de incidentes y seguridad para empresas del sector minero en Arequipa.

## Configuración local

El proyecto usa Django y SQLite. Para desarrollo puedes activar el modo debug con:

```powershell
$env:DJANGO_DEBUG='True'
python manage.py runserver
```

En producción define `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_DEBUG=False`,
`DJANGO_SECURE_SSL_REDIRECT=True`, `DJANGO_SESSION_COOKIE_SECURE=True` y
`DJANGO_CSRF_COOKIE_SECURE=True`.

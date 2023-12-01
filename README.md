# wymysorys-corpus-infrastructure

This is a Django App to host a corpus of Wymysorys language + data.

## Installation

1. Clone into the directory structure of a host Django site. The site should use the default auth User models. Rename the tope level directory to nwymc.

2. Pip install the requirements

3. Add `nwymc` and other required apps

``` python
INSTALLED_APPS = [
    # ...
    'nwymc.apps.NwymcConfig',
    'crispy_bootstrap4',
    'crispy_forms',
    'django_ace',
    'reversion',
    # ...
]
```

4. Add English and Polish to settings.py

```
LANGUAGES = [
    ('en', "English"),
    ('pl', "Polish")
]
```

5. Other settings

``` python
DATA_UPLOAD_MAX_MEMORY_SIZE = 262144000
CRISPY_TEMPLATE_PACK = 'bootstrap4'
```

6. Add  `media/` and `media/nwymc-assets/` directories at project root and the following settings.

``` python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```
7. Incorporate the following into the host app's main url file

``` python
from django.conf.urls.i18n import i18n_patterns
from nwymc.decorators import user_is_at_least_worker

@login_required
@user_is_at_least_worker
def protected_serve_nwymc(request, path, document_root=None, show_indexes=False):
    return serve(request, path, document_root, show_indexes)

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    # <existing/patterns>"
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    path('wymysorys-korpus/', include('nwymc.urls'))
)
```

9. MIDDLEWARE

``` python
'django.middleware.locale.LocaleMiddleware',
```
10. add the following to settings, under TEMPLATES>OPTIONS>context_processors
```
    'django.template.context_processors.i18n',
    'django.template.context_processors.media',
```
11. make migrations and migrate


12. run `createinitialrevisions`

13. compile translations

14. Configure server 

- serve `media/` to anyone
- serve `media/nwymc-assets/`, authenticate against Django database
- create superuser and other users if not already 
- assign some users some permission in the nywmc Permission model

15. (optional) populate DB with dump file

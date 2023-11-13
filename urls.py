from django.urls import path
from nwymc import views as nwymc_views

urlpatterns = [
    path('', nwymc_views.landing, name='nwymc-landing'),
    path('about/', nwymc_views.about, name='nwymc-about'),
    path('asset_overview/', nwymc_views.asset_overview, name='nwymc-asset-overview'),
    path('asset/<str:asset_pk>/', nwymc_views.asset_view, name='nwymc-asset-view'),
    path('author_overview/', nwymc_views.author_overview, name='nwymc-author-overview'),
    path('author/<str:author_pk>/', nwymc_views.author_view, name='nwymc-author-view'),
    path('document_overview/', nwymc_views.document_overview, name='nwymc-document-overview'),
    path('document_meta/<str:document_pk>/', nwymc_views.document_meta, name='nwymc-document-meta'),
    path('document_content/<str:document_pk>/', nwymc_views.document_content, name='nwymc-document-content'),
    path('document_markup/<str:document_pk>/', nwymc_views.document_markup, name='nwymc-document-markup'),
    path('markup_reference/', nwymc_views.markup_reference, name='nwymc-markup-reference'),
    path('search/', nwymc_views.search, name='nwymc-search')
]

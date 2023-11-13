from django.contrib import admin
from reversion.admin import VersionAdmin
from .models import *




class AuthorMetaAdmin(VersionAdmin):
    fields = [
        'DOB_y',
        'DOB_y_priv',
        'DOB_m',
        'DOB_m_priv',
        'DOB_d',
        'DOB_d_priv',
        'DOD_y',
        'DOD_y_priv',
        'DOD_m',
        'DOD_m_priv',
        'DOD_d',
        'DOD_d_priv',
        'dateadded',
        'author_names',
        'author_bios'
    ]
    readonly_fields = (
        'dateadded',
        'author_names',
        'author_bios'
    )
    list_display = [
        '__str__',
        'DOB_y'
    ]



    
class AuthorBioAdmin(VersionAdmin):
    fields = [
        'author',
        'language',
        'private',
        'bio'
    ]
    list_display = [
        'author',
        'language',
        'private'
    ]



    
class AuthorNameAdmin(VersionAdmin):
    fields = [
        'author',
        'surname',
        'firstname',
        'primary',
        'private'
    ]
    list_display = [
        'surname',
        'firstname',
        'primary',
        'private'
    ]




class ContributorAdmin(VersionAdmin):
    fields = [
        'name',
        'siteorid',
        'contributor_contributions'
    ]
    readonly_fields = ('contributor_contributions',)
    list_display = [ 
        'name',
        'siteorid'
    ]




class ContributionAdmin(VersionAdmin):
    fields = [
        'contributor',
        'start',
        'end',
        'title',
        'description',
    ]
    list_display = [
        'contributor',
        'title'
    ]




class DocumentCollectionAdmin(VersionAdmin):
    fields = [
        'name',
        'description',
        'collection_documents'
    ]
    readonly_fields = ('collection_documents',)
    list_display = [
        'name'
    ]




class DocumentAdmin(VersionAdmin):
    fields = [
        'title',
        'authors',
        'incollection',
        'prod_y',
        'prod_m',
        'prod_d',
        'document_descriptions',
        'manualdocid',
        'dateadded',
        'readyincorpus'
    ]
    readonly_fields = ('dateadded','document_descriptions')
    filter_horizontal = ('authors', )
    list_display = [
        'title',
        'authors_list',
        'manualdocid',
        'prod_y'
    ]




class DocumentExtraMetadataAdmin(VersionAdmin):
    fields = [
        'document',
        'publisher',
        'publisherlocation',
        'docid',
        'docidtype',
        'inpublication',
        'publicationvolume',
        'publicationissue',
        'pagerange',
        'url'
    ]
    list_display = [
        'document',
        'docid',
        'url'
    ]
    
class DocumentDescriptionAdmin(VersionAdmin):
    fields = [
        'document',
        'language',
        'description'
    ]
    list_display = [
        'document',
        'language'
    ]



    
class DocumentMarkupAdmin(VersionAdmin):
    fields = [
        'document',
        'canedit',
        'markup',
        'version',
        'id'        
    ]
    list_display = [
        'document',
        'canedit',
        'version',        
        'id'
    ]
    readonly_fields = ('id',)




class DocumentParagraphAdmin(VersionAdmin):
    fields = [
        'document',
        'order'
    ]
    list_display = [
        'document',
        'order'
    ]




class ParagraphFragmentAdmin(VersionAdmin):
    fields = [
        'paragraph',
        'order',
        'language',
        'text'
    ]
    list_display = [
        'paragraph',
        'order',
        'language',
        'text'
    ]

    


class MarginTextAdmin(VersionAdmin):
    fields = [
        'fragment',
        'location',
        'text'
    ]
    list_display = [
        'fragment',
        'location',
        'text'
    ]




class AssetAdmin(VersionAdmin):
    fields = [
        'file_instance',
        'filetype',
        'showonui',
        'order',
        'document',
        'uploader',
        'dateadded'
    ]
    readonly_fields = ('dateadded',)
    list_display = [
        'id',
        'file_instance',
        'filetype',
        'order',
        'uploader',
        'document'
    ]




class PermissionAdmin(VersionAdmin):
    fields = [
        'user',
        'level'
    ]
    list_display = [
        'user',
        'level'
    ]




admin.site.register(AuthorMeta, AuthorMetaAdmin)
admin.site.register(AuthorBio, AuthorBioAdmin)
admin.site.register(AuthorName, AuthorNameAdmin)
admin.site.register(Contributor, ContributorAdmin)
admin.site.register(Contribution, ContributionAdmin)
admin.site.register(DocumentCollection, DocumentCollectionAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(DocumentExtraMetadata, DocumentExtraMetadataAdmin)
admin.site.register(DocumentDescription, DocumentDescriptionAdmin)
admin.site.register(DocumentMarkup, DocumentMarkupAdmin)
admin.site.register(DocumentParagraph, DocumentParagraphAdmin)
admin.site.register(ParagraphFragment, ParagraphFragmentAdmin)
admin.site.register(MarginText, MarginTextAdmin)
admin.site.register(Asset, AssetAdmin)
admin.site.register(Permission, PermissionAdmin)

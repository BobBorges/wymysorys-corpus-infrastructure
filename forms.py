from django import forms
from django.utils.translation import gettext_lazy as _
from django_ace import AceWidget
from .models import Asset, DocumentMarkup, AuthorName, AuthorBio, Document, DocumentDescription, DocumentExtraMetadata
from .models import  LANGUAGE_OPTIONS_TWO as lang_opts




class UploadAssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            'file_instance',
            'filetype',
            'showonui'
        ]
        labels = {
            'file_instance': _("Select a file"),
            'filetype': _("Type"),
            'showonui': _("File will be publically viewable")
        }
        help_texts = {
            'filetype': _("Currently, text-type files are supported. Cooked text files like .doc and .ods are accepted but can't be displayed in the asset view. Admins might decide to convert such files to .pdf."),
            'showonui': _("If not selected, the asset will only be available to the site administrators.")
        }


    
class AssignAssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            'document',
            'order'
        ]
        labels = {
            'document': _("Document"),
            'order': _("Order of Assets in Document")
        }
        help_texts = {
            'document': _("The document instance must already be defined before an asset can be assigned. Go to the Documents page and create a document if a Document does not exist already for this asset."),
            'order': _("If a document has more than one associated assets, you can specify the order of assets here (it will be the sort order on the markup page, for instance).")
        }




class MarkdownForm(forms.ModelForm):
    class Meta:
        model = DocumentMarkup
        fields = [
            'version',
            'markup'
        ]
        widgets = {
            'markup': AceWidget(
                #mode="python",
                theme="twilight",
                height="690px",
                width="100%",
                toolbar=False,
                showgutter=True,
                wordwrap=True
            ),
            'version': forms.HiddenInput()
        }
        labels = {
            'markup': ''
        }
        exclude = ()


        

class AddAuthorForm(forms.Form):
    surname = forms.CharField(
        label = _("Surname"),
        required = True
    )
    firstname = forms.CharField(
        label = _("First name(s)"),
        required = True,
        help_text = _("Surname and First name(s) fields will become the newly created author's primary, publically visible alias.")
    )
    year_o_birth = forms.IntegerField(
        label = _("Author's Birth Year"),
        required = False,
        help_text = _("If entered, the author's birth year will be publically visible on the site.")
    )




class AddAuthorNameForm(forms.ModelForm):
    class Meta:
        model = AuthorName
        fields = [
            'surname',
            'firstname'
        ]
        labels = {
            'surename': _("Alternate Surname"),
            'firstname': _("Alternate First Name(s)")
        }
        help_texts = {
            'firstname': _("If only surname or first name(s) are alternate, fill in the other as the same as the primary name.")
        }



        
class AddAuthorBioForm(forms.ModelForm):
    class Meta:
        model = AuthorBio
        fields = [
            'language',
            'bio'
        ]
        help_texts = {
            'language': _("You can only make one Bio per language. Edit an existing Bio if one already exists in the language you want to use.")
        }




class AddDocumentForm(forms.ModelForm):        
    class Meta:
        model = Document
        fields = [
            'title',
            'authors',
            'prod_y',
            'manualdocid'
        ]
        labels = {
            'title': _("Title"),
            'authors': _("Author(s)"),
            'prod_y': _("Publication or production year"),
            'manualdocid': _("Manual Document ID")
        }
        help_texts = {
            'authors': _("Authors must be defined before their documents. If you don't see your document's author, head over to the Authors page and create one. Hold the ctrl button while you click to select multiple authors."),
            'manualdocid': _("If you don't know what this is, just leave it blank.")
        }


class DocumentExtraMetadataForm(forms.ModelForm):
    class Meta:
        model = DocumentExtraMetadata
        fields = [
            'publisher',
            'publisherlocation',
            'docidtype',
            'docid',
            'inpublication',
            'publicationvolume',
            'publicationissue',
            'pagerange',
            'url'
        ]
        labels = {
            'publisher': _("Publisher"),
            'publisherlocation':_("Publisher location"),
            'docidtype': _("Document ID type"),
            'docid': _("Document ID"),
            'inpublication': _("In publication"),
            'publicationvolume': _("Publication volume"),
            'publicationissue': _("Publication issue"),
            'pagerange': _("Page range"),
            'url': "URL"
        }
        help_texts = {
            'inpublication': _("Use this field if the Document was part of a book with many author or published in a magazine or journal."),
            'pagerange': _("Separate pages with two hyphens, e.g. 4--8. Use a comma to separate multiple page ranges, e.g. 4--7, 9--12.")
        }



        
class DocumentDescriptionForm(forms.ModelForm):
    class Meta:
        model = DocumentDescription
        fields = [
            'language',
            'description'
        ]
        help_texts = {
            'language': _("You can only make one description per language. Edit the existing one if it exists.")
        }


        

class EditDocumentDescriptionForm(forms.Form):
    description_text = forms.CharField(
        widget = forms.Textarea,
        help_text = _("You should only edit one description at a time. Save agter each edit.")
    )
    descr_pk = forms.CharField(
        widget = forms.HiddenInput
    )



    
class EditAuthorBioForm(forms.Form):
    bio_text = forms.CharField(
        widget = forms.Textarea,
        help_text = _("You should only edit one Bio at a time. Save after each edit.")
    )
    bio_pk = forms.CharField(
        widget = forms.HiddenInput
    )



    
class SubmitMarkdownForm(forms.Form):
    saved = forms.BooleanField(
        label = _('All changes have been saved changes with the "Save Markup" button.'),
        help_text = _('If you have edited the markup field and not yet saved the changes, submitting to the corpus now will submit the Markup version before the changes you made and your work will be lost. click the "Save Markup" button now if you are not sure.'),
        required = True,
        initial = False
    )
    alltext = forms.BooleanField(
        label = _('All text from media file(s) (left) is represented in the Markup.'),
        required = True,
        initial = False
    )
    formatting = forms.BooleanField(
        label = _('Basic formatting --bold, italic, underline, strikethrough-- is represented in the Markup.'),
        required = True,
        initial = False
    )
    langset = forms.BooleanField(
        label = _('All fragments have a defined language using the &lt;SET language=""/&gt; tag'),
        required = True,
        initial = False
    )
    pagebreaks = forms.BooleanField(
        label = _('In documents with multi-page media, all page breaks are represented with the &lt;ENDPAGE nr=""/&gt; tag.'),
        required = True,
        initial = False
    )
    marginal = forms.BooleanField(
        label = _('Marginal, header, and footer text is enclosed in the &lt;MARGIN loc=""&gt;&lt;/MARGIN&gt; tag.'),
        required = True,
        initial = False
    )




class SearchForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.fields['findintitles'] = forms.MultipleChoiceField(
            label = _("Search in these document only"),
            required = False,
            choices =  [(x['id'], x['title']) for x in Document.objects.filter(readyincorpus=True).values('id', 'title')],
            help_text = _("If not selected, the term will be searched in all documents' text only.")
        )
    
    term = forms.CharField(
        label = _("Search Term"),
        required = True,
        help_text = _("By default, the search is case insensitive. If you have a case sensitive issue to search for, use the regex option.")
    )
    queryinlanguage = forms.MultipleChoiceField(
        label = _("Return results annotated as language"),
        required = False,
        choices = lang_opts,
        help_text = _("Hold down 'ctrl' key to select multiple or deselect. No selection will search all languages. This option doesn't apply in Document title searches.")
    )   
    regex = forms.BooleanField(
        label = _("Regular Expression Search"),
        required = False,
        initial = False,
        help_text = _("The regex search option nulifies 'whole word' and 'ignore formatting' options. If you want to use regex searches, you can write them into your own regex.")
    )
    wholewords = forms.BooleanField(
        label = _("Search for whole words (only)"),
        required = False,
        initial = False
    )
    ignorelinebreaks = forms.BooleanField(
        label = _("Find words that break accross a line"),
        required = False,        
        initial = True
    )

    class Meta:
        widgets = {
            'queryinlanguage': forms.CheckboxSelectMultiple(choices=lang_opts)
        }

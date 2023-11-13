from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _




LANGUAGE_OPTIONS = (
    ("Polish", _("Polish")),
    ("English", _("English")),
    ("Wymysorys", _("Wymysorys")),
    ("German", _("German"))
)

LANGUAGE_OPTIONS_TWO = (
    ("Polish", _("Polish")),
    ("English", _("English")),
    ("Wymysorys", _("Wymysorys")),
    ("German", _("German")),
    ("TX, Polish-Wymysorys", _("TX, Polish-Wymysorys")),
    ("TX, English-Wymysorys", _("TX, English-Wymysorys")),
    ("TX, German-Wymysorys", _("TX, German-Wymysorys"))
)

ASSET_TYPES = (
    ('pdf', _('pdf document')),
    ('img', _('image')),
    ('doc', _('doc or other cooked text')),
    ('txt', _('plain txt'))
)

DOC_ID_TYPES = (
    ("ISBN", "ISBN"),
    ("DOI", "DOI")
)

MARGIN_LOC_OPTIONS = [
    ("bottom-left", _("bottom-left")),
    ("bottom-right", _("bottom-right")),
    ("bottom", _("bottom")),
    ("top-left", _("top-left")),
    ("top-right", _("top-right")),
    ("top", _("top")),
    ("left", _("left")),
    ("right", _("right"))
]




class AuthorMeta(models.Model):
    DOB_y = models.IntegerField(
        _("Birth Year"),
        blank = True,
        null = True
    )
    DOB_m = models.IntegerField(
        _("Birth Month"),
        blank = True,
        null = True
    )
    DOB_d = models.IntegerField(
        _("Birth Day"),
        blank = True,
        null = True
    )
    DOB_y_priv = models.BooleanField(
        _("Private Birth Year"),
        default=False
    )
    DOB_m_priv = models.BooleanField(
        _("Private Birth Month"),
        default=True
    )
    DOB_d_priv = models.BooleanField(
        _("Private Birth Day"),
        default=True
    )
    DOD_y = models.IntegerField(
        _("Death Year"),
        blank = True,
        null = True
    )
    DOD_m = models.IntegerField(
        _("Death Month"),
        blank = True,
        null = True
    )
    DOD_d = models.IntegerField(
        _("Death Day"),
        blank = True,
        null = True
    )
    DOD_y_priv = models.BooleanField(
        _("Private Death Year"),
        default=False
    )
    DOD_m_priv = models.BooleanField(
        _("Private Death Month"),
        default=True
    )
    DOD_d_priv = models.BooleanField(
        _("Private Death Day"),
        default=True
    )
    dateadded = models.DateField(
        _("Date Added"),
        auto_now_add=True
    )


    def __str__(self):
        names = self.author_name.all()
        if names:
            primary = [x for x in names if x.primary == True][0]
            return str(primary)
        else:
            return str(self.id)

    def author_names(self):
          names = self.author_name.all()
          if names:
              return "\n".join([str(n) for n in names])
          else:
              return None

    def alt_names(self):
        names = self.author_name.all()
        if names:
            return [n for n in names if n.primary==False and n.private==False]
        else:
            return None
          
    def author_bios(self):
        bios = self.author_bio.all()
        if bios:
            return  "\n~~~~~~~~~~~~~\n".join(
                ["{}:\n{}".format(b.language, b.bio) for b in bios]
            )
        else:
            return None

    def bio_objects(self):
        bios = self.author_bio.all()
        if bios:
            return [b for b in bios if b.private==False]
        else:
            return None


    
class AuthorBio(models.Model):
    author = models.ForeignKey(
        AuthorMeta,
        on_delete = models.CASCADE,
        related_name = "author_bio"
    )
    language = models.CharField(
        _("Language of Bio"),
        max_length = 120,
        choices = LANGUAGE_OPTIONS
    )
    private = models.BooleanField(
        _("Private Bio"),
        default=False
    )
    bio = models.TextField()

    def __str__(self):
        return str(self.author)

    class Meta:
        unique_together = ('author', 'language')



    
class AuthorName(models.Model):
    author = models.ForeignKey(
        AuthorMeta,
        on_delete = models.CASCADE,
        blank = True,
        null = True,
        related_name = "author_name"
    )
    primary = models.BooleanField()
    private = models.BooleanField()
    firstname = models.CharField(
        _("Author First Name(s)"),
        max_length = 120
    )
    surname = models.CharField(
        _("Author Surname"),
        max_length = 120
    )

    def __str__(self):
        return "{}, {}".format(self.surname, self.firstname)




class Contributor(models.Model):
    name = models.CharField(
        _("Name of Contributor"),
        max_length = 120
    )
    siteorid = models.CharField(
        _("Website and / or orcid"),
        max_length = 540,
        blank = True,
        null = True
    )

    def __str__(self):
        return self.name

    def contributor_contributions(self):
        contributions = self.contributor_contribution.all()
        if contributions:
            return "\n~~~~~~~~~~~\n".join(
                ["{}:\n{}".format(c.title, c.description) for c in contributions]
            )
        else:
            return None




class Contribution(models.Model):
    contributor = models.ForeignKey(
        Contributor,
        on_delete = models.CASCADE,
        related_name = 'contributor_contribution'
    )
    start = models.CharField(
        _("Start of Contribution"),
        max_length = 120
    )
    end = models.CharField(
        _("End of Contribution"),
        max_length = 120,
        blank = True,
        null = True
    )
    title = models.CharField(
        _("Title of Contribution"),
        max_length = 540,
    )
    description = models.TextField()

    def __str__(self):
        return self.title



    
class DocumentCollection(models.Model):
    name = models.CharField(
        _("Collection Name"),
        max_length = 120
    )
    description = models.TextField()

    def __str__(self):
        return self.name

    def collection_documents(self):
        docs = self.collection_doc.all()
        if docs:
            return "\n".join(
                [str(d.title) for d in docs]
            )
        else:
            return None
    

    
class Document(models.Model):
    title = models.CharField(
        _("Title of Document"),
        max_length = 540,
    )
    authors = models.ManyToManyField(AuthorMeta)
    incollection = models.ForeignKey(
        DocumentCollection,
        on_delete = models.SET_NULL,
        related_name = "collection_doc",
        blank = True,
        null = True
    )
    manualdocid = models.IntegerField(
        _("Manual doc ID"),
        unique = True,
        blank = True,
        null = True
    )
    dateadded = models.DateField(
        _("Date Added"),
        auto_now_add=True
    )
    prod_y = models.IntegerField(
        _("Production Year"),
        blank = True,
        null = True
    )
    prod_m = models.IntegerField(
        _("Production Month"),
        blank = True,
        null = True
    )
    prod_d = models.IntegerField(
        _("Production Day"),
        blank = True,
        null = True
    )
    readyincorpus = models.BooleanField(
        _("Document Ready in Corpus"),
        default=False
    )

    def __str__(self):
        return self.title

    def authors_list(self):
        return "\n".join(
            [str(a) for a in self.authors.all()]
        )

    def document_descriptions(self):
        descrs = self.document_description.all()
        if descrs:
            return "\n~~~~~~~~~~~~\n".join(
                ["{}:\n{}".format(d.language, d.description) for d in descrs]
            )
        else:
            return None

    def description_objects(self):
        descrs = self.document_description.all()
        if descrs:
            return [d for d in descrs]
        else:
            return None



class DocumentExtraMetadata(models.Model):
    document = models.OneToOneField(
        Document,
        on_delete = models.CASCADE,
        blank = True,
        null = True
    )
    publisher = models.CharField(
        _("Publisher"),
        max_length = 240,
        blank = True,
        null = True
    )
    publisherlocation = models.CharField(
        _("Publisher Location"),
        max_length = 120,
        blank = True,
        null = True
    )
    docid = models.CharField(
        _("Document ID"),
        max_length = 120,
        blank = True,
        null = True
    )
    docidtype = models.CharField(
        _("Document ID type"),
        max_length = 24,
        choices = DOC_ID_TYPES,
        blank = True,
        null = True
    )
    inpublication = models.CharField(
        _("In Publication (journal, volume)"),
        max_length = 240,
        blank = True,
        null = True
    )
    publicationvolume = models.IntegerField(
        _("Volume"),
        blank = True,
        null = True
    )
    publicationissue = models.IntegerField(
        _("Issue"),
        blank = True,
        null = True
    )
    pagerange = models.CharField(
        _("Page Range"),
        max_length = 120,
        blank = True,
        null = True,
    )
    url = models.CharField(
        _("Publication / Document URL"),
        max_length = 500,
        blank = True,
        null = True,
    )
     
    def __str__(self):
        return str(self.document)



class DocumentDescription(models.Model):
    document = models.ForeignKey(
        Document,
        on_delete = models.CASCADE,
        related_name = "document_description"
    )
    language = models.CharField(
        _("Language of Description"),
        max_length = 120,
        choices = LANGUAGE_OPTIONS
    )
    description = models.TextField()
    
    def __str__(self):
        return str(self.document)

    class Meta:
        unique_together = ('document', 'language')

    


class DocumentMarkup(models.Model):
    version = models.IntegerField()
    document = models.OneToOneField(
        Document,
        on_delete = models.CASCADE
    )
    canedit = models.BooleanField(default=True)
    markup = models.TextField()

    def __str__(self):
        return "{} markup".format(str(self.document))

    

    
class DocumentParagraph(models.Model):
    document = models.ForeignKey(
        Document,
        on_delete = models.CASCADE
    )
    order = models.IntegerField(
        _("Order of Paragraphs in Document"),
        blank = True,
        null = True
    )

    def __str__(self):
        return "{}, paragraph {}".format(str(self.document), str(self.order))




class ParagraphFragment(models.Model):
    # fragments are used to separate multilingual paragraphs....
    # it's fine to have just one fragment in a paragraph...
    # this is different from the XML version
    paragraph = models.ForeignKey(
        DocumentParagraph,
        on_delete = models.CASCADE
    )
    order = models.IntegerField(
        _("Order of Fragments in Document"),
        blank = True,
        null = True
    )
    language = models.CharField(
        _("Language of Fragment"),
        max_length = 120,
        choices = LANGUAGE_OPTIONS_TWO,
        blank = True,
        null = True
    )
    text = models.TextField()

    def __str__(self):
        return "{}, fragment {}".format(str(self.paragraph), str(self.order))




class MarginText(models.Model):
    fragment = models.ForeignKey(
        ParagraphFragment,
        on_delete = models.CASCADE
    )
    location = models.CharField(
        _("Location of Text"),
        max_length = 120,
        choices = MARGIN_LOC_OPTIONS
    )
    text = models.TextField()

    def __str__(self):
        return "Marginal text on Fragment {}".format(str(self.fragment))




class Asset(models.Model):
    file_instance = models.FileField(
        _("File Instance"),
        upload_to = "nwymc-assets",
        null = True
    )
    filetype = models.CharField(
        _("File Type"),
        max_length = 120,
        choices = ASSET_TYPES
    )
    order = models.IntegerField(
        _("Order of Assets in Document"),
        blank = True,
        null = True
    )
    document = models.ForeignKey(
        Document,
        on_delete = models.SET_NULL,
        blank=True,
        null=True
    )
    showonui = models.BooleanField(
        _("Show on UI"),
        default=True
    )
    uploader = models.ForeignKey(
        User,
        on_delete = models.CASCADE
    )
    dateadded = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ('order',)
        
    def __str__(self):
        return str(self.file_instance)




PERMISSIONS_LEVELS = (
    ('public', _('General Public')),
    ('contributor', _('Contributor')),
    ('worker', _('Worker')),
    ('admin', _('Admin'))
)

class Permission(models.Model):
    user = models.OneToOneField(
        User,
        on_delete = models.CASCADE,
        blank = False,
        null = False,
    )
    level = models.CharField(
        _("Permissions Level"),
        max_length = 120,
        choices = PERMISSIONS_LEVELS
    )

    def __str__(self):
        return f"{self.user.username} - {self.level}"

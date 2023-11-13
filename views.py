from django.shortcuts import render, redirect
from django.conf.urls.i18n import i18n_patterns
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage, BadHeaderError
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from .decorators import *
from .forms import *
from .models import *
import time
import re
import json




#########################
### SUPPORT FUNCTIONS ###
#########################


def get_lines(text):
    lines = text.split('\n')
    return lines

def is_different(stored_lines, submitted_lines):
    differences = []
    for idx, subl in enumerate(submitted_lines):
        print(subl, stored_lines[idx])
        if subl == stored_lines[idx]:
        #    print("TRUE")
            differences.append((True, subl))
        else:
        #    print("FASLE")
            differences.append((False, subl))

    return differences
        

def interpolate_term(term):
    capture_group = "(<br/>|-<br/>)?"
    interpolated_term = ''
    for i, l in enumerate(term):
        if i == len(term) - 1:
            interpolated_term += l
        else:
            interpolated_term += l
            interpolated_term += capture_group

    return interpolated_term




prepostspan = 60 # how much text we want on either side of the hit
def get_filter_indexes(Qobjects, research, isregex):
    results = []
    for O in Qobjects:
        #print(O)
        hits = None
        if isregex:
            hits = re.finditer(rf'{research}', O.text)
        else:
            hits = re.finditer(rf'{research}', O.text, re.IGNORECASE)
        for hit in hits:
            #print(hit)
            if hit.span()[0] > prepostspan:
                pretext = '... ' + O.text[hit.span()[0]-prepostspan: hit.span()[0]] + ' ...'
            elif hit.span()[0] == 0:
                pretext = ''
            else:
                pretext = O.text[:hit.span()[0]] + ' ...'

            if hit.span()[1] < len(O.text) - prepostspan:
                posttext = '... ' + O.text[hit.span()[1]:hit.span()[1]+prepostspan] + ' ...'
            elif hit.span()[1] == len(O.text) - 1:
                posttext = ''
            else:
                posttext = '... ' + O.text[hit.span()[1]:]

            results.append((
                O,
                pretext,
                hit[0],
                posttext
            ))

    return results, results
        



######################
### VIEW FUNCTIONS ###
######################




# no login necessary 
def landing(request):
    with open('nwymc/WordsDumps/latest_summary.json', 'r', encoding='utf-8') as J:
        wordssummary = json.load(J) 
    context = {
        'title': _('Corpus of New Wymysorys – Home'),
        'NAssets': len(Asset.objects.all()),
        'NpublicAssets': len(Asset.objects.filter(showonui=True)),
        'NDocuments': len(Document.objects.all()),
        'NreadyDocuments': len(Document.objects.filter(readyincorpus=True)),
        'NAuthors': len(AuthorMeta.objects.all()),
        'wordssummary': wordssummary
    }
    
    return render(request, 'nwymc/landing.html', context)




# no login necessary
def about(request):
    context = {
        'title': _('Corpus of New Wymysorys – About'),
        'contributions': Contribution.objects.all().order_by('start')
    }
    
    return render(request, 'nwymc/about.html', context)




@login_required
@user_has_permissions_assignment
def asset_overview(request):
    context = {
        'title': _('Corpus of New Wymysorys – Asset Overview'),
        'num_assets': len(Asset.objects.all())
    }

    if request.user.permission.level != 'public':
        if request.method == "POST":
            UAform = UploadAssetForm(request.POST, request.FILES)
            context['form'] = UAform
            if UAform.is_valid():
                print("FORM IS VALID")
                inst = UAform.save(commit=False)
                inst.uploader = request.user
                inst.save()
                messages.info(request, _("Thanks for the contribution!"))
                return redirect('asset-overview')
            else:
                print("FORM NOT VALID")
                print(UAform.errors)
        else:
            context['form'] = UploadAssetForm()

    if request.user.permission.level == 'admin':
        asset_objects = Asset.objects.all()
    else:
        asset_objects = Asset.objects.filter(showonui=True)

    paginator = Paginator(asset_objects, 50)
    page = request.GET.get("page")
    try:
        asset_objects = paginator.page(page)
    except PageNotAnInteger:
        asset_objects = paginator.page(1)
    except EmptyPage:
        asset_objects = paginator.page(paginator.num_pages)
    
    if request.user.permission.level == 'public':
        context['asset_objects'] = None
    else:
        context['asset_objects'] = asset_objects
        
    return render(request, 'nwymc/asset-overview.html', context)




@login_required
@user_has_permissions_assignment
@user_is_at_least_contributor
def asset_view(request, asset_pk):
    asset = Asset.objects.get(pk=asset_pk)
    
    if asset.showonui == False and request.user.permission.level != 'admin':
        messages.warning(request, _("You are requesting an Asset that either does not exist or you do not have permission to view"))
        return redirect('nwymc-asset-overview')

    filename = str(asset.file_instance)[13:]        
    context = {
        'title': _('Corpus of New Wymysorys – Asset:') + ' ' + filename,
        'filename': filename,
        'asset': asset,
    }
    if request.user.permission.level == "worker" or request.user.permission.level == "admin":
        if request.method == 'POST':
            form = AssignAssetForm(request.POST, instance=asset)
            if form.is_valid():
                form.save()
                return redirect('asset-view', asset_pk=asset_pk)
        else:
            form = AssignAssetForm()
            
        context['form'] = form

    return render(request, 'nwymc/asset-view.html', context)




@login_required
@user_has_permissions_assignment
def author_overview(request):
    context = {
        'title': _('Corpus of New Wymysorys – Author Overview'),
    }

    if request.user.permission.level != 'public':
        if request.method == 'POST':
            form = AddAuthorForm(request.POST)
            if form.is_valid():
                if form.cleaned_data['year_o_birth']:
                    AMinst = AuthorMeta.objects.create(
                        DOB_y = form.cleaned_data['year_o_birth']
                    )
                else:
                    AMinst = AuthorMeta.objects.create()
                AMinst.save()
                ANinst = AuthorName.objects.create(
                    author = AMinst,
                    primary = True,
                    private = False,
                    surname = form.cleaned_data['surname'],
                    firstname = form.cleaned_data['firstname']
                )
                ANinst.save()
                messages.info(request, _("Thanks for the contribution!"))
                return redirect('author-overview')
        else:
            context['form'] = AddAuthorForm()

    author_objects = AuthorMeta.objects.all()
    
    paginator = Paginator(author_objects, 25)
    page = request.GET.get("page")
    try:
        author_objects = paginator.page(page)
    except PageNotAnInteger:
        author_objects = paginator.page(1)
    except EmptyPage:
        author_objects = paginator.page(paginator.num_pages)
        
    context['author_objects'] = author_objects
        
    return render(request, 'nwymc/author-overview.html', context)




@login_required
@user_has_permissions_assignment
def author_view(request, author_pk):
    author = AuthorMeta.objects.get(pk=author_pk)
    context = {
        'title': _('Corpus of New Wymysorys – Author:'),
        'author': author
    }

    if request.user.permission.level != 'public':
        if request.method == "POST":
            submission_bool = False
            if 'surname' in request.POST:
                aan_form = AddAuthorNameForm(request.POST)
                if aan_form.is_valid():
                    aan_inst = aan_form.save(commit=False)
                    aan_inst.author = author
                    aan_inst.primary = False
                    aan_inst.private = False
                    aan_inst.save()
                    submission_bool = True
            if 'bio' in request.POST:
                aab_form = AddAuthorBioForm(request.POST)
                if aab_form.is_valid():
                    aab_inst = aab_form.save(commit=False)
                    aab_inst.author = author
                    aab_inst.private = False
                    aab_inst.save()
                    submission_bool = True
            if 'bio_text' in request.POST:
                eab_form = EditAuthorBioForm(request.POST)
                if eab_form.is_valid():
                    bio_inst = AuthorBio.objects.get(pk=eab_form.cleaned_data['bio_pk'])
                    bio_inst.bio = eab_form.cleaned_data['bio_text']
                    bio_inst.save()
                    submission_bool = True
            if submission_bool:
                messages.info(request, _("Thanks for the contribution!"))
                return redirect('author-view', author_pk=author_pk)
        else:    
            context['AANform'] = AddAuthorNameForm()
            context['AABform'] = AddAuthorBioForm()
            if request.user.permission.level != 'contributor':
                context['EABform'] = EditAuthorBioForm()
    
    return render(request, 'nwymc/author-view.html', context)




# no login
def document_overview(request):
    context = {
        'title': _("Corpus of New Wymysorys – Document Overview"),
    }
    document_objects = Document.objects.all()

    if hasattr(request.user, 'permission'):
        if request.user.permission.level != 'public':
            if request.method == "POST":
                form = AddDocumentForm(request.POST)
                if form.is_valid():
                    form.save()
                    messages.info(request, _("Thanks for the contribution!"))
                    return redirect('document-overview')
            else:
                context['form'] = AddDocumentForm()

    paginator = Paginator(document_objects, 25)
    page = request.GET.get("page")
    try:
        document_objects = paginator.page(page)
    except PageNotAnInteger:
        document_objects = paginator.page(1)
    except EmptyPage:
        document_objects = paginator.page(paginator.num_pages)
    context['document_objects'] = document_objects
    
    return render(request, 'nwymc/document-overview.html', context)




# no login necessary
def document_meta(request, document_pk):
    document = Document.objects.get(pk=document_pk)
    N_assets = len(Asset.objects.filter(document=document))
    context = {
        'title': _('Corpus of New Wymysorys – Document meta:') + ' ' + document.title,
        'document': document,
        'descriptions': DocumentDescription.objects.filter(pk=document_pk),
        'N_assets': N_assets
    }
    if hasattr(request.user, 'permission'):
        if request.user.permission.level != 'public':
            if request.method == 'POST':
                # here's a comment
                #
                #
                submission_bool = False
                if 'publisher' in request.POST:
                    try:
                        em_form = DocumentExtraMetadataForm(
                            request.POST,
                            instance=DocumentExtraMetadata.objects.get(document=document)
                        )
                    except:
                        em_form = DocumentExtraMetadataForm(
                            request.POST,
                        )
                    if em_form.is_valid():
                        em_inst = em_form.save(commit=False)
                        em_inst.document = document
                        em_inst.save()
                        submission_bool = True
                if 'description' in request.POST:
                    ad_form = DocumentDescriptionForm(request.POST)
                    if ad_form.is_valid():
                        ad_inst = ad_form.save(commit=False)
                        ad_inst.document = document
                        ad_inst.save()
                        submission_bool = True
                if 'description_text' in request.POST:
                    ed_form = EditDocumentDescriptionForm(request.POST)
                    if ed_form.is_valid():
                        desc_inst =  DocumentDescription.objects.get(pk=ed_form.cleaned_data['descr_pk'])
                        desc_inst.description = ed_form.cleaned_data['description_text']
                        desc_inst.save()
                        submission_bool = True
                if submission_bool:
                    messages.info(request, _("Thanks for the contribution!"))
                    return redirect('document-meta', document_pk=document_pk)                
            else:
                context['DDform'] = DocumentDescriptionForm()
                try:
                    context['DEMform'] = DocumentExtraMetadataForm(
                        instance=DocumentExtraMetadata.objects.get(document=document)
                    )
                except:
                    context['DEMform'] = DocumentExtraMetadataForm()
                if request.user.permission.level != 'contributor':
                    context['EDform'] = EditDocumentDescriptionForm()

    return render(request, 'nwymc/document-meta.html', context)




@login_required
@user_is_at_least_contributor
def document_content(request, document_pk):
    document = Document.objects.get(pk=document_pk)
    paragraphs = DocumentParagraph.objects.filter(document=document).order_by('order')
    paginator = Paginator(paragraphs, 30)
    page = request.GET.get("page")
    try:
        paragraphs = paginator.page(page)
    except PageNotAnInteger:
        paragraphs = paginator.page(1)
    except EmptyPage:
        paragraphs = paginator.page(paginator.num_pages)
    
    context = {
        'title': _('Corpus of New Wymysorys – Document content:') + ' ' + document.title,
        'document': document,
        'paragraphs': paragraphs
    }

    return render(request, 'nwymc/document-content.html', context)




@login_required
@user_is_at_least_worker
def document_markup(request, document_pk):
    document = Document.objects.get(pk=document_pk)
    assets = Asset.objects.filter(document=document, showonui=True)
    try:
        markup = DocumentMarkup.objects.get(document=document)
    except:
        markup = None
        
    if request.method == 'POST':
        if request.POST.get('langset'):
            form = MarkdownForm(instance=markup)
            subform = SubmitMarkdownForm(request.POST)
            if subform.is_valid():
                markup.canedit = False
                markup.save()

                #
                #
                #
                # email notice to admin
                mail_subject = 'NWymC:: New Markup Submission'
                mail_message = render_to_string('NWymC/new-markup_email.html',
                                                {'user':request.user,
                                                'document': document}
                )
                admins = User.objects.filter(permission__level__contains='admin')
                admin_emails = [a.email for a in admins]
                email = EmailMessage(mail_subject, mail_message, to=admin_emails)
                email.send()
                #
                #
                #
                #
                
                return redirect('document-meta', document.id)
        else:
            form = None
            markup_version = None
            if markup:
                form = MarkdownForm(request.POST, instance=markup)
                markup_version = markup.version
            else:
                updated_request = request.POST.copy()
                updated_request.update({'version':0})
                form = MarkdownForm(updated_request)
                
                
            subform = SubmitMarkdownForm()
            if form.is_valid():
                print("form valid")
                if markup_version == None or markup_version == form.cleaned_data['version']:
                    instance = form.save(commit=False)
                    instance.document = document
                    instance.canedit = True
                    instance.version = int(form.cleaned_data['version']) + 1
                    instance.markup = form.cleaned_data['markup']
                    instance.save()
                    return redirect('document-markup', document_pk=document.id) 
                else:
                    print(form.cleaned_data)
                    storedMO = DocumentMarkup.objects.get(document=document)
                    stored_lines = get_lines(storedMO.markup)
                    submitted_lines = get_lines(form.cleaned_data['markup'])
                    behindness = int(storedMO.version) - int(form.cleaned_data['version'])
                    context = {
                        'title': "Oh No! Concurrency error",
                        'stored_lines': stored_lines,
                        'submitted_lines': is_different(stored_lines, submitted_lines),
                        'behindness': behindness
                    }
                    return render(request, 'nwymc/concurrency-error.html', context)
            else:
                print(form.errors)
                    
    else:
        if markup:
            form = MarkdownForm(instance=markup)
        else:
            form = MarkdownForm(initial={'markup':'<SET language="?"/>'})
        subform = SubmitMarkdownForm()
    context = {
        'title': _('Corpus of New Wymysorys – Markup:') + ' ' + document.title,
        'document': document,
        'assets': assets,
        'form': form,
        'submit_form': subform,
        'markup': markup
    }
            
    return render(request, 'nwymc/document-markup.html', context)




@login_required
@user_has_permissions_assignment
def markup_reference(request):
    context = {
        'title': _('Corpus of New Wymysorys – Markup Reference')
    }
    return render(request, 'nwymc/markup-reference.html', context)




def document_collection_overview(request, collection_pk):
    pass




# no log in
def search(request):
    context = {
        'title': _('Corpus of New Wymysorys – Search'),
        'form': SearchForm,
        'query': None
    }

    if request.method == "GET":
        search_form = SearchForm(request.GET)
        search_results = None
        if search_form.is_valid():
            context['form'] = search_form
            query = search_form.cleaned_data
            context['query'] = query
            
            term = query['term']
            Qterm = None
            RX = False
            if query['regex']:
                Qterm = term
                RX = True
            else:
                if query['ignorelinebreaks']:
                    iterm = interpolate_term(term)
                    if query['wholewords']:
                    #    Qterm = rf'\b{iterm}\b'
                        Qterm = rf"[^A-Za-zȦȧÖöӧŁłŻżŹźĆćĄąĘęŚśŃńÓó]({iterm})[^A-Za-zȦȧÖӧöŁłŻżŹźĆćĄąĘęŚśŃńÓó]"                        
                    else:
                        Qterm = rf"[A-Za-zȦȧÖöӧŁłŻżŹźĆćĄąĘęŚśŃńÓó]*({iterm})[A-Za-zȦȧÖöӧŁłŻżŹźĆćĄąĘęŚśŃńÓó]*"
                else:
                    if query['wholewords']:
                    #    Qterm = rf'\b{term}\b'
                        Qterm = rf"[^A-Za-zȦȧÖöӧŁłŻżŹźĆćĄąĘęŚśŃńÓó]({term})[^A-Za-zȦȧÖöӧŁłŻżŹźĆćĄąĘęŚśŃńÓó]"
                    else:
                        Qterm = rf'[A-Za-zȦȧÖöӧŁłŻżŹźĆćĄąĘęŚśŃńÓó]*({term})[A-Za-zȦȧÖöӧŁłŻżŹźĆćĄąĘęŚśŃńÓó]*'
            if query['regex']:
                qobj = Q(text__regex=Qterm)
            else:
                qobj = Q(text__iregex=f"{Qterm}")
                    
            lQ = None
            first_l = True

            if len(query['queryinlanguage']) > 0:
                for l in query['queryinlanguage']:
                    if first_l:
                        lQ = Q(language=l)
                        first_l = False
                    else:
                        lQ.add(Q(language=l), Q.OR)
                if lQ:
                    qobj.add(lQ, Q.AND)

            tQ = None
            first_t = True
            if len(query['findintitles']) > 0:
                for t in query['findintitles']:
                    if first_t:
                        tQ = Q(paragraph__document=t)
                        first_t = False
                    else:
                        tQ.add(Q(paragraph__document=t), Q.OR)
                if tQ:
                    qobj.add(tQ, Q.AND)
                    
            #context['qqquery'] = ParagraphFragment.objects.filter(qobj).query
            QOBJS = ParagraphFragment.objects.filter(qobj)
            search_results, results = get_filter_indexes(QOBJS, Qterm, RX)
            context['N_results'] = len(QOBJS)
            context['N_results'] = len(results)
            paginator = Paginator(search_results, 20)
            page = request.GET.get("page")
            try:
                search_results = paginator.page(page)
            except PageNotAnInteger:
                search_results = paginator.page(1)
            except EmptyPage:
                search_results = paginator.page(paginator.num_pages)
        
            context['search_results'] = search_results
            
    return render(request, 'nwymc/search.html', context)



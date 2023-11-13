from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from nwymc.models import DocumentMarkup as Markup
import re

now = datetime.now()
dtstr = now.strftime("%Y%m%d-%H%M%S")

LANGUAGE_OPTIONS = [
    "Wymysorys",
    "English",
    "Polish",
    "German",
    "TX, Polish-Wymysorys",
    "TX, English-Wymysorys",
    "TX, German-Wymysorys",
    "Unspecified"
]

lang_opts = "|".join(LANGUAGE_OPTIONS)

MARGIN_LOC_OPTIONS = [
    "bottom-left",
    "bottom-right",
    "bottom",
    "top-left",
    "top-right",
    "top",
    "left",
    "right"
]

margloc_opts = "|".join(MARGIN_LOC_OPTIONS)


def validate_language(line, linenr):

    errors = None
    messages = []
    
    noattr = re.compile('<SET(?! language=")')
    missingattr = re.search(noattr, line)
    if missingattr:
        errors = True
        messages.append(f"Line {linenr}: (attribute) {missingattr.string}")
    
    unregognizedlanguage = re.compile(f'<SET language="(?!{lang_opts})')
    badlang = re.search(unregognizedlanguage, line)
    if badlang:
        errors = True
        messages.append(f"line {linenr}: (language) {badlang.string}")

    tagclosing = re.compile(f'<SET language="({lang_opts})(?!"/>)')
    badclose = re.search(tagclosing, line)
    if badclose:
        errors = True
        messages.append(f"Line {linenr}: (tag) {badclose.string}")

    return (errors, messages)




def validate_pagebreaks(line, linenr):

    errors = None
    messages = []

    noattr = re.compile('<ENDPAGE(?! NR=")')
    badattr = re.search(noattr, line)
    if badattr:
        errors = True
        messages.append(f"Line {linenr}: (attribute) {badattr.string}")

    nonr = re.compile('<ENDPAGE NR="(?!\d+")')
    badnr = re.search(nonr, line)
    if badnr:
        errors = True
        messages.append(f"Line {linenr}: (page nr) {badnr.string}")

    tagclosing = re.compile('<ENDPAGE NR="\d+"(?!/>)')
    badclose = re.search(tagclosing, line)
    if badclose:
        errors = True
        messages.append(f"Line {linenr}: (tag) {badclose.string}")

    return (errors, messages)




def validate_margins(line, linenr):
    
    errors = None
    messages = []

    noattr = re.compile('<MARGIN(?! loc=")')
    badattr = re.search(noattr, line)
    if badattr:
        errors = True
        messages.append(f"Line {linenr}: (attribute) {badattr.string}")

    unrecognizedlocation = re.compile(f'<MARGIN loc="(?!{margloc_opts})')
    badloc = re.search(unrecognizedlocation, line)
    if badloc:
        errors = True
        messages.append(f"Line {linenr}: (location) {badloc.string}")

    wrongtagend = re.compile(f'<MARGIN loc="({margloc_opts})"(?!>)')
    badtagend = re.search(wrongtagend, line)
    if badtagend:
        errors = True
        messages.append(f"Line {linenr}: (tagclose) {badtagend.string}")

    noclosingtag = re.compile(fr'(<MARGIN loc="({margloc_opts})">).+</(?!MARGIN>)')
    badclose = re.search(noclosingtag, line)
    if badclose:
        errors = True
        messages.append(f"Line {linenr}: (closing tag) {badclose.string}")

    return (errors, messages)




def validate_formatting(line, linenr):
    
    errors = None
    messages = []

    br = re.compile('<br>')
    badbr = re.search(br, line)
    if badbr:
        errors = True
        messages.append(f'Line {linenr}: (br) {line}')

    ital = re.compile('<i>(?!.*\</i>)(.*)')
    badital = re.search(ital, line)
    if badital:
        errors = True
        messages.append(f'Line {linenr}: (ital) {line}')

    bold = re.compile('<b>(?!.*\</b>)(.*)')
    badbold = re.search(bold, line)
    if badbold:
        errors = True
        messages.append(f'Line {linenr}: (bold) {line}')

    underline = re.compile('<u>(?!.*\</u>)(.*)')
    badunderline = re.search(underline, line)
    if badunderline:
        errors = True
        messages.append(f'Line {linenr}: (underline) {line}')

    strike = re.compile('<s>(?!.*\</s>)(.*)')
    badstrike = re.search(strike, line)
    if badstrike:
        errors = True
        messages.append(f'Line {linenr}: (strikethrough) {line}')

    return (errors, messages)    






class Command(BaseCommand):
    
    help = """Validates Markup instance. Takes Markup pk as a single argument.

Usage:
    ./manage.py validate-markup <pk>
"""

    def add_arguments(self, parser):
        parser.add_argument('MarkupID')

    def handle(self, *args, **options):
        try:
            MarkupID = options["MarkupID"]
            markup = Markup.objects.get(pk=MarkupID)
        except:
            raise CommandError(f'There is no Document Markup Instance with ID {MarkupID}.')

        filename = f'{settings.BASE_DIR}/NWymC/MarkupDumps/{MarkupID}_{dtstr}_validate.NWymCMarkup' 
        with open(filename, 'w+') as dump:
            dump.write(markup.markup)

        with open(filename, 'r') as txt:
            lines = txt.readlines()
            lines = [l.strip() for l in lines]
            
            with open(f'{settings.BASE_DIR}/NWymC/MarkupDumps/{MarkupID}_{dtstr}.validation-log', 'w+') as log:

                language_errors = None
                log.write("Language markup validation:\n")
                self.stdout.write("Language markup validation:")
                for ln, l in enumerate(lines, start=1):
                    vl =  validate_language(l, ln)
                    if vl[0]:
                        language_errors = True
                        for m in vl[1]:
                            log.write(f'  {m}\n')                            

                if language_errors:
                    self.stdout.write(" ~!~! There were language markup errors. Fix those before continuing")
                else:
                    self.stdout.write(" ~~  OK")
                    log.write(" ~~ OK\n")
                    
                pagebreak_errors = None
                log.write("Pagebreak markup validation:\n")
                self.stdout.write("Pagebreak markup validation:")
                for ln, l in enumerate(lines, start=1):
                    vp =  validate_pagebreaks(l, ln)
                    if vp[0]:
                        pagebreak_errors = True
                        for m in vp[1]:
                            log.write(f'  {m}\n')
                            
                if pagebreak_errors:
                    self.stdout.write(" ~!~! There were pagebreak markup errors. Fix those before continuing")
                else:
                    self.stdout.write(" ~~  OK")
                    log.write(" ~~ OK\n")
                    
                margins_errors = None
                log.write("Margins validation\n")
                self.stdout.write("Margins validation")
                for ln, l in enumerate(lines, start=1):
                    vm = validate_margins(l, ln)
                    if vm[0]:
                        margins_errors = True
                        for m in vm[1]:
                            log.write(f'  {m}\n')

                if margins_errors:
                    self.stdout.write(" ~!~! There were margins markup errors. Fix those before continuing")
                else:
                    self.stdout.write(" ~~  OK")
                    log.write(" ~~ OK\n")
                    
                formatting_errors = None
                log.write("Formatting validataion:\n")
                self.stdout.write("Formatting validataion")
                for ln, l in enumerate(lines, start=1):
                    vf = validate_formatting(l, ln)
                    if vf[0]:
                        formatting_errors = True
                        for m in vf[1]:
                            log.write(f'  {m}\n')

                if formatting_errors:
                    self.stdout.write(" ~!~! There were formatting markup errors. Fix those before continuing")
                else:
                    self.stdout.write(" ~~  OK")        
                    log.write(" ~~ OK\n")

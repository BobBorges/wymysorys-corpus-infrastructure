from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from nwymc.models import (
    Document,
    ParagraphFragment,
    MarginText,
    DocumentParagraph,
)
from nwymc.models import DocumentMarkup as Markup
import os, re, regex




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

lang_tag_re = re.compile(f'<SET language="({lang_opts})"/>')
endpage_re = re.compile('<ENDPAGE NR="\d+"/>')




def findall(pattern, string):
    matches = []
    fragments = []
    while True:

        match = re.search(pattern, string)

        if not match:
            fragments.append(string)
            break
        matches.append(match)
        fragments.append(string[:match.start()])
        string = string[match.end():]
             
    return matches, fragments




def get_margins(fragment):
    margin = None
    margintxt = regex.compile(f'(?<=<MARGIN loc="({margloc_opts})">)(.*)(?=</MARGIN>)')
    mtxt = regex.search(margintxt, fragment)
    if mtxt:
        margin = mtxt
        fragment = fragment[:margin.start() - len(margin.groups()[0]) - 15] + fragment[margin.end() + 9:]
    return fragment, margin




def is_validated(self, markup_id):
    markup_dump_dir = f'{settings.BASE_DIR}/nwymc/MarkupDumps'
    markup_dumps = os.listdir(markup_dump_dir)
    current_markup_dumps = [f for f in markup_dumps if f.startswith(markup_id) and f.endswith('.validation-log')]
    current_markup_dumps.sort()
    most_recent_dump = current_markup_dumps[-1]
    if most_recent_dump:
        try:
            with open(f'{markup_dump_dir}/{most_recent_dump}', 'r') as v:
                validation = v.readlines()
                validation = [l.strip() for l in validation]
        except:
            self.stdout.write(f"\n\n\nERROR:\nThere's a problem reading the most recent dump file: {most_recent_dump}")
            return False, None
        if validation[1] == '~~ OK' and validation[3] == '~~ OK' and validation[5] == '~~ OK' and validation[7] == '~~ OK':
            markup_file = f'{markup_dump_dir}/{most_recent_dump[:-15]}_validate.NWymCMarkup'
            if os.path.isfile(markup_file):
                return True, markup_file
            else:
                self.stdout.write(f"\n\n\nERROR:\nThe markup file --{most_recent_dump[:-15]}.NWymCMarkup-- can't be found!")
                return False, None
        else:
            self.stdout.write(f"\n\n\nERROR\nThe validation of the most recend Markup Dump --{most_recent_dump}-- failed. Please fix that and try again!")
    else:
        return False, None




class Command(BaseCommand):

    help = "Parses the Markup and creates DocumentParagrap, ParagraphFragment, and MarginText instances in the corpus database."
    
    def add_arguments(self, parser):
        parser.add_argument('MarkupID')

    def handle(self, *args, **options):
        MarkupID = options["MarkupID"]

        try:
            markup = Markup.objects.get(pk=MarkupID)
        except:
            raise CommandError(f"\n\nThere is no Document Markup Instance with ID {MarkupID}\n\n")

        can_continue, markup_file = is_validated(self, MarkupID)
        if can_continue:
            self.stdout.write("\n\n\nVALIDATION IS OK -- let's get on with it...\n\n")

            with open(markup_file, 'r') as file_object:
                lines = file_object.readlines()
                lines = [l.strip() for l in lines if l.strip() != '']
                lines = [l for l in lines if l != '<br>']

                fragment_language = None
                index_correction = 0

                for lidx, l in enumerate(lines, start=1):
                    fragment_count = 1
                    s = re.fullmatch(lang_tag_re, l)
                    if s:
                        fragment_language = s.groups()[0]
                        if fragment_language == "Unspecified":
                            fragment_language = None
                        index_correction += 1
                    elif re.fullmatch(endpage_re, l):
                        p = DocumentParagraph(
                            document = markup.document,
                            order = lidx - index_correction
                        )
                        p.save()
                        f = ParagraphFragment(
                            paragraph = p,
                            order = fragment_count,
                            language = None,
                            text = l
                        )
                        f.save()
                    else:
                        ss, frags = findall(lang_tag_re, l)
                        p = DocumentParagraph(
                            document = markup.document,
                            order = lidx - index_correction
                        )
                        p.save()
                        if ss:
                            for fidx, frag in enumerate(frags):
                                ff = frag.split("<ENDFRAGMENT/>")
                                for f in ff:
                                    f, m = get_margins(f)
                                    fragment = ParagraphFragment(
                                        paragraph = p,
                                        order = fragment_count,
                                        language = fragment_language,
                                        text = f
                                    )
                                    fragment.save()
                                    if m:
                                        margin = MarginText(
                                            fragment = fragment,
                                            location = m.groups()[0],
                                            text = m.groups()[1]
                                        )
                                        margin.save()
                                    fragment_count += 1
                                if fidx < len(frags)-1:
                                    fragment_language = ss[fidx].groups()[0]
                                    if fragment_language == "Unspecified":
                                        fragment_language = None
                        else:
                            ff = l.split("<ENDFRAGMENT/>")
                            for f in ff:
                                f, m = get_margins(f)
                                fragment = ParagraphFragment(
                                    paragraph = p,
                                    order = fragment_count,
                                    language = fragment_language,
                                    text = f
                                )
                                fragment.save()
                                if m:
                                    margin = MarginText(
                                        fragment = fragment,
                                        location = m.groups()[0],
                                        text = m.groups()[1]
                                    )
                                    margin.save()
                                fragment_count += 1
            document = markup.document
            document.readyincorpus = True
            document.save()
            self.stdout.write("It seems like everything worked as it should. Yay!")
        else:
            self.stdout.write(f"\nThe Document Markup --{MarkupID}-- needs to be successfully validated before you can parse it to the corpus.\n\n\n")
    

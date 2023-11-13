import shutil
import sys, string
from google_trans_new import google_translator




twoLetters = sys.argv[1]

def TX(text):
    translator = google_translator()
    tx = translator.translate(text, lang_tgt='pl')
    print(f'TEXT: {text}')
    print(f'TX: {tx}')
    return tx


if len(sys.argv) != 2:
    print("Wrong N args, donkey")
else:
    poFilePath = f"{twoLetters}/LC_MESSAGES/django.po"
    with open(poFilePath, 'r') as poFile:
        poFileContent = poFile.readlines()
        poHead = poFileContent[:23]
        poFileContent = [l.strip() for l in poFileContent]
        poFileContent = [l for l in poFileContent if len(l) > 0]
        poFileContent = poFileContent[22:]
        
        msghead = None
        msgid = None
        translations = []

        for l in poFileContent:
            if l.startswith("msgstr"):
                 T = TX(msgid)
                 translations.append((msghead, msgid, T))
            elif l.startswith("#:"):
                msgid = None
                msghead = l
            elif l.startswith("msgid"):
                msgid = l[7:-1]
            else:
                msgid = msgid + l[1:-1]

        with open(f'{twoLetters}/LC_MESSAGES/newpo.po', 'w+') as outf:
            for h in poHead:
                outf.write(h)
            for t in translations:
                outf.write(f'{t[0]}\n')
                outf.write(f'msgid "{t[1]}"\n')
                outf.write(f'msgstr "{t[2]}"\n\n')

from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from nwymc.models import ParagraphFragment
from tqdm import tqdm
import json, shutil



class Command(BaseCommand):

    help = "Dumps words and word counts to the WordsDumps/ directory."

    def handle(self, *args, **options):

        DT = datetime.now().strftime("%m%d%Y%H%M%S")

        all_N_tot_words = 0
        all_N_uniq_words = 0
        all_uniq_words = []

        wym_N_tot_words = 0
        wym_N_uniq_words = 0
        wym_words = {}

        non_wym_frags = ParagraphFragment.objects.filter(~Q(language='Wymysorys'))
        wym_frags = ParagraphFragment.objects.filter(Q(language='Wymysorys'))

        print("Hamdle non-Wymysorys Fragments")
        for nwf in tqdm(non_wym_frags, total=len(non_wym_frags)):
            text = nwf.text
            words = text.split(' ')
            words = [w.strip('.,?!()[];:-–') for w in words]
            words = [w.lower() for w in words]
            words = [''.join(w.split('<br/>')) for w in words]
            words = [w for w in words if w != '']

            for w in words:
                all_N_tot_words += 1
                if w not in all_uniq_words:
                    all_uniq_words.append(w)
        print("Hamdle Wymysorys Fragments")
        for wf in tqdm(wym_frags, total=len(wym_frags)):
            text = wf.text
            words = text.split(' ')
            words = [w.strip('.,?!()[];:-–') for w in words]
            words = [w.lower() for w in words]
            words = [''.join(w.split('<br/>')) for w in words]
            words = [w for w in words if w != '']

            for w in words:
                all_N_tot_words += 1
                wym_N_tot_words += 1
                if w not in all_uniq_words:
                    all_uniq_words.append(w)
                if w in wym_words:
                    wym_words[w] += 1
                else:
                    wym_words[w] = 1

        all_N_uniq_words = len(all_uniq_words)
        wym_N_uniq_words = len(wym_words)

        wym_words = dict(sorted(wym_words.items(), key=lambda item: item[1], reverse=True))
        
        summaryD = {
            'N_all_all_words': all_N_tot_words,
            'N_uniq_all_words': all_N_uniq_words,
            'N_all_wym_words': wym_N_tot_words,
            'N_uniq_wym_words': wym_N_uniq_words,
            'ten_frequentest': dict(list(wym_words.items())[:10])
        }

        with open(f'nwymc/WordsDumps/summary_{DT}.json', 'w+') as sumout:
            json.dump(summaryD, sumout, indent=4, ensure_ascii=False)
        shutil.copy2(f'nwymc/WordsDumps/summary_{DT}.json', 'nwymc/WordsDumps/latest_summary.json')

        with open(f'nwymc/WordsDumps/wym-words_{DT}.json', 'w+') as wordsout:
            json.dump(wym_words, wordsout, indent=4, ensure_ascii=False)
        shutil.copy2(f'nwymc/WordsDumps/wym-words_{DT}.json', 'nwymc/WordsDumps/latest_wym-words.json')

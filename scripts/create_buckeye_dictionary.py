from __future__ import annotations

import collections

from pathlib import Path


from praatio import textgrid as tgio

buckeye_reference_directory = Path(r'D:\Data\speech\Buckeye\buckeye_reference_alignments')
output_path = r'D:\Data\experiments\adaptation_benchmarking\source_dictionaries\buckeye.dict'

def mid_point(interval):
    return interval.start + ((interval.end - interval.start) / 2)


def format_probability(probability_value: float) -> float:
    """Format a probability to have two decimal places and be between 0.01 and 0.99"""
    return min(max(round(probability_value, 2), 0.01), 0.99)


if __name__ == '__main__':
    dictionary = collections.defaultdict(collections.Counter)
    phones_set = set()
    for speaker_dir in buckeye_reference_directory.iterdir():
        for file in speaker_dir.iterdir():
            print(file.name)
            tg = tgio.openTextgrid(file, includeEmptyIntervals=False, reportingMode="silence")
            phone_tier = None
            word_tier = None
            for tier_name in tg.tierNames:
                if "phones" in tier_name:
                    phone_tier = tg._tierDict[tier_name]
                elif "words" in tier_name:
                    word_tier = tg._tierDict[tier_name]
            for w_begin, w_end, word in word_tier.entries:
                if not word:
                    continue
                if any(word.startswith(x) for x in ['<', '{', '[']):
                    continue
                if word in {'?'}:
                    continue
                phones = []
                for x in phone_tier.entries:
                    if w_begin > mid_point(x):
                        continue
                    if w_end < mid_point(x):
                        break
                    phones.append(x.label)
                    phones_set.add(x.label)
                pronunciation = ' '.join(phones)
                if not pronunciation or any(x in phones for x in {'sil', "spn", '', 'ej', 'aj'}):
                    print(w_end, file.stem, word, pronunciation)
                    continue
                #if word == 'i' and pronunciation not in {'ay', 'aa', 'ah', 'ae', 'eh', 'ih'}:
                #    print(w_end, file.stem, pronunciation)
                dictionary[word.lower()][pronunciation] += 1
    with open(output_path, 'w', encoding='utf8') as f:
        for w, prons in sorted(dictionary.items(), key=lambda x: x[0]):
            max_count = max(prons.values())
            for p, count in sorted(prons.items(), key=lambda x: x[1]):
                #if count <= 1:
                #    continue
                prob = count/max_count
                f.write(f'{w}\t{format_probability(prob)}\t{p}\n')
    for p in sorted(phones_set):
        print(p)
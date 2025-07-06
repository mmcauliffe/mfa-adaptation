import shutil

from pathlib import Path
from praatio import textgrid as tgio
from praatio.utilities.constants import Interval

source_root_directory = Path(r'C:\Users\micha\Documents\Data\VariCS')

naming_source_directory = source_root_directory.joinpath('varics_naming_source')
naming_benchmark_directory = source_root_directory.joinpath('varics_naming_benchmark')
reference_benchmark_directory = source_root_directory.joinpath('varics_naming_reference_alignments')


if __name__ == '__main__':
    naming_benchmark_directory.mkdir(parents=True, exist_ok=True)
    reference_benchmark_directory.mkdir(parents=True, exist_ok=True)
    not_found_count = 0
    found_count = 0
    for f in naming_source_directory.iterdir():
        if f.suffix == '.wav' and not naming_benchmark_directory.joinpath(f.name).exists():
            shutil.copyfile(f, naming_benchmark_directory.joinpath(f.name))
        elif f.suffix == '.TextGrid':
            tg = tgio.openTextgrid(f, includeEmptyIntervals=False, reportingMode="silence")
            reference_tg = tgio.Textgrid(tg.minTimestamp, tg.maxTimestamp)
            benchmark_tg = tgio.Textgrid(tg.minTimestamp, tg.maxTimestamp)
            speaker_name = None
            utterances = []
            reference_phone_tier = None
            reference_word_tier = None
            benchmark_utterance_tier = None
            for tier_name in tg.tierNames:
                if "phones" in tier_name:
                    if reference_phone_tier is not None:
                        continue
                    print(tier_name)
                    reference_phone_tier = tg._tierDict[tier_name]
                    entries = []
                    for i, (start, end, label) in enumerate(reference_phone_tier._entries):
                        pi = Interval(start, end, label)
                        if i != 0 and i != len(reference_phone_tier._entries) - 1:
                            prev_label = reference_phone_tier._entries[i-1][-1]
                            foll_label = reference_phone_tier._entries[i+1][-1]
                            if label == 'EH1' and prev_label == 'M' and foll_label == "M":
                                pi = Interval(pi.start, pi.end, 'IY1')
                            if label == 'AO0' and prev_label == 'S' and foll_label == "K":
                                pi = Interval(pi.start, pi.end, 'AA1')
                            if label == 'IY1' and prev_label == 'F' and foll_label == "SH":
                                pi = Interval(pi.start, pi.end, 'IH1')
                        entries.append(pi)
                    reference_phone_tier._entries = entries
                    reference_tg.addTier(reference_phone_tier)
                elif "words" in tier_name:
                    reference_word_tier = tg._tierDict[tier_name]
                    reference_tg.addTier(reference_word_tier)
                else:
                    benchmark_utterance_tier = tg._tierDict[tier_name]
                    benchmark_tg.addTier(benchmark_utterance_tier)
            tg.save(f, format="long_textgrid", includeBlankSpaces=True)
            reference_tg.save(reference_benchmark_directory.joinpath(f.name), format="long_textgrid", includeBlankSpaces=True)
            benchmark_tg.save(naming_benchmark_directory.joinpath(f.name), format="long_textgrid", includeBlankSpaces=True)
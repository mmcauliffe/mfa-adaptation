import shutil

import os
from pathlib import Path
from praatio import textgrid as tgio
from praatio.utilities.constants import Interval

source_root_directory = Path(r'C:\Users\micha\Documents\Data\VariCS')

correction_directory = source_root_directory.joinpath('sweep1_naming_corrected_tg_wav_14May25', 'corrected_naming_14May25')

naming_benchmark_directory = source_root_directory.joinpath('varics_naming_source')
reference_benchmark_directory = source_root_directory.joinpath('varics_naming_reference_alignments')

bad_files = {
    '23-10-02_11-27-AM_researcher_2_Vcs_wd_ohr_08_m_06_c2_naming_1',
    '23-10-30_11-22-AM_researcher_2_Vcs_gl_stb_07_m_05_c1_naming_1',
    '23-11-06_02-30-PM_researcher_2_Vcs_gl_stb_08_f_07_c2_naming_1',
    '23-10-03_01-24-PM_researcher_1_Vcs_gl_olr_05_m_07_c2_naming_1',
}

PADDING = 0.15

if __name__ == '__main__':
    naming_benchmark_directory.mkdir(parents=True, exist_ok=True)
    reference_benchmark_directory.mkdir(parents=True, exist_ok=True)
    not_found_count = 0
    found_count = 0
    for f in correction_directory.iterdir():
        if f.stem in bad_files:
            continue
        if f.suffix == '.wav' and not naming_benchmark_directory.joinpath(f.name).exists():
            shutil.copyfile(f, naming_benchmark_directory.joinpath(f.name))
        elif f.suffix == '.TextGrid':
            tg = tgio.openTextgrid(f, includeEmptyIntervals=False, reportingMode="silence")
            reference_tg = tgio.Textgrid(tg.minTimestamp, tg.maxTimestamp)
            speaker_name = None
            utterances = []
            reference_phone_tier = None
            reference_word_tier = None
            no_speaker_name = "words" in tg.tierNames or "phones" in tg.tierNames or "words - words" in tg.tierNames
            #if no_speaker_name:
            #    bad_files.add(f.stem)
            #    continue
            p_student = 'p - student - words' in tg.tierNames or 'p - whisper - words' in tg.tierNames
            for tier_name in tg.tierNames:
                speaker_name = "Vcs_" + f.stem.split('Vcs_')[-1]
                speaker_name = speaker_name.split('_naming')[0]
                if not no_speaker_name and not p_student:
                    if ' - ' not in tier_name:
                        continue
                    if "researcher" in tier_name.lower():
                        continue
                    if "resercher" in tier_name.lower():
                        continue
                    if "whisper" in tier_name.lower():
                        continue
                    if "student" in tier_name.lower():
                        continue
                    if "words - words" in tier_name.lower():
                        continue
                    if '_' not in tier_name.split(' - ')[0]:
                        continue
                if "phones" in tier_name:
                    if p_student and 'p - ' not in tier_name:
                        continue
                    if reference_phone_tier is not None:
                        continue
                    reference_phone_tier = tg._tierDict[tier_name]
                    reference_phone_tier.name = f'{speaker_name} - phones'
                    for i, pi in enumerate(reference_phone_tier._entries):
                        if pi.label in {'AE', 'IY', 'OW', 'AA', 'AO', 'AH', 'EH', 'EY', 'UW', 'UH', 'IH'}:
                            reference_phone_tier._entries[i] = Interval(pi.start, pi.end, pi.label + '1')
                        elif pi.label == 'H':
                            reference_phone_tier._entries[i] = Interval(pi.start, pi.end, 'HH')
                        elif pi.label in {'C', "CK"}:
                            reference_phone_tier._entries[i] = Interval(pi.start, pi.end, 'K')
                        elif pi.label == 'OU1':
                            reference_phone_tier._entries[i] = Interval(pi.start, pi.end, 'OW1')
                        elif pi.label == 'AEI':
                            reference_phone_tier._entries[i] = Interval(pi.start, pi.end, 'AE1')
                        elif pi.label == 'eI':
                            reference_phone_tier._entries[i] = Interval(pi.start, pi.end, 'EY1')
                        elif pi.label == 'AA1K':
                            reference_phone_tier._entries[i] = Interval(pi.start, pi.end, 'AA1')
                        elif pi.label == 'Sh':
                            reference_phone_tier._entries[i] = Interval(pi.start, pi.end, 'SH')
                        elif pi.label.islower() and pi.label not in {'spn', 'sil'}:
                            reference_phone_tier._entries[i] = Interval(pi.start, pi.end, pi.label.upper())
                        elif pi.label == 'ΙΥ1':
                            print(pi, f.stem)
                            errror
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
                    if p_student and 'p - ' not in tier_name:
                        continue
                    if reference_word_tier is not None:
                        continue
                    reference_word_tier = tg._tierDict[tier_name]
                    reference_word_tier.name = f'{speaker_name} - words'
                    reference_tg.addTier(reference_word_tier)
                    for wi in reference_word_tier._entries:
                        if wi.label in {'inaudible', 'unknown'}:
                            continue
                        new_start = max(0.0, round(wi.start-PADDING, 3))
                        new_end = min(tg.maxTimestamp, round(wi.end+PADDING, 3))
                        if utterances and utterances[-1].end >= new_start:
                            utterances[-1] = Interval(utterances[-1].start, new_end, utterances[-1].label + ' ' + wi.label)
                            continue
                        utterances.append(Interval(new_start, new_end, wi.label))
            if reference_phone_tier is None or reference_word_tier is None:
                print("DID NOT FIND SPEAKER NAME", f.name)
                not_found_count += 1
                continue
            found_count += 1
            reference_tg.save(reference_benchmark_directory.joinpath(f.name), format="long_textgrid", includeBlankSpaces=True)

            benchmark_tg = tgio.Textgrid(tg.minTimestamp, tg.maxTimestamp)

            utterance_tier = tgio.IntervalTier(speaker_name, utterances, tg.minTimestamp, tg.maxTimestamp)
            benchmark_tg.addTier(utterance_tier)
            benchmark_tg.addTier(reference_word_tier)
            benchmark_tg.addTier(reference_phone_tier)
            benchmark_tg.save(naming_benchmark_directory.joinpath(f.name), format="long_textgrid", includeBlankSpaces=True)
    print(f"NOT FOUND: {not_found_count}, FOUND: {found_count}")
import os
import sys

import sqlalchemy.sql.functions
from pathlib import Path
from montreal_forced_aligner.command_line.mfa import mfa_cli
from montreal_forced_aligner.alignment import AdaptingAligner
from montreal_forced_aligner.db import Utterance, bulk_update
from montreal_forced_aligner.data import WorkflowType
from montreal_forced_aligner import config

if sys.platform == 'darwin':
    root_directory = Path(r'/Users/michael/Documents/Data/experiments/adaptation_benchmarking')
    corpus_root_directory = Path(r'/Users/michael/Documents/Data/VariCS')

    corpus_directory = r'/Users/michael/Documents/Data/VariCS/varics_eval_benchmark'
    reference_directory = r'/Users/michael/Documents/Data/VariCS/varics_naming_reference_alignments'
else:
    root_directory = Path(r'D:\Data\experiments\adaptation_benchmarking')
    corpus_directory = r'C:\Users\micha\Documents\Data\VariCS\varics_naming_benchmark'
    reference_directory = r'C:\Users\micha\Documents\Data\VariCS\varics_naming_reference_alignments'

acoustic_model_directory = root_directory.joinpath('acoustic_models')
dictionary_directory = root_directory.joinpath('dictionaries')

conditions = {
    'arpa': (dictionary_directory.joinpath('arpa_varics.dict'), acoustic_model_directory.joinpath('english_us_arpa.zip')),
}

adapt_folders = ['varics_naming_corrected', 'varics_naming_corrected_plus']

if __name__ == '__main__':
    for folder in adapt_folders:
        for condition, (dictionary_path, model_path) in conditions.items():
            print(folder, condition)
            output_model_path = acoustic_model_directory.joinpath(f'varics_{condition}_adapted_{folder}.zip')
            output_directory = os.path.join(root_directory, 'varics_alignments', f'{condition}_adapted_{folder}')
            if not output_model_path.exists():
                if not model_path.exists():
                    continue
                if not dictionary_path.exists():
                    continue
                print(condition)
                command = ['adapt',
                           str(corpus_root_directory.joinpath(folder)),
                           str(dictionary_path),
                           str(model_path),
                           str(output_model_path),
                           '-j', '10',
                           '--clean',
                           '--no_debug',
                           '--use_mp',
                           '--use_cutoff_model',
                           '--use_postgres',
                           '--beam', '10', '--retry_beam', '40'
                           ]
                print(command)
                mfa_cli(command, standalone_mode=False)
            if os.path.exists(output_directory):
                continue
            if not os.path.exists(model_path):
                continue
            if not os.path.exists(dictionary_path):
                continue
            command = ['align',
                       str(corpus_directory),
                       str(dictionary_path),
                       str(output_model_path),
                       str(output_directory),
                       '-j', '10',
                       '--clean',
                       '--no_debug',
                       '--use_mp',
                       '--use_cutoff_model',
                       '--use_postgres',
                       '--cleanup_textgrids',
                       #'--reference_directory',
                       #str(reference_directory),
                       '--beam', '10', '--retry_beam', '40'
                       ]
            print(command)
            mfa_cli(command, standalone_mode=False)

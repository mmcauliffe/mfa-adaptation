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

manual_percent = [0.01, 0.05, 0.1, 0.5, 1.0]

if __name__ == '__main__':
    for percent in manual_percent:
        for condition, (dictionary_path, model_path) in conditions.items():
            print(condition)
            output_model_path = acoustic_model_directory.joinpath(f'varics_{condition}_adapted_manual_{int(percent*100)}.zip')
            output_directory = os.path.join(root_directory, 'varics_alignments', f'{condition}_adapted_manual_{int(percent*100)}')
            if not output_model_path.exists():
                if not model_path.exists():
                    continue
                if not dictionary_path.exists():
                    continue
                print(condition)
                config.update_configuration({"clean": True,
                                             "num_jobs": 10, "use_mp": True,
                                             "debug":False, "use_postgres": True})
                adapter = AdaptingAligner(
                    corpus_directory=corpus_directory,
                    dictionary_path=dictionary_path,
                    acoustic_model_path=model_path,
                    reference_directory=reference_directory,
                )
                adapter.create_new_current_workflow(WorkflowType.alignment)
                adapter.setup()
                if percent < 1.0:
                    non_manual_utterances = int((1.0 - percent) * adapter.num_utterances)

                    with adapter.session() as session:
                        mapping = []
                        for u_id, in session.query(Utterance.id).order_by(sqlalchemy.sql.functions.random()).limit(non_manual_utterances):
                            mapping.append({"id": u_id, "manual_alignments": False})
                        bulk_update(session, Utterance, mapping)
                        session.commit()
                adapter.adapt()
                adapter.export_model(output_model_path)
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

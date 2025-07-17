import os
import sys
from pathlib import Path
import sqlalchemy.sql.functions
from montreal_forced_aligner.command_line.mfa import mfa_cli
from montreal_forced_aligner.alignment import AdaptingAligner
from montreal_forced_aligner.db import Utterance, bulk_update
from montreal_forced_aligner.data import WorkflowType, Language
from montreal_forced_aligner import config

if sys.platform == 'darwin':
    root_directory = Path(r'/Users/michael/Documents/Data/experiments/adaptation_benchmarking')
    corpus_directory = r'/Users/michael/Documents/Data/Buckeye'
else:
    root_directory = Path(r'D:\Data\experiments\adaptation_benchmarking')
    corpus_directory = r'D:\Data\speech\Buckeye'

mapping_directory = Path(__file__).parent.parent.joinpath("data", "evaluation_mappings")
adaptation_mapping_directory = Path(__file__).parent.parent.joinpath("data", "evaluation_mappings")

acoustic_model_directory = root_directory.joinpath('acoustic_models')
dictionary_directory = root_directory.joinpath('dictionaries')

conditions = {
    'english': (root_directory.joinpath('source_dictionaries', 'english_us_mfa.dict'), acoustic_model_directory.joinpath('english_mfa.zip')),
    'czech': (dictionary_directory.joinpath('czech.dict'), acoustic_model_directory.joinpath('czech_mfa.zip')),
    'arpa': (dictionary_directory.joinpath('arpa.dict'), acoustic_model_directory.joinpath('english_us_arpa.zip')),
    'german': (dictionary_directory.joinpath('german.dict'), acoustic_model_directory.joinpath('german_mfa.zip')),
    'mandarin': (dictionary_directory.joinpath('mandarin.dict'), acoustic_model_directory.joinpath('mandarin_mfa.zip')),
}
mapping_files = {
    'english': mapping_directory.joinpath("mfa_buckeye_mapping.yaml"),
    'czech': mapping_directory.joinpath("czech_buckeye_mapping.yaml"),
    'arpa': mapping_directory.joinpath("arpa_buckeye_mapping.yaml"),
    'german': mapping_directory.joinpath("german_buckeye_mapping.yaml"),
    'mandarin': mapping_directory.joinpath("mandarin_buckeye_mapping.yaml"),

}
adaptation_mapping_files = {
    'english': adaptation_mapping_directory.joinpath("mfa_buckeye_mapping.yaml"),
    'czech': adaptation_mapping_directory.joinpath("czech_buckeye_mapping.yaml"),
    'arpa': adaptation_mapping_directory.joinpath("arpa_buckeye_mapping.yaml"),
    'german': adaptation_mapping_directory.joinpath("german_buckeye_mapping.yaml"),
    'mandarin': adaptation_mapping_directory.joinpath("mandarin_buckeye_mapping.yaml"),

}

manual_percent = [0.01, 0.05, 0.1, 0.5, 1.0]

if __name__ == '__main__':
    for percent in manual_percent:
        for condition, (dictionary_path, model_path) in conditions.items():
            output_model_path = acoustic_model_directory.joinpath(f'{condition}_adapted_{int(percent*100)}.zip')
            output_directory = root_directory.joinpath( 'alignments', f'{condition}_adapted_manual_{int(percent*100)}')
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
                    corpus_directory=os.path.join(corpus_directory, 'buckeye_corpus_benchmark'),
                    dictionary_path=dictionary_path,
                    acoustic_model_path=model_path,
                    language=Language.unknown,
                    reference_directory=os.path.join(corpus_directory, 'buckeye_reference_alignments'),
                )
                adapter.initialize_database()
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
            if not output_directory.exists():
                command = ['align',
                           os.path.join(corpus_directory, 'buckeye_corpus_benchmark'),
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
                           '--reference_directory',
                           os.path.join(corpus_directory, 'buckeye_reference_alignments'),
                           '--custom_mapping_path',
                            mapping_files[condition],
                           '--beam', '10', '--retry_beam', '40'
                           ]
                if condition == 'mandarin':
                    command += ['--language', 'unknown']
                print(command)
                mfa_cli(command, standalone_mode=False)

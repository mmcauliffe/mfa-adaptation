import os
from pathlib import Path
from montreal_forced_aligner.command_line.mfa import mfa_cli

root_directory = Path(r'D:\Data\experiments\adaptation_benchmarking')

subset_directory = Path(r'D:\Data\experiments\adaptation_benchmarking\subset_corpora')
training_subsets = subset_directory.joinpath('train_subsets')
evaluation_subsets = subset_directory.joinpath('evaluation_subsets')

mapping_directory = Path(__file__).parent.parent.joinpath("data", "evaluation_mappings")
adaptation_mapping_directory = Path(__file__).parent.parent.joinpath("data", "evaluation_mappings")

corpus_directory = r'D:\Data\speech\Buckeye'

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

if __name__ == '__main__':
    for s in training_subsets.iterdir():
        speaker_count = s.name
        train_corpus_directory = s.joinpath(f"{speaker_count}_benchmark")
        train_reference_directory = s.joinpath(f"{speaker_count}_reference")
        evaluation_corpus_directory = evaluation_subsets.joinpath(speaker_count, f"{speaker_count}_benchmark")
        evaluation_reference_directory = evaluation_subsets.joinpath(speaker_count, f"{speaker_count}_reference")
        for condition, (dictionary_path, model_path) in conditions.items():
            manual_output_model_path = acoustic_model_directory.joinpath(f'{condition}_adapted_manual_{speaker_count}_mixed.zip')
            base_output_model_path = acoustic_model_directory.joinpath(f'{condition}_adapted_{speaker_count}.zip')
            manual_output_directory = root_directory.joinpath( 'alignments', f'{condition}_adapted_manual_{speaker_count}_mixed')
            base_output_directory = root_directory.joinpath( 'alignments', f'{condition}_adapted_{speaker_count}')
            if not manual_output_model_path.exists():
                if not model_path.exists():
                    continue
                if not dictionary_path.exists():
                    continue
                print(condition)
                command = ['adapt',
                           str(train_corpus_directory),
                           str(dictionary_path),
                           str(model_path),
                           str(manual_output_model_path),
                           '-j', '10',
                           '--clean',
                           '--no_debug',
                           '--use_mp',
                           '--use_cutoff_model',
                           '--use_postgres',
                           '--reference_directory',
                           str(train_reference_directory),
                           '--custom_mapping_path',
                            adaptation_mapping_files[condition],
                           '--beam', '10', '--retry_beam', '40'
                           ]
                if condition == 'mandarin':
                    command += ['--language', 'unknown']
                print(command)
                mfa_cli(command, standalone_mode=False)
            if not base_output_model_path.exists():
                if not model_path.exists():
                    continue
                if not dictionary_path.exists():
                    continue
                print(condition)
                command = ['adapt',
                           str(train_corpus_directory),
                           str(dictionary_path),
                           str(model_path),
                           str(base_output_model_path),
                           '-j', '10',
                           '--clean',
                           '--no_debug',
                           '--use_mp',
                           '--use_cutoff_model',
                           '--use_postgres',
                           '--beam', '10', '--retry_beam', '40'
                           ]
                if condition == 'mandarin':
                    command += ['--language', 'unknown']
                print(command)
                mfa_cli(command, standalone_mode=False)
            if not manual_output_directory.exists():
                command = ['align',
                           str(evaluation_corpus_directory),
                           str(dictionary_path),
                           str(manual_output_model_path),
                           str(manual_output_directory),
                           '-j', '10',
                           '--clean',
                           '--no_debug',
                           '--use_mp',
                           '--use_cutoff_model',
                           '--use_postgres',
                           '--cleanup_textgrids',
                           '--reference_directory',
                           str(evaluation_reference_directory),
                           '--custom_mapping_path',
                            mapping_files[condition],
                           '--beam', '10', '--retry_beam', '40'
                           ]
                if condition == 'mandarin':
                    command += ['--language', 'unknown']
                print(command)
                mfa_cli(command, standalone_mode=False)
            if not base_output_directory.exists():
                command = ['align',
                           str(evaluation_corpus_directory),
                           str(dictionary_path),
                           str(base_output_model_path),
                           str(base_output_directory),
                           '-j', '10',
                           '--clean',
                           '--no_debug',
                           '--use_mp',
                           '--use_cutoff_model',
                           '--use_postgres',
                           '--cleanup_textgrids',
                           '--reference_directory',
                           str(evaluation_reference_directory),
                           '--custom_mapping_path',
                            mapping_files[condition],
                           '--beam', '10', '--retry_beam', '40'
                           ]
                if condition == 'mandarin':
                    command += ['--language', 'unknown']
                print(command)
                mfa_cli(command, standalone_mode=False)

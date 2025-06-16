import os
from pathlib import Path
from montreal_forced_aligner.command_line.mfa import mfa_cli

root_dir = r'D:\Data\experiments\alignment_benchmarking'
mfa10_dir = r"D:\Data\models\1.0_archived"
mfa20_dir = r"D:\Data\models\2.0_archived"
mfa20a_dir = r"D:\Data\models\2.0.0a_archived"
mfa21_dir = r"D:\Data\models\2.1_trained"
mfa22_dir = r"D:\Data\models\2.2_trained"
mfa30_dir = r"D:\Data\models\3.0_trained"
mfa31_dir = r"D:\Data\models\3.1_trained"
trained22_dir = r"D:\Data\models\2.2_trained\buckeye"
trained30_dir = r"D:\Data\models\3.0_trained\buckeye"

root_directory = Path(r'D:\Data\experiments\adaptation_benchmarking')

mapping_directory = Path(__file__).parent.parent.joinpath("data", "evaluation_mappings")
adaptation_mapping_directory = Path(__file__).parent.parent.joinpath("data", "evaluation_mappings")

corpus_directory = r'D:\Data\speech\Buckeye'

acoustic_model_directory = root_directory.joinpath('acoustic_models')
dictionary_directory = root_directory.joinpath('dictionaries')

conditions = {
    #'english': (root_directory.joinpath('source_dictionaries', 'english_us_mfa.dict'), acoustic_model_directory.joinpath('english_mfa.zip')),
    'czech': (dictionary_directory.joinpath('czech_buckeye.dict'), acoustic_model_directory.joinpath('czech_mfa.zip')),
    'arpa': (dictionary_directory.joinpath('arpa_buckeye.dict'), acoustic_model_directory.joinpath('english_us_arpa.zip')),
    'german': (dictionary_directory.joinpath('german_buckeye.dict'), acoustic_model_directory.joinpath('german_mfa.zip')),
    'mandarin': (dictionary_directory.joinpath('mandarin_buckeye.dict'), acoustic_model_directory.joinpath('mandarin_mfa.zip')),
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
    for condition, (dictionary_path, model_path) in conditions.items():
        output_model_path = acoustic_model_directory.joinpath(f'{condition}_adapted.zip')
        output_directory = os.path.join(root_directory, 'alignments', f'{condition}_adapted_buckeye_dict')
        if not output_model_path.exists():
            if not model_path.exists():
                continue
            if not dictionary_path.exists():
                continue
            print(condition)
            command = ['adapt',
                       os.path.join(corpus_directory, 'buckeye_corpus_benchmark'),
                       str(dictionary_path),
                       str(model_path),
                       str(output_model_path),
                       '-j', '10',
                       '--clean',
                       '--no_debug',
                       '--use_mp',
                       '--use_cutoff_model',
                       '--use_postgres',
                       '--reference_directory',
                       os.path.join(corpus_directory, 'buckeye_reference_alignments'),
                       '--custom_mapping_path',
                        adaptation_mapping_files[condition],
                       '--beam', '10', '--retry_beam', '40'
                       ]
            if condition == 'mandarin':
                command += ['--language', 'unknown']
            print(command)
            mfa_cli(command, standalone_mode=False)
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

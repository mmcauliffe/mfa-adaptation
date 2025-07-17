import os
from pathlib import Path
from montreal_forced_aligner.command_line.mfa import mfa_cli

root_directory = Path(r'/Users/michael/Documents/Data/experiments/adaptation_benchmarking')


corpus_directory = r'/Users/michael/Documents/Data/VariCS/varics_eval_benchmark'
reference_directory = r'/Users/michael/Documents/Data/VariCS/varics_naming_reference_alignments'

acoustic_model_directory = root_directory.joinpath('acoustic_models')
dictionary_directory = root_directory.joinpath('dictionaries')

conditions = {
    'arpa': (dictionary_directory.joinpath('arpa_varics.dict'), acoustic_model_directory.joinpath('english_us_arpa.zip')),
}

if __name__ == '__main__':
    for condition, (dictionary_path, model_path) in conditions.items():
        print(condition)
        output_directory = os.path.join(root_directory, 'varics_alignments', condition)
        if os.path.exists(output_directory):
            print(output_directory)
            continue
        if not os.path.exists(model_path):
            print(model_path)
            continue
        if not os.path.exists(dictionary_path):
            print(dictionary_path)
            continue
        command = ['align',
                   str(corpus_directory),
                   str(dictionary_path),
                   str(model_path),
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

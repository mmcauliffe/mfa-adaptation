
from pathlib import Path

import yaml

from montreal_forced_aligner.command_line.mfa import mfa_cli

data_directory = Path(__file__).parent.parent.joinpath("data")

root_directory = Path(r'D:\Data\experiments\adaptation_benchmarking')

source_dictionary_path = root_directory.joinpath('source_dictionaries', "english_us_mfa.dict")
remapped_dictionary_directory = root_directory.joinpath('dictionaries')
acoustic_model_directory = root_directory.joinpath('acoustic_models')

phone_remapping_paths = {
    "czech": data_directory.joinpath("english_to_czech_phone_mapping.yaml"),
    "german": data_directory.joinpath("english_to_german_phone_mapping.yaml"),
    "mandarin": data_directory.joinpath("english_to_mandarin_phone_mapping.yaml"),
    "arpa": data_directory.joinpath("english_to_arpa_phone_mapping.yaml"),
}

buckeye_remapping_paths = {
    "czech": data_directory.joinpath("evaluation_mappings", "czech_buckeye_mapping.yaml"),
    "german": data_directory.joinpath("evaluation_mappings", "german_buckeye_mapping.yaml"),
    "mandarin": data_directory.joinpath("evaluation_mappings", "mandarin_buckeye_mapping.yaml"),
}

acoustic_model_paths = {
    "czech": acoustic_model_directory.joinpath("czech_mfa.zip"),
    "german": acoustic_model_directory.joinpath("german_mfa.zip"),
    "mandarin": acoustic_model_directory.joinpath("mandarin_mfa.zip"),
    "arpa": acoustic_model_directory.joinpath("english_us_arpa.zip"),
}

if __name__ == '__main__':
    with open(data_directory.joinpath("evaluation_mappings", "mfa_buckeye_mapping.yaml"), 'r', encoding='utf8') as f:
        mfa_phone_mapping = yaml.load(f, yaml.SafeLoader)
        for k, v in mfa_phone_mapping.items():
            if isinstance(v, str):
                mfa_phone_mapping[k] = {v}
            else:
                mfa_phone_mapping[k] = set(v)
    remapped_dictionary_directory.mkdir(parents=True, exist_ok=True)
    for dict_name, phone_remapping_path in phone_remapping_paths.items():
        if dict_name in buckeye_remapping_paths:
            with open(phone_remapping_path, 'r', encoding='utf8') as f:
                phone_mapping = yaml.load(f, yaml.SafeLoader)
            buckeye_mapping = {}
            for k, v in phone_mapping.items():
                if v not in buckeye_mapping:
                    buckeye_mapping[v] = set()
                if k in mfa_phone_mapping:
                    buckeye_mapping[v].update(mfa_phone_mapping[k])
            with open(buckeye_remapping_paths[dict_name], 'w', encoding='utf8') as f:
                for k, v in buckeye_mapping.items():
                    buckeye_mapping[k] = sorted(v)
                yaml.dump(buckeye_mapping, f, yaml.SafeDumper, allow_unicode=True)
        output_dictionary = remapped_dictionary_directory.joinpath(f"{dict_name}.dict")
        acoustic_model_path = acoustic_model_paths[dict_name]
        command = ['remap_dictionary',
                   str(source_dictionary_path),
                   str(acoustic_model_path),
                   str(phone_remapping_path),
                   str(output_dictionary),
                   '--clean',
                   ]
        print(command)
        mfa_cli(command, standalone_mode=False)
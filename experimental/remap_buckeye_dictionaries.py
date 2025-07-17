
from pathlib import Path

from montreal_forced_aligner.command_line.mfa import mfa_cli

data_directory = Path(__file__).parent.parent.joinpath("data")

root_directory = Path(r'D:\Data\experiments\adaptation_benchmarking')

source_dictionary_path = root_directory.joinpath('source_dictionaries', "buckeye.dict")
remapped_dictionary_directory = root_directory.joinpath('dictionaries')
acoustic_model_directory = root_directory.joinpath('acoustic_models')

phone_remapping_paths = {
    "arpa": data_directory.joinpath("dictionary_mappings", "buckeye_to_arpa_phone_mapping.yaml"),
    "czech": data_directory.joinpath("dictionary_mappings", "buckeye_to_czech_phone_mapping.yaml"),
    "german": data_directory.joinpath("dictionary_mappings", "buckeye_to_german_phone_mapping.yaml"),
    "mandarin": data_directory.joinpath("dictionary_mappings", "buckeye_to_mandarin_phone_mapping.yaml"),
}

acoustic_model_paths = {
    "czech": acoustic_model_directory.joinpath("czech_mfa.zip"),
    "german": acoustic_model_directory.joinpath("german_mfa.zip"),
    "mandarin": acoustic_model_directory.joinpath("mandarin_mfa.zip"),
    "arpa": acoustic_model_directory.joinpath("english_us_arpa.zip"),
}

if __name__ == '__main__':
    remapped_dictionary_directory.mkdir(parents=True, exist_ok=True)
    for dict_name, phone_remapping_path in phone_remapping_paths.items():
        output_dictionary = remapped_dictionary_directory.joinpath(f"{dict_name}_buckeye.dict")
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
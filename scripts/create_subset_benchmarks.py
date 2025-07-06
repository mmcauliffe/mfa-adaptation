from pathlib import Path
import os


corpus_directory = Path(r'D:\Data\speech\Buckeye')
benchmark_directory = corpus_directory.joinpath('buckeye_corpus_benchmark')
reference_directory = corpus_directory.joinpath('buckeye_reference_alignments')

root_directory = Path(r'D:\Data\experiments\adaptation_benchmarking\subset_corpora')
training_subsets = root_directory.joinpath('train_subsets')
evaluation_subsets = root_directory.joinpath('evaluation_subsets')

if __name__ == '__main__':
    speakers = os.listdir(benchmark_directory)
    for i in range(1, len(speakers)):
        train_speakers = speakers[:i]
        evaluation_speakers = speakers[i:]
        train_output = training_subsets.joinpath(f'{i}_speakers')
        train_benchmark = train_output.joinpath(f'{i}_speakers_benchmark')
        train_benchmark.mkdir(parents=True, exist_ok=True)
        train_reference = train_output.joinpath(f'{i}_speakers_reference')
        train_reference.mkdir(parents=True, exist_ok=True)
        for s in train_speakers:
            if not train_benchmark.joinpath(s).exists():
                os.symlink(benchmark_directory.joinpath(s), train_benchmark.joinpath(s), target_is_directory=True)
            if not train_reference.joinpath(s).exists():
                os.symlink(reference_directory.joinpath(s), train_reference.joinpath(s), target_is_directory=True)

        eval_output = evaluation_subsets.joinpath(f'{i}_speakers')
        eval_benchmark = eval_output.joinpath(f'{i}_speakers_benchmark')
        eval_benchmark.mkdir(parents=True, exist_ok=True)
        eval_reference = eval_output.joinpath(f'{i}_speakers_reference')
        eval_reference.mkdir(parents=True, exist_ok=True)
        for s in evaluation_speakers:
            if not eval_benchmark.joinpath(s).exists():
                os.symlink(benchmark_directory.joinpath(s), eval_benchmark.joinpath(s), target_is_directory=True)
            if not train_benchmark.joinpath(s).exists():
                os.symlink(benchmark_directory.joinpath(s), train_benchmark.joinpath(s), target_is_directory=True)
            if not eval_reference.joinpath(s).exists():
                os.symlink(reference_directory.joinpath(s), eval_reference.joinpath(s), target_is_directory=True)

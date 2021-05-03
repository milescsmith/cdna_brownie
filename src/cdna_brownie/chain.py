from pathlib import Path
from typing import Optional
from functools import reduce
from multiprocessing import cpu_count

import typer
import pyranges as pr
import pandas as pd

chain_app = typer.Typer()


def add_source(annotation_file: Path) -> pr.PyRanges:

    prf = pr.read_gff(annotation_file)
    samplename = pd.Series(
        data=[annotation_file.parent for _ in range(len(prf))],
        name="Source"
    )

    return prf.insert(samplename)


def merge_ranges(pr1: pr.PyRanges, pr2: pr.PyRanges) -> pr.PyRanges:

    df1 = pr1.as_df()
    df2 = pr2.as_df()

    merged_df = pd.concat([df1, df2], ignore_index=True, axis=0)

    return pr.PyRanges(df=merged_df)


@chain_app.command(name="chain_app")
def chain(
    directories: str = typer.Argument(..., help="A comma-separated list of directories (absolute or relative path) corresponding to the samples to reconcile."),
    group_filename: str = typer.Option(..., "group", "g", help="Either a single name matching the transcript group filename in each sample directory or a comma-separated list of group filenames which must be the same length and in the same order as the directories given in the `directories` argument."),
    gff_filename: str = typer.Option(..., "gff", "a", help="Either a single name matching the gff annotation filename in each sample directory or a comma-separated list of group filenames which must be the same length and in the same order as the directories given in the `directories` argument."),
    count_filename: str = typer.Option(..., "count", "c", help="Either a single name matching the count file in each sample directory or a comma-separated list of group filenames which must be the same length and in the same order as the directories given in the `directories` argument."),
    fastq_filename: Optional[str] = typer.Option(None, "fastq", "f", help="Either a single name matching the fastq in each sample directory or a comma-separated list of group filenames which must be the same length and in the same order as the directories given in the `directories` argument."),
    cpus: Optional[int] = typer.Option(0, help="Number of cpus to use when performing clustering.  Default is to use all available cpus.")
) -> None:
    """
    Chain together the files created cDNA Cupcake, reconciling the differing PBIDs
    """

    if cpus == 0:
        cpus = cpu_count()
    elif cpus > cpu_count():
        cpus = cpu_count()

    directories = [Path(_) for _ in directories.split(",")]
    datafiles = {
            "group": group_filename,
            "annotation": gff_filename,
            "counts": count_filename
        }

    if fastq_filename:
        datafiles.update({"sequence": fastq_filename})

    # If either group, annotation, or counts is given as a list,
    # split it and then join the file names with the given directory list.
    # If instead, they are given as a pattern, just join that one pattern with
    # each directory
    for x in datafiles:
        item = [_ for _ in datafiles[x].split(",")]
        if len(item) == 1:
            datafiles[x] = [a.joinpath(item[0]) for a in directories]
        elif len(item) == len(directories):
            datafiles[x] = [a.joinpath(b) for a, b in zip(directories, item)]
        else:
            raise RuntimeError(f"The number of filenames given for {x} does not match the number of directories.")

        # Raise an issue if the given files do not exist
        for i in datafiles[x]:
            if not i.exists():
                raise FileNotFoundError(f"The {x} file {i} cannot be found")

    # Add sample-specific name to each annotation file:
    annotations = map(add_source, datafiles["annotation"])

    merged_annotation = reduce(lambda i, j: merge_ranges(i, j), annotations)

    merged_annotation = merged_annotation.cluster(nb_cpus=cpus)
    
NOTE that CAT/BAT/RAT are now hosted on https://github.com/MGXlab/CAT_pack.

# CAT, BAT, and RAT

- [Introduction](#introduction)
- [Dependencies and where to get them](#dependencies-and-where-to-get-them)
- [Installation](#installation)
- [Getting started](#getting-started)
  - [Downloading preconstructed database files](#downloading-preconstructed-database-files)
  - [Creating a fresh NCBI nr or GTDB database yourself](#creating-a-fresh-ncbi-nr-or-gtdb-database-yourself)
  - [Creating a custom database](#creating-a-custom-database)
  - [Running CAT/BAT/RAT](#running-cat/bat/rat)
  - [Getting help](#getting-help)
- [Taxonomic annotation of contigs or MAGs with CAT and BAT](#taxonomic-annotation-of-contigs-or-mags-with-cat-and-bat)
  - [Interpreting the output files](#interpreting-the-output-files)
  - [Marking suggestive taxonomic assignments with an asterisk](#marking-suggestive-taxonomic-assignments-with-an-asterisk)
  - [Optimising running time, RAM, and disk usage](#optimising-running-time-ram-and-disk-usage)
  - [Examples](#examples)
- [Estimating the microbial composition with RAT](#estimating-the-microbial-composition-with-rat)
  - [Output files](#output-files)


## Introduction
**Contig Annotation Tool (CAT)** and **Bin Annotation Tool (BAT)** are pipelines for the taxonomic classification of long DNA sequences and metagenome assembled genomes (MAGs / bins) of both known and (highly) unknown microorganisms, as generated by contemporary metagenomics studies. The core algorithm of both programs involves gene calling, mapping of predicted ORFs against a protein database, and voting-based classification of the entire contig / MAG based on classification of the individual ORFs. CAT and BAT can be run from intermediate steps if files are formated appropriately.

A paper describing the algorithm together with extensive benchmarks can be found at https://doi.org/10.1186/s13059-019-1817-x. If you use CAT or BAT in your research, it would be great if you could cite us:

* *von Meijenfeldt FAB, Arkhipova K, Cambuy DD, Coutinho FH, Dutilh BE. Robust taxonomic classification of uncharted microbial sequences and bins with CAT and BAT. Genome Biology. 2019;20:217.*

**Read Annotation Tool (RAT)** estimates the taxonomic composition of metagenomes using CAT and BAT output. A manuscript describing RAT with benchmarks can be found at https://doi.org/10.1101/2023.03.22.533753. If you use RAT in your research, it would be great if you could cite:

* *von Meijenfeldt FAB, Arkhipova K, Cambuy DD, Coutinho FH, Dutilh BE. Robust taxonomic classification of uncharted microbial sequences and bins with CAT and BAT. Genome Biology. 2019;20:217.*
* *Hauptfeld E, Pappas N, van Iwaarden S, Snoek BL, Aldas-Vargas A, Dutilh BE, von Meijenfeldt FAB. Integration of taxonomic signals from MAGs and contigs improves read annotation and taxonomic profiling of metagenomes. bioRXiv. 2023*


## Dependencies and where to get them
* Python 3, https://www.python.org/.

* DIAMOND, https://github.com/bbuchfink/diamond.

* Prodigal, https://github.com/hyattpd/Prodigal.

RAT further requires (not needed for CAT and BAT):

* BWA, https://github.com/lh3/bwa.

* SAMtools, http://www.htslib.org/download/.

CAT, BAT, and RAT have been thoroughly tested on Linux systems, and should run on macOS as well.


## Installation
No installation is required. You can run CAT, BAT and RAT by supplying the absolute path:

```
$ ./CAT_pack/CAT_pack --help
```

Alternatively, if you add the files in the CAT\_pack directory to your `$PATH` variable, you can run CAT, BAT, and RAT from anywhere:

```
$ CAT_pack --version
```


## Getting started
To get started with CAT/BAT/RAT, you will have to get the database files on your system.
You can either download preconstructed database files, or generate them yourself.

### Downloading preconstructed database files

To download the database files, find the most recent version on [tbb.bio.uu.nl/tina/CAT\_pack\_prepare/](https://tbb.bio.uu.nl/tina/CAT_pack_prepare/), download and extract, and you are ready to go!

For NCBI nr:
```
$ wget tbb.bio.uu.nl/tina/CAT_pack_prepare/20231120_CAT_nr.tar.gz

$ tar -xvzf 20231120_CAT_nr.tar.gz
```

For GTDB:
```
$ wget tbb.bio.uu.nl/tina/CAT_pack_prepare/20231120_CAT_gtdb.tar.gz

$ tar -xvzf 20231120_CAT_gtdb.tar.gz
```

### Creating a fresh NCBI nr or GTDB database yourself

Instead of using the preconstructed database, you can construct a fresh database yourself. The `download` module can be used to download and process raw data, in preparation for building a new CAT pack database.
This will ensure that all input dependencies are met and correctly formatted for `CAT_pack prepare`.

Currently, two databases are supported, NCBI's nr and the Genome Taxonomy Database (GTDB) proteins.

#### NCBI non-redundant protein database (nr)

```
$ CAT_pack download -db nr -o path/to/nr_data_dir
```

Will download the fasta file with the protein sequences, their mapping to a taxid, and the taxonomy information from NCBI's ftp site.

#### [Genome Taxonomy Database (GTDB)](https://gtdb.ecogenomic.org/) proteins

```
$ CAT_pack download -db gtdb -o path/to/gtdb_data_dir
```

The files required to build a CAT pack database are provided by the [GTDB downloads page](https://gtdb.ecogenomic.org/downloads).

`CAT_pack download` fetches the necessary files and does some additional processing to get them ready for `CAT_pack prepare`:

  - The taxonomy information from GTDB is transformed into NCBI style `nodes.dmp` and `names.dmp` files.
  - Protein sequences are extracted from `gtdb_proteins_aa_reps.tar.gz` and are subjected to a round of deduplication.
The deduplication reduces the redundancy in the DIAMOND database, thus simplifying the alignment process.
Exact duplicate sequences are identified based on a combination of the MD5sum of the protein sequences and their length.
Only one representative sequence is kept, with all duplicates encoded in the fasta header.
This information is later used by `CAT_pack prepare` to assign the LCA of the protein sequence appropriately in the `.fastaid2LCAtaxid` file.
  - The mapping of all protein sequences to their respective taxonomy is created.
  - In addition, the newick formatted trees of Bacteria and Archaea are downloaded and - artificially - concatenated under a single `root` node, to produce an `all.tree` file.
This file is **not** used by the CAT pack but may come in handy for downstream analyses.

When the download and processing of the files is finished successfully you can build a CAT pack database with `CAT_pack prepare`.

For all command line options available see

```
$ CAT_pack download -h
```
and
```
$ CAT_pack prepare -h
```

### Creating a custom database

For a custom CAT pack database, you must have the following input ready before you launch a `CAT_pack prepare` run.

1. A fasta file containing all protein sequences you want to include in your database.

2. A `names.dmp` file that contains mappings of taxids to their ranks and scientific names.
The format must be the same as the NCBI standard `names.dmp` (uses `\t|\t` as field separator).

An example looks like this:

```
1	|	root	|	scientific name	|
2	|	Bacteria	|	scientific name	|
562	|	Escherichia	coli	|	scientific name	|
```

3. A `nodes.dmp` file that describes the child-parent relationship of the nodes in the taxonomy tree and their (official) rank.
The format must be the same as the NCBI standard `nodes.dmp` (uses `\t|\t` as the field separator).

An example looks like this:

```
1	|	1	|	root	|
2	|	1	|	superkingdom	|
1224	|	2	|	phylum	|
1236	| 1224	|	class	|
91437	|	1236	|	order	|
543	|	91347	|	family	|
561	|	543	|	genus	|
562	|	561	|	species	|
```

For more information on the `nodes.dmp` and `names.dmp` files, see the [NCBI taxdump_readme.txt](https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump_readme.txt).

4. A 2-column, tab-separated file containing the mapping of each sequence in the fasta file to a taxid in the taxonomy.
This file must contain the header `accession.version	taxid`.

An example looks like this

```
accession.version	taxid
protein_1	562
protein_2	123456
```

Once all of the above requirements are met you can run `CAT_pack prepare`.
All the input  needs to be explicitly specified for `CAT_pack prepare` to work, for example:

```
$ CAT_pack prepare \
--db_fasta path/to/fasta \
--names path/to/names.dmp \
--nodes path/to/nodes.dmp \
--acc2tax path/to/acc2taxid.txt.gz \
--db_dir path/to/output_dir
```

will create an `output_dir` that will look like this

```
output_dir
├── 2023-11-05_CAT_pack.log
├── db
│   ├── 2023-11-05_CAT_pack.dmnd
│   ├── 2023-11-05_CAT_pack.fastaid2LCAtaxid
│   └── 2023-11-05_CAT_pack.taxids_with_multiple_offspring
└── tax
    ├── names.dmp
    └── nodes.dmp
```

Notes:

- The two subdirs `db` and `tax` are created that contain all necessary files.
- The `nodes.dmp` and `names.dmp` in the `tax` directory are copied from their original location.
This is to ensure that the `-t` flag of CAT, BAT, and RAT work.
- The default prefix is `<YYYY-MM-DD>_CAT_pack`. You can customize it with the `--common_prefix` option.

For all command line options available see

```
$ CAT_pack prepare -h
```

### Running CAT/BAT/RAT.
The database files are needed in subsequent CAT/BAT/RAT runs. They only need to be generated/downloaded once or whenever you want to update the database.

To run CAT/BAT/RAT, respectively:
```
$ CAT_pack contigs     # Runs CAT.

$ CAT_pack bins        # Runs BAT.

$ CAT_pack reads       # Runs RAT.
```

### Getting help.
If you are unsure what options a program has, you can always add `--help` to a command. This is a great way to get you started with CAT, BAT, or RAT.

```
$ CAT_pack --help

$ CAT_pack contigs --help

$ CAT_pack summarise --help
```

If you are unsure about what input files are required, you can just run CAT/BAT/RAT, as the appropriate error messages are generated if formatting is incorrect.


## Taxonomic annotation of contigs or MAGs with CAT and BAT
After you have got the database files on your system, you can run CAT to annotate your contig set:

```
$ CAT_pack contigs -c {contigs fasta} -d {database folder} -t {taxonomy folder}
```

Multiple output files and a log file will be generated. The final classification files will be called `out.CAT.ORF2LCA.txt` and `out.CAT.contig2classification.txt`.

Alternatively, if you already have a predicted proteins fasta file and/or an alignment table for example from previous runs, you can supply them to CAT, which will then skip the steps that have already been done and start from there:

```
$ CAT_pack contigs -c {contigs fasta} -d {database folder} -t {taxonomy folder} -p {predicted proteins fasta} -a {alignment file}
```

The headers in the predicted proteins fasta file must look like this `>{contig}_{ORFnumber}`, so that CAT can couple contigs to ORFs. The alignment file must be tab-seperated, with queried ORF in the first column, protein accession number in the second, and bit-score in the 12th.

To run BAT on a set of MAGs:

```
$ CAT_pack bins -b {bin folder} -d {database folder} -t {taxonomy folder}
```

Alternatively, BAT can be run on a single MAG:

```
$ CAT_pack bins -b {bin fasta} -d {database folder} -t {taxonomy folder}
```

Multiple output files and a log file will be generated. The final classification files will be called `out.BAT.ORF2LCA.txt` and `out.BAT.bin2classification.txt`.

Similarly to CAT, BAT can be run from intermidate steps if gene prediction and alignment have already been carried out once:

```
$ CAT_pack bins -b {bin folder} -d {database folder} -t {taxonomy folder} -p {predicted proteins fasta} -a {alignment file}
```

If you have previously run CAT on the set of contigs from which the MAGs originate, you can use the previously predicted protein and alignment files to classify the MAGs.

```
$ CAT_pack contigs -c {contigs fasta} -d {database folder} -t {taxonomy folder}

$ CAT_pack bins -b {bin folder} -d {database folder} -t {taxonomy folder} -p {predicted proteins fasta from contig run} -a {alignment file from contig run}
```
This is a great way to run both CAT and BAT on a set of MAGs without needing to do protein prediction and alignment twice!

### Interpreting the output files
The ORF2LCA output looks like this:

ORF | number of hits (r: 10) | lineage | bit-score
--- | --- | --- | ---
contig\_1\_ORF1 | 7 | 1;131567;2;1783272 | 574.7

Where the lineage is the full taxonomic lineage of the classification of the ORF, and the bit-score the top-hit bit-score that is assigned to the ORF for voting. The BAT ORF2LCA output file has an extra column where ORFs are linked to the MAG in which they are found.

The contig2classification and bin2classification output looks like this:

contig or bin | classification | reason | lineage | lineage scores (f: 0.3)
--- | --- | --- | --- | ---
contig\_1 | taxid assigned | based on 14/15 ORFs | 1;131567;2;1783272 | 1.00; 1.00; 1.00; 0.78
contig\_2 | taxid assigned (1/2) | based on 10/10 ORFs | 1;131567;2;1783272;17id98711;1117;307596;307595;1890422;33071;1416614;1183438\* | 1.00;1.00;1.00;1.00;1.00;1.00;1.00;1.00;1.00;1.00;0.23;0.23
contig\_2 | taxid assigned (2/2) | based on 10/10 ORFs | 1;131567;2;1783272;1798711;1117;307596;307595;1890422;33071;33072 | 1.00;1.00;1.00;1.00;1.00;1.00;1.00;1.00;1.00;1.00;0.77
contig\_3 | no taxid assigned | no ORFs found

Where the lineage scores represent the fraction of bit-score support for each classification. **contig\_2 has two classifications.** This can happen if the *f* parameter is chosen below 0.5. For an explanation of the **starred classification**, see [Marking suggestive taxonomic assignments with an asterisk](#marking-suggestive-taxonomic-assignments-with-an-asterisk).

To add names to the taxids in either output file, run:

```
$ CAT_pack add_names -i {ORF2LCA / classification file} -o {output file} -t {taxonomy folder}
```

This will show you that for example contig\_1 is classified as Terrabacteria group. To only get official rank (*i.e.* superkingdom, phylum, ...):

```
$ CAT_pack add_names -i {ORF2LCA / classification file} -o {output file} -t {taxonomy folder} --only_official
```

Or, alternatively:

```
$ CAT_pack add_names -i {ORF2LCA / classification file} -o {output file} -t {taxonomy folder} --only_official --exclude_scores
```

If you have named a CAT or BAT classification file with official names, you can get a summary of the classification, where total length and number of ORFs supporting a taxon are calculated for contigs, and the number of MAGs per encountered taxon for MAG classification:

```
$ CAT_pack summarise -c {contigs fasta} -i {named CAT classification file} -o {output file}

$ CAT_pack summarise -i {named BAT classification file} -o {output file}
```

`CAT_pack summarise` currently does not support classification files wherein some contigs / MAGs have multiple classifications (as contig\_2 above).

### Marking suggestive taxonomic assignments with an asterisk
When we want to confidently go down to the lowest taxonomic level possible for a classification, an important assumption is that on that level conflict between classifications could have arisen. Namely, if there were conflicting classifications, the algorithm would have made the classification more conservative by moving up a level. Since it did not, we can trust the low-level classification. However, it is not always possible for conflict to arise, because in some cases no other sequences from the clade are present in the database. This is true for example for the family Dehalococcoidaceae, which in our databases is the sole representative of the order Dehalococcoidales. Thus, here we cannot confidently state that an classification on the family level is more correct than an classification on the order level. For these cases, CAT and BAT mark the lineage with asterisks, starting from the lowest level classification up to the level where conflict could have arisen because the clade contains multiple taxa with database entries. The user is advised to examine starred taxa more carefully, for example by analysing sequence identity between predicted ORFs and hits, or move up the lineage to a confident classification (i.e. the first classification without an asterisk).

If you do not want the asterisks in your output files, you can add the `--no_stars` flag to CAT or BAT.

### Optimising running time, RAM, and disk usage
CAT and BAT may take a while to run, and may use quite a lot of RAM and disk space. Depending on what you value most, you can tune CAT and BAT to maximize one and minimize others. The classification algorithm itself is fast and is friendly on memory and disk space. The most expensive step is alignment with DIAMOND, hence tuning alignment parameters will have the highest impact:

- The `-n / --nproc` argument allows you to choose the number of cores to deploy.
- You can choose to run DIAMOND in sensitive mode with the `--sensitive` flag. This will increase sensitivity but will make alignment considerably slower.
- Setting the `--block_size` parameter lower will decrease memory and temporary disk space usage. Setting it higher will increase performance.
- For high memory machines, it is adviced to set `--index_chunks` to 1 (currently the default). This parameter has no effect on temprary disk space usage.
- You can specify the location of temporary DIAMOND files with the `--tmpdir` argument.

### Examples
Getting help for running the prepare utility:

```
$ CAT_pack prepare --help
```

Run CAT on a contig set with default parameter settings deploying 16 cores for DIAMOND alignment. Name the contig classification output with official names, and create a summary:

```

$ CAT_pack contigs -c contigs.fasta -d db/ -t tax/ -n 16 --out_prefix first_CAT_run

$ CAT_pack add_names -i first_CAT_run.contig2classification.txt -o first_CAT_run.contig2classification.official_names.txt -t tax/ --only_official

$ CAT_pack summarise -c contigs.fasta -i first_CAT_run.contig2classification.official_names.txt -o CAT_first_run.summary.txt
```

Run BAT on the set of MAGs that was binned from these contigs, reusing the protein predictions and DIAMOND alignment file generated previously during the contig classification:

```
$ CAT_pack bins -b bins/ -d db/ -t tax/ -p first_CAT_run.predicted_proteins.faa -a first_CAT_run.alignment.diamond -o first_BAT_run
```

Run the contig classification algorithm again with custom parameter settings, and name the output with all names in the lineage, excluding the scores:

```
$ CAT_pack contigs --range 5 --fraction 0.1 -c contigs.fasta -d db/ -t tax/ -p first_CAT_run.predicted_proteins.faa -a first_CAT_run.alignment.diamond -o second_CAT_run

$ CAT_pack add_names -i second_CAT_run.contig2classification.txt -o second_CAT_run.contig2classification.names.txt -t tax/ --exclude_scores

```

Run BAT on the set of MAGs with custom parameter settings, suppressing verbosity and not writing a log file. Next, add names to the ORF2LCA output file:

```
$ CAT_pack bins -r 3 -f 0.1 -b bins/ -s .fa -d db/ -t tax/ -p first_CAT_run.predicted_proteins.faa -a first_CAT_run.alignment.diamond --o second_BAT_run --quiet --no_log

$ CAT_pack add_names -i second_BAT_run.ORF2LCA.txt -o second_BAT_run.ORF2LCA.names.txt -t tax/
```

#### Identifying contamination/mis-binned contigs within a MAG
We often use the combination of CAT / BAT to explore possible contamination within a MAG.

```
$ CAT_pack contigs -c ../bins/interesting_MAG.fasta -d db/ -t tax/ -o CAT.interesting_MAG

$ CAT_pack bins -b ../bins/interesting_MAG.fasta -d db/ -t tax/ -p CAT.interesting_MAG.predicted_proteins.faa -a CAT.interesting_MAG.alignment.diamond -o BAT.interesting_MAG
```

Contigs that have a different taxonomic signal than the MAG classification are probably contamination.

Alternatively, you can look at contamination from the MAG perspective, by setting the *f* parameter to a low value:

```
$ CAT_pack bins -f 0.01 -b ../bins/interesting_MAG.fasta -d db/ -t tax/ -o BAT.interesting_MAG

$ CAT_pack add_names -i BAT.interesting_MAG.bin2classification.txt -o BAT.interesting_MAG.bin2classification.names.txt -t tax/
```

BAT will output any taxonomic signal with at least 1% support. Low scoring diverging signals are clear signs of contamination!


## Estimating the microbial composition with RAT
RAT estimates the taxonomic composition of metagenomes by integrating taxonomic signals from MAGs, contigs, and reads. RAT has been added to the CAT pack from version 6.0.
To use RAT, you need the CAT pack database files (see [Getting started](#getting-started) for more information).

RAT makes an integrated profile using MAGs/bins, contigs, and reads. To specify which elements should be integrated, use the `--mode` argument. Possible letters for `--mode` are `m` (for MAGs), `c` (for contigs), and `r` (for reads). All combinations of the three letters are possible, except `r` alone.
To run RAT's complete workflow, specify the mode, read files, contig files, bin folder, and database files:

```
$ CAT_pack reads --mode mcr -b bin_folder/ -c contigs.fasta -1 forward_reads.fq.gz -2 reverse_reads.fq.gz -d db/ -t tax/
```

Currently, RAT supports single read files as well as paired-end read files. Interlaced read files are currently not supported. RAT will run CAT and BAT on the contigs and MAGs, will map the reads back to the contigs, and then try to annotate any unmapped reads separately.
If you already have a sorted mapping file, you can supply it and RAT will skip the mapping step:

```

$ CAT_pack reads --mode mcr -b bin_folder/ -c contigs.fasta --bam1 mapping_file_sorted.bam -1 forward_reads.fq.gz -2 reverse_reads.fq.gz -d db/ -t tax/
```

If CAT and/or BAT have already been run on your data, you can supply the output files to RAT to skip the CAT and BAT runs:

```

$ CAT_pack reads --mode mcr -b bin_folder/ -c contigs.fasta -1 forward_reads.fq.gz -2 reverse_reads.fq.gz -d db/ -t tax/ --c2c CAT_contig2classification_file.txt --b2c BAT_bin2classification_file.txt
```

Similarly, if a previous RAT run crashed after the unmapped reads have already been aligned to the database with diamond, you can supply the intermediate files to continue the run:

```

$ CAT_pack reads --mode mcr -b bin_folder/ -c contigs.fasta -1 forward_reads.fq.gz -2 reverse_reads.fq.gz -d db/ -t tax/ --c2c CAT_contig2classification_file.txt --b2c BAT_bin2classification_file.txt --alignment_unmapped unmapped_alignment_file.diamond
```

After a RAT run is finished, you can run add_names on the abundance files (only for RAT runs with nr database):

```

$ CAT_pack add_names -i RAT.completete_abundance_file.txt -o RAT.completete_abundance_file_with_names.txt -t tax/ 
```

Similar to CAT and BAT, the paths to all dependencies can be supplied via an argument:

```

$ CAT_pack reads --mode mcr -b bin_folder/ -c contigs.fasta -1 forward_reads.fq.gz -2 reverse_reads.fq.gz -d db/ -t tax/ --path_to_samtools /path/to/samtools
```

### Output files
The RAT output consists of:

- A log file.
- All CAT output files for the contig fasta.
- All BAT output files for the MAGs (except DIAMOND alignment and protein fasta).
- A table that contains the abundance of each MAG.
- A table that contains all detected taxa and their abundance in the sample.
- A table that contains the lineage for each read, as well as which step the annotation was made in (optional without `r` in `--mode`).
- A table that contains the abundance of each contig in the contig fasta.
- A fasta containing the sequences of all unmapped reads and contigs that could not be annotated by CAT.
- The diamond alignment of unmapped reads and unannotated contigs.
- A table that contains the annotations for unmapped reads and (previously) unannotated contigs.

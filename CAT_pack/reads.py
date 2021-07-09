#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 11:07:07 2020

@author: tina
"""

import os
import subprocess
import argparse
import datetime
import multiprocessing
import sys
import decimal

import about
import check
import shared
import tax



def parse_arguments():
    parser = argparse.ArgumentParser(
            prog='CAT reads',
            description='Run Read Annotation Tool (RAT).',
            # @Tina: Should the explanation on how to use RAT be in the description? Right now the 'Run Read Annotation Tool' is at a little weird position. Also if you forget one argument (say -c) you'll not only get the help message but also the entire usage which is a little overkill.
            # @Tina: I do like this explanation of complete and partial workflows... Maybe we should add it to the other CAT pack as well?
            usage='CAT reads -c -t [options] [-h / --help]\n\n'
            'Complete RAT workflow (perform read mapping, run CAT, BAT, and RAT): '
            'Supply contigs, reads, database folder, taxonomy folder, and bin folder.\n\n'
            'Partial workflows:\n'
            'If you have already mapped your reads, you can supply the sorted mapping '
            'file and no read mapping will be performed.\n'
            'If you have already run CAT and/or BAT, you can supply the output '
            'files (contig2classification, bin2classification) and the path to the '
            'taxonomy folder instead.\n'
            'If you prefer not to use bin classification, do not supply the path '
            'to a bin folder.',
            add_help=False)
    
    required = parser.add_argument_group('Required arguments')
    shared.add_argument(required, 'contigs_fasta', True)
    shared.add_argument(required, 'taxonomy_folder', True)
    
    optional = parser.add_argument_group('Optional arguments')
    shared.add_argument(optional, 'out_prefix', False, default='./out.RAT')
    shared.add_argument(optional, 'read_file1', False)
    shared.add_argument(optional, 'read_file2', False)
    shared.add_argument(optional, 'bam_file1', False)
    shared.add_argument(optional, 'bam_file2', False)
    shared.add_argument(optional, 'bin_folder', False)
    shared.add_argument(optional, 'bin_suffix', False)
    shared.add_argument(optional, 'contig2classification', False)
    shared.add_argument(optional, 'bin2classification', False)
    shared.add_argument(optional, 'read2classification', False)
    shared.add_argument(optional, 'mapping_quality', False, default=2)
    shared.add_argument(optional, 'read_classification', False)
    shared.add_argument(optional, 'path_to_bwa', False, default='bwa')
    shared.add_argument(optional, 'path_to_samtools', False, default='samtools')
    shared.add_argument(optional, 'nproc', False,
            default=multiprocessing.cpu_count())
    shared.add_argument(optional, 'force', False)
    shared.add_argument(optional, 'quiet', False)
    shared.add_argument(optional, 'verbose', False)
    shared.add_argument(optional, 'no_log', False)
    shared.add_argument(optional, 'help', False)
    
    CAT_args = parser.add_argument_group('CAT/BAT-specific arguments')
    shared.add_argument(CAT_args, 'database_folder', False)
    shared.add_argument(CAT_args, 'r', False, default=decimal.Decimal(10))
    shared.add_argument(CAT_args, 'f', False, default=decimal.Decimal(0.5))
    shared.add_argument(CAT_args, 'path_to_prodigal', False,
            default='prodigal')
    shared.add_argument(CAT_args, 'path_to_diamond', False, default='diamond')
    shared.add_argument(CAT_args, 'no_stars', False)
    shared.add_argument(CAT_args, 'IkwId', False)
    
    dmnd_args = parser.add_argument_group('DIAMOND specific optional arguments')
    shared.add_all_diamond_arguments(dmnd_args, add_nproc=False)
                          
    (args, extra_args) = parser.parse_known_args()
    extra_args = [arg for (i, arg) in enumerate(extra_args) if
        (i, arg) != (0, 'reads')]
    if len(extra_args) > 0:
        sys.exit('error: too many arguments supplied:\n{0}'.format(
            '\n'.join(extra_args)))

    # Add extra arguments.
    shared.expand_arguments(args)
    
    if not args.contigs_fasta:
        sys.exit('error: no contigs_fasta supplied.')
    
    if not args.bam_file1 and not args.read_file1:
        sys.exit('error: you have to supply either a sorted bam file or '
                 'two paired-end read files!')
    if not args.contig2classification and not args.database_folder:
        sys.exit('error: please provide either a contig2classification file '
                 'or the path to the CAT database_folder!')
    if args.bin_folder and not args.bin2classification and not args.database_folder:
        sys.exit('error: please provide either a bin2classification file or '
                 'the path to the CAT database_folder for bin classification!')
    if args.bin2classification and not args.bin_folder:
        sys.exit('error: bin2classification file but no bin_folder supplied. '
                 'RAT requires -b/--bin_folder to include bins in annotation!')
    
    
    return args





def run():
    args = parse_arguments()

    message = '# CAT v{0}.'.format(about.__version__)
    shared.give_user_feedback(message, args.log_file, args.quiet,
        show_time=False)

    
    # Checks
    
    
    
    errors = []
    
    errors.append(
            check.check_input_file(args.contigs_fasta, args.log_file, args.quiet))
    
    if args.read_file1:
        errors.append(
            check.check_input_file(args.read_file1, args.log_file, args.quiet))
    if args.read_file2:
        errors.append(
            check.check_input_file(args.read_file2, args.log_file, args.quiet))
    if args.bam_file1:
        errors.append(
            check.check_input_file(args.bam_file1, args.log_file, args.quiet))
    if args.contig2classification:
        errors.append(
            check.check_input_file(args.contig2classification, args.log_file, args.quiet))
    if args.bin2classification:
        errors.append(
            check.check_input_file(args.bin2classification, args.log_file, args.quiet))
    
    
    
    if not args.force:
        if args.read_file1:
            outf_bwamem='{0}.{1}.bwamem'.format(args.out_prefix+'.'+
                                        os.path.split(args.contigs_fasta)[-1], 
                                        os.path.split(args.read_file1)[-1])
            print(outf_bwamem)
            errors.append(
                    check.check_output_file(
                        outf_bwamem, args.log_file, args.quiet))
            errors.append(
                    check.check_output_file(
                        outf_bwamem + '.bam', args.log_file, args.quiet))
            errors.append(
                    check.check_output_file(
                        outf_bwamem + '.sorted', args.log_file, args.quiet))
        if not args.contig2classification:
            outf_cat_protein_faa='{0}.CAT.predicted_proteins.faa'.format(args.out_prefix)
            outf_cat_c2c='{0}.CAT.contig2classification.txt'.format(args.out_prefix)
            outf_cat_alignment='{0}.CAT.alignment.diamond'.format(args.out_prefix)
            errors.append(
                    check.check_output_file(
                        outf_cat_protein_faa, args.log_file, args.quiet))
            errors.append(
                    check.check_output_file(
                        outf_cat_c2c, args.log_file, args.quiet))
            errors.append(
                    check.check_output_file(
                        outf_cat_alignment, args.log_file, args.quiet))
        if args.bin_folder and not args.bin2classification:
            outf_bat_protein_faa='{0}.BAT.{1}.predicted_proteins.faa'.format(args.out_prefix,
                                                                         'concatenated')
            outf_bat_b2c='{0}.BAT.bin2classification.txt'.format(args.out_prefix)
            outf_bat_alignment='{0}.BAT.{1}.alignment.diamond'.format(args.out_prefix,
                                                                         'concatenated')
            errors.append(
                    check.check_output_file(
                        outf_bat_protein_faa, args.log_file, args.quiet))
            errors.append(
                    check.check_output_file(
                        outf_bat_b2c, args.log_file, args.quiet))
            errors.append(
                    check.check_output_file(
                        outf_bat_alignment, args.log_file, args.quiet))

        
    errors.append(
            check.check_samtools_binaries(
                args.path_to_samtools, args.log_file, args.quiet))
    if not args.bam_file1:
        errors.append(
            check.check_bwa_binaries(
                args.path_to_bwa, args.log_file, args.quiet))
    if not args.contig2classification or (args.bin_folder and not args.bin2classification):
        errors.append(
            check.check_prodigal_binaries(
                args.path_to_prodigal, args.log_file, args.quiet))
        errors.append(
            check.check_diamond_binaries(
                args.path_to_diamond, args.log_file, args.quiet))
    
    if True in errors:
        sys.exit(1)
    
    
    
    # First: run bwa mem, samtools view and samtools sort if there is no bam file
    bam_files=[]
    if not args.bam_file1:
        message = (
                '\n'
                'RAT is running. Mapping reads against assembly with bwa mem.\n')
        shared.give_user_feedback(message, args.log_file, args.quiet,
                show_time=False)
            
        reads=[args.read_file1]
            
        if args.read_file2:
            reads.append(args.read_file2)
        else:
            message = (
                'WARNING: only one read file supplied! Currently RAT does not '
                'support interlaced read files. If you are working with '
                'paired-end reads, please provide a reverse read-file!' )
            shared.give_user_feedback(message, args.log_file, args.quiet, 
                                      show_time=False)

        shared.run_bwa_mem(args.path_to_bwa, args.path_to_samtools,
                              args.contigs_fasta, reads, args.out_prefix,
                              args.nproc, args.log_file)

            
            
        bam_files.append('{0}.{1}.bwamem.sorted'.format(args.out_prefix+'.'+os.path.split(args.contigs_fasta)[-1], 
                        os.path.split(args.read_file1)[-1]))
    else:
        bam_files.append(args.bam_file1)
        if args.bam_file2:
            bam_files.append(args.bam_file2)
            message = (
                'WARNING: you provided two bam files. Consider mapping forward '
                'and reverse reads together or repeating the mapping step with '
                'RAT!')
            shared.give_user_feedback(message, args.log_file, args.quiet, 
                                      show_time=False)

    
    # Process bin folder
    contig2bin={}
    
    if args.bin_folder:
        message = 'Bin folder supplied. Processing bin folder.'
        shared.give_user_feedback(message, args.log_file, args.quiet,
                show_time=True)

        bins=process_bin_folder(args.bin_folder, args.bin_suffix)
        contig2bin=invert_bin_dict(bins)


    # Run BAT on folder if bin folder but not BAT_file is supplied
    # Or process BAT file if it is supplied
    b2c={}
    
    if args.bin_folder and args.bin2classification:
        message = (
                'bin2classification file supplied. Processing bin '
                'classifications.')
        shared.give_user_feedback(message, args.log_file, args.quiet,
                show_time=True)
        b2c=process_CAT_table(args.bin2classification, args.nodes_dmp, 
                              args.log_file, args.quiet)
    
    elif args.bin_folder and not args.bin2classification:
        message = ('No bin2classification file supplied. Running BAT on bin '
                   'folder.')
        shared.give_user_feedback(message, args.log_file, args.quiet,
                show_time=True)

        shared.run_BAT(args.bin_folder, args.database_folder, args.taxonomy_folder,
                       args.log_file, args.quiet, args.nproc, args.f, args.r, 
                       args.path_to_prodigal, args.path_to_diamond, args.out_prefix, 
                       args.bin_suffix)
        b2c=process_CAT_table('{0}.BAT.bin2classification.txt'.format(args.out_prefix), 
                              args.nodes_dmp, args.log_file, args.quiet)
        
    elif not args.bin_folder:
        message = 'No bin folder supplied. No bin classification will be made.'
        
        shared.give_user_feedback(message, args.log_file, args.quiet,
                show_time=False)
    
    
    # Run CAT or process CAT output file
    if args.contig2classification:
        message = (
                'contig2classification file supplied. Processing contig '
                'classifications.')
        shared.give_user_feedback(message, args.log_file, args.quiet,
                show_time=True)
        c2c=process_CAT_table(args.contig2classification, args.nodes_dmp, 
                              args.log_file, args.quiet)
    else:
        message = (
                'No contig2classification file supplied. Running CAT on '
                'contigs.')
        shared.give_user_feedback(message, args.log_file, args.quiet,
                show_time=True)
        shared.run_CAT(args.contigs_fasta, args.database_folder, 
                       args.taxonomy_folder, args.log_file, args.quiet, 
                       args.nproc, args.f, args.r, args.path_to_prodigal, 
                       args.path_to_diamond, args.out_prefix)
        c2c=process_CAT_table('{0}.CAT.contig2classification.txt'.format(args.out_prefix), 
                              args.nodes_dmp, args.log_file, args.quiet)
    
    
    # Process BAM files and grab unmapped reads
    message = 'Processing mapping file(s).\n'
    shared.give_user_feedback(message, args.log_file, args.quiet,
            show_time=True)
    # @Tina: we could just supply the first argument as a list, that will save you the conditional.
    if len(bam_files)==2:
        reads, unmapped_reads, sum_of_reads, paired = process_bam_file(bam_files[0], 
                                                                       bam_files[1], 
                                                                       mapping_quality=args.mapping_quality)
    else:
        reads, unmapped_reads, sum_of_reads, paired = process_bam_file(bam_files[0], 
                                                                       mapping_quality=args.mapping_quality)
    
    
    # Get lengths of the contigs from contigs file    
    contig_length_dict, sum_of_nucleotides = get_contig_lengths(args.contigs_fasta)
    # make contig_dict
    contigs, reads, max_primary=make_contig_dict(reads, bam_files, paired, contig2bin)
    

    # Write the tax tables and get unclassified contigs for sensitive aligner (later)
    message = 'Writing output tables.'
    shared.give_user_feedback(message, args.log_file, args.quiet,
            show_time=True)
    
    unclassified_contigs=make_tax_table(c2c, 
                                        contigs, 
                                        contig_length_dict, 
                                        contig2bin, b2c, 
                                        sum_of_nucleotides, 
                                        sum_of_reads, 
                                        args.out_prefix)
    make_bin_table(contig2bin, 
                   contigs, 
                   contig_length_dict, 
                   sum_of_reads, 
                   args.out_prefix)
    
       
    
    # Finally: Optional: Classify reads and write per_read table
    if args.read2classification:
        reads=classify_reads(reads, c2c, b2c)
        write_read_table(reads, args.out_prefix, max_primary)
    
    message = (
            '\n-----------------\n\n'
            '[{0}] RAT is done!'.format(
                datetime.datetime.now()))
    shared.give_user_feedback(message, args.log_file, args.quiet,
            show_time=False)
    return



def classify_reads(read_dict, contig2classification, bin2classification):
    worked=0
    for read in read_dict:
        for r in range(len(read_dict[read]['contig'])):
            # If there is bin classification, store it
            if bin2classification:
                try:
                    if read_dict[read]['bin'][r]=='unbinned':
                        read_dict[read]['taxon_bin'].append('')
                    else:
                        read_dict[read]['taxon_bin'].append(';'.join(bin2classification[read_dict[read]['bin'][r]][0]))
                    worked+=1
                except IndexError:
                    print(r)
                    sys.exit('Worked: {}'.format(worked))
            
            contig=read_dict[read]['contig'][r]
            if contig2classification==[] or len(contig2classification[contig])<2 or len(contig2classification[contig][0])==2 and contig2classification[contig][0][1]=='131567':
                read_dict[read]['taxon_contig'].append('')
            else:
                read_dict[read]['taxon_contig'].append(';'.join(contig2classification[contig][0]))
    return read_dict



def write_read_table(read_dict, sample_name, max_primary):
    # Takes the read dictionary with bin lineage and contig lineage and writes
    # annotation for each read and each tier of annotation into a file
    read_table=sample_name + '.read2classification.txt'
    
    with open(read_table, 'w') as outf:
        outf.write('## command: {}\n'.format(' '.join(sys.argv)))
        outf.write('# read\tclassification\tbin classification\t'
                   'contig classification\t'
                   #'[aligner] unclassified contig\t[aligner] unclassified read\n'
                   )
        for read in read_dict:

            for c in range(len(read_dict[read]['contig'])):
                try:
                    b_taxon=read_dict[read]['taxon_bin'][c]
                    c_taxon=read_dict[read]['taxon_contig'][c]
                    
                except IndexError:
                    b_taxon=''
                    c_taxon=''
                    
                outf.write('{0}\t{1}\t{2}\t{3}\n'.format(read,
                           'taxid assigned', b_taxon, c_taxon))
            n=max_primary-len(read_dict[read]['contig'])
            if len(read_dict[read]['contig'])<max_primary:
                outf.write(n*'{0}\t{1}\n'.format(read, 'no taxid assigned'))
    return



def make_bin_table(contig2bin, 
                   contig_dict, 
                   contig_length_dict, 
                   total_reads, 
                   out_prefix):
    # Include lineage?
    bin_data={}
    bin_file='{0}.bin.reads.txt'.format(out_prefix)
    
    with open(bin_file, 'w') as op:
        op.write('## command: {}\n'.format(' '.join(sys.argv)))
        op.write('# bin\tnumber of reads\tfraction of reads\tbin length\t'
                 'corrected fraction\n')
        for contig in contig_dict:
            if contig in contig2bin:
                bin_id=contig2bin[contig]
            else:
                bin_id='unbinned'
            if not bin_id in bin_data:
                bin_data[bin_id]={
                    'n_reads': 0,
                    'n_nucleotides': 0
                    }
            # if contig is in contig_dict, then reads have mapped to it, otherwise
            # no reads have mapped to it
            try:
                bin_data[bin_id]['n_reads']+=contig_dict[contig]
                bin_data[bin_id]['n_nucleotides']+=contig_length_dict[contig]
            except KeyError:
                pass
            
        divisor=get_proper_fraction(bin_data, total_reads)
        for bin_id in bin_data:
            read_fraction=bin_data[bin_id]['n_reads']/total_reads
            if bin_data[bin_id]['n_nucleotides']!=0:
                corrected_frac=(read_fraction/bin_data[bin_id]['n_nucleotides'])/divisor
            else:
                corrected_frac=0
            op.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(bin_id, 
                                                bin_data[bin_id]['n_reads'], 
                                                read_fraction, 
                                                bin_data[bin_id]['n_nucleotides'], 
                                                corrected_frac))
    return





def make_tax_table(c2c_dict, 
                   contig_dict, 
                   contig_length_dict, 
                   contig2bin, 
                   bin2classification, 
                   sum_of_nucleotides, 
                   total_reads, 
                   sample_name):
    """
    Makes a dictionary that keeps all the necessary info in the same place
    Writes contig table
    Writes table with all classifications including subspecies
    """
    RAT_contig_header=('# contig\tnumber of reads\tfraction of reads\t'
                       'contig_length\tAverage Coveraget\tlineage\t'
                       'lineage ranks\tlineage scores\n')
                       
    RAT_file_header=('# lineage\tnumber of reads\tfraction of reads\t'
                     'taxon length\tlineage ranks\n')
    
    taxon_dict={}
    unclassified={
            'contigs': set(),
            'n_reads': 0,
            'n_nucleotides': 0
            }
    
    for contig in contig_dict:
        
        # If the contig name is '*', that means that a read is unmapped, gets
        # added to unmapped, which is just a number, and just gets a fraction
        # of reads. This does not get a fraction of nucleotides, because we are
        # talking about reads and we assume the number of nucleotides in the
        # environment is the number of nucleotides in the assembly
        if contig=='*':
            unmapped=contig_dict[contig]
        
        # If the contig is in contig2bin, that means that it is binned and therefore
        # will be assigned the lineage of the bin and not the contig
        elif contig in contig2bin:
            taxon=';'.join(bin2classification[contig2bin[contig]][0])
            if taxon not in taxon_dict:
                taxon_dict[taxon]={
                        'n_reads': 0,
                        'n_nucleotides': 0,
                        'ranks': bin2classification[contig2bin[contig]][1]
                        }
            # add number of reads that map to the contig to the taxon and
            # add nucleotides of the contig to the taxon
            taxon_dict[taxon]['n_reads']+=contig_dict[contig]
            taxon_dict[taxon]['n_nucleotides']+=contig_length_dict[contig]
            
        # If C2C[contig] is an empty list, it's unclassified
        # If the length of the list of classified tax_ids is shorter than 2, the
        # contig is not classified at superkingdom level and therefore, for our
        # purpose unclassified
        elif c2c_dict[contig]==[] or len(c2c_dict[contig][0])<2 or len(c2c_dict[contig][0])==2 and c2c_dict[contig][0][1]=='131567':
            unclassified['n_reads']+=contig_dict[contig]
            unclassified['n_nucleotides']+=contig_length_dict[contig]
        
        # The other possibility is that the contig is unbinned, but classified
        else:
            taxon=';'.join(c2c_dict[contig][0])
            if taxon not in taxon_dict:
                taxon_dict[taxon]={
                        'n_reads': 0,
                        'n_nucleotides': 0,
                        'ranks': c2c_dict[contig][1]
                        }
            
            # add number of reads that map to the contig to the taxon and
            # add nucleotides of the contig to the taxon
            taxon_dict[taxon]['n_reads']+=contig_dict[contig]
            taxon_dict[taxon]['n_nucleotides']+=contig_length_dict[contig]
    
    unmapped_line='{0}\t{1}\t{2}\n'.format('unmapped', unmapped,
                                           unmapped/total_reads)
    unclassified_line='{0}\t{1}\t{2}\t{3}\t'.format('unclassified',
                       unclassified['n_reads'],
                       unclassified['n_reads']/total_reads,
                       unclassified['n_nucleotides'])
    
    
    # write the output tables for contigs:
    with open('{0}.contig.abundance.txt'.format(sample_name), 'w') as outf_contig:
        outf_contig.write('## command: {}\n'.format(' '.join(sys.argv)))
        outf_contig.write(RAT_contig_header)
        # @Tina: not to work with decimals instead of floats.
        # get the divisor to make corrected fraction add up to 1

        divisor=get_proper_fraction(contig_dict, total_reads, unclassified, contig_length_dict)
        outf_contig.write(unmapped_line)
        for contig in contig_dict:
            if not contig=='*':
                read_frac=contig_dict[contig]/total_reads
                corrected_frac=(read_frac/contig_length_dict[contig])/divisor
                # If contig is binned, then get the lineage of the bin and not the contig
                try:
                    if contig in contig2bin:
                        lineage=';'.join(bin2classification[contig2bin[contig]][0])
                        rank_list=';'.join(bin2classification[contig2bin[contig]][1])
                        scores=';'.join(bin2classification[contig2bin[contig]][2])
                        
                    else:
                        lineage=';'.join(c2c_dict[contig][0])
                        rank_list=';'.join(c2c_dict[contig][1])
                        scores=';'.join(c2c_dict[contig][2])
                        
                except IndexError:
                    lineage=''
                    rank_list=''
                    scores=''
                outf_contig.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\n'.format(
                        contig, contig_dict[contig], read_frac, 
                        contig_length_dict[contig], corrected_frac, lineage, 
                        rank_list, scores))
    
    
    # write output table for complete lineage
    with open('{0}.complete.abundance.txt'.format(sample_name), 'w+') as outf_complete:
        outf_complete.write('## command: {}\n'.format(' '.join(sys.argv)))
        outf_complete.write(RAT_file_header)
        outf_complete.write(unmapped_line)
        outf_complete.write(unclassified_line)

        if unclassified['n_reads']!=0:
            outf_complete.write('{0}\n'.format(((unclassified['n_reads']/total_reads)/unclassified['n_nucleotides'])/divisor))
        else:
            outf_complete.write('0\n')
        
        for taxon in taxon_dict:
            read_frac=taxon_dict[taxon]['n_reads']/total_reads

            outf_complete.write('{0}\t{1}\t{2}\t{3}\t{4}\n'.format(
                    taxon, 
                    taxon_dict[taxon]['n_reads'],
                    read_frac, 
                    taxon_dict[taxon]['n_nucleotides'],
                    # add average genome size
                    ';'.join(taxon_dict[taxon]['ranks'])))
    
    
    return unclassified['contigs']



def get_proper_fraction(rank_dict, 
                        total_reads, 
                        unclassified={}, 
                        contig_length_dict={}):
    divisor=0
    if unclassified and unclassified['n_reads']!=0:
        divisor+=(unclassified['n_reads']/total_reads)/unclassified['n_nucleotides']
    try:
        for taxon in rank_dict:
            if rank_dict[taxon]['n_nucleotides']!=0:
                divisor+=(rank_dict[taxon]['n_reads']/total_reads)/rank_dict[taxon]['n_nucleotides']
    except TypeError:
        for contig in rank_dict:
            if not contig=='*':
                divisor+=(rank_dict[contig]/total_reads)/contig_length_dict[contig]
    return divisor



def process_CAT_table(CAT_output_table, 
                      nodes_dmp, 
                      log_file, 
                      quiet):
    """
    takes CAT contig2classification or bin2classification table and taxonomy 
    nodes file as input; returns a dictionary that contains the complete 
    lineage for each contig/bin:
    (list of tuples of the format [(tax_id1,tax_id2...), 
                                   (rank1,rank2,...), 
                                   (score1,score2...)])
    bin id contains the file extension!
    """
    c2c={}
    
    # get rank for each taxid
    taxid2rank=tax.import_nodes(nodes_dmp, log_file, quiet)[1]
    
    with open(CAT_output_table, 'r') as contigs:
        for contig in contigs:
            
            # if it is not the first line, get contig id, lineage and lineage scores
            if not contig.startswith('# '):
                contig_id=contig.strip().split('\t')[0]
                c2c[contig_id]=[]
                
                # Build a list of tuples for the lineage:
                # (tax_id1,tax_id2...), (rank1,rank2,...), (score1,score2...)]
                if len(contig.split('\t'))>3:
                    tax_ids=contig.split('\t')[3].strip().split(';')
                    scores=contig.split('\t')[4].strip().split(';')
                    c2c[contig_id]=[tuple([t for t in tax_ids]),
                                   tuple([taxid2rank[t.strip('*')] for t in tax_ids]),
                                   tuple([s for s in scores])]
                                        
    return c2c
            




def process_bam_file(BAM_fw_file, BAM_rev_file=False, path_to_samtools='samtools', mapping_quality=40):
    """
    # function that processes the bam file(s) by picking out the primary alignments
    # and storing the contigs that the forward and reverse reads map to. If only
    # one file is given, checks whether it's paired or not before it counts the
    # unmapped reads.
    # Keeps track of unmapped reads: If paired read file, then if checks the flag
    # for whether the unmapped read is the first or the second in the pair; if
    # it's single reads, it just fills up the fw key of the dictionary, and if
    # there is a reverse file, then the reverse file only adds to the rev key.
    """
    read_dict={}
    unmapped_reads={'fw': set(), 'rev': set()}
    
    # open alignment file with samtools, so that we don't need pysam dependency
    cmd=[path_to_samtools, 'view', BAM_fw_file]
    proc=subprocess.Popen(cmd, stdout=subprocess.PIPE)

    # check whether it is a paired bam file by checking the flags for "read paired"
    # flag and setting paired to true if it finds it
    paired=False


    # build read_dictionary with list of 0-2 contigs that each read/mate maps to
    # @Tina: call this mapping instead of read?
    for read in proc.stdout:
        read=read.decode("utf-8").rstrip().split('\t')
        read_id, flag, contig, score=read[0], int(read[1]), read[2], int(read[4])
        
        if bin(flag)[-1]=='1' and not paired:
            # @Tina: Why do you put the 'and not paired' in there? Is it quicker
            # Than just overwriting paired everytime? If that's true it's probably
            # even quicker still to swap the arguments: if not paired and bin(fl etc...
            # Python will only go the second (more costly) if the first is met.
            # Also are ALL reads flagged with [-1] == '1' if they come from
            # paired fastq files? Because if they do we can just do this on the
            # first line only, and if they don't we might have a problem later
            # because we assume pair information in the same line.
            paired=True
        
        if read_id not in read_dict:
            read_dict[read_id]={}
            read_dict[read_id]['contig']=[]
            read_dict[read_id]['bin']=[]
            read_dict[read_id]['taxon_bin']=[]
            read_dict[read_id]['taxon_contig']=[]
        
        # check whether the score is above the threshold and whether the 
        # 'supplementary alignment' flag is unchecked, if yes, store contig
        # @Tina: how does this capture unmapped reads? What if a user gives a quality of 0?
        if score>=mapping_quality and len(bin(flag))<14:
            read_dict[read_id]['contig'].append(contig)
        
        # store unmapped reads as forward and reverse:
        # @Tina: should we group these conditions? I'm easily confused by 'x or y and z'.
        elif contig=='*' or score<mapping_quality and len(bin(flag))<14:
            # check if read is the "first in pair"
            if paired:
                if len(bin(flag))>8 and bin(flag)[-7]=='1':
                    unmapped_reads['fw'].add(read_id)
                else:
                    unmapped_reads['rev'].add(read_id)
            else:
                unmapped_reads['fw'].add(read_id)
    
    
    # if a reverse alignment file is given, add the contig that the mate maps to
    if BAM_rev_file:
        cmd=[path_to_samtools, 'view', BAM_fw_file]
        proc=subprocess.Popen(cmd, stdout=subprocess.PIPE)

        for read in proc.stdout:
            read=read.decode("utf-8").rstrip().split('\t')
            read_id, flag, contig, score=read[0], int(read[1]), read[2], int(read[4])
            if score>=mapping_quality and len(bin(flag))<14:
                read_dict[read_id]['contig'].append(contig)
            elif contig=='*' or score<mapping_quality and len(bin(flag))<14:
                unmapped_reads['rev'].add(read_id)
    
    # calculate sum of reads as number of reads in the dictionary (unmapped reads
    # are stored as well) for single read mappings, or as twice the number of reads
    # in the dictionary for paired-end read mappings
    if paired or BAM_rev_file:
        sum_of_reads=2*len(read_dict)
    else:
        sum_of_reads=len(read_dict)

    return read_dict, unmapped_reads, sum_of_reads, paired



def make_contig_dict(read_dict, 
                     bam_files, 
                     paired, 
                     contig2bin):
    """
    takes the read dictionary that stores which read maps where and returns
    a dictionary that stores how many reads bind to each contig. It also adds
    bin annotation to the read dict
    """
    contig_dict={}
    contig_dict['*']=0
    
    # check how long the list of contigs per read is allowed to be to calculate
    # unmapped reads and check that everything is working correctly
    if len(bam_files)>1 or paired:
        max_primary=2
    else:
        max_primary=1
    
    for read in read_dict:
        # if a read (pair) has multiple primary alignments, exit
        if len(read_dict[read]['contig'])>max_primary:
            message = (
                    'Something is wrong with the alignment. Too many mappings '
                    'detected. Please check your alignment file or map your reads '
                    'using RAT.')
            shared.give_user_feedback(message)
            sys.exit(1)
        
        # otherwise, determine the number of unmapped reads and add it to unmapped
        # build a dictionary of contigs and how many reads map to them
        # Add bin info to read dictionary
        else:
            contig_dict['*']+=max_primary-len(read_dict[read]['contig'])
            for contig in read_dict[read]['contig']:
                if not contig in contig_dict:
                    contig_dict[contig]=0
                    
                contig_dict[contig]+=1
                if contig2bin:
                    if contig in contig2bin:
                        read_dict[read]['bin'].append(contig2bin[contig])
                    else:
                        read_dict[read]['bin'].append('unbinned')
                    
    return contig_dict, read_dict, max_primary





def get_contig_lengths(contig_file):
    """
    gets the lengths of all contigs from the contig file. Works for all types
    of contig IDs, as long as it is a proper file with unique headers, because
    it checks the length of the strings.
    """
    contig_length_dict={}
    sum_of_nucleotides=0
    
    # split the fasta file into contigs and prevent empty strings
    # @Tina: opening a file like this will load the entire file into memory. I would open it line by line myself. This may get super slow depending on how you implement it, it can also be very fast.
    with open(contig_file, 'r') as inp:
        # @Tina: what does the [1:] do here? Also shouldn't the strip() remove the trailing newline? or do you mean rstrip()?
        contigs=inp.read()[1:].strip().split('\n>')
        
    # for each contig, store contig name and the length of sequence without whitespace
    # for each contig, add its length to the sum of nucleotides in the assembly
    for c in contigs:
        c_id, c_seq=c.split('\n')[0].strip(), c.split('\n', 1)[1].strip().replace('\n','')
        contig_length_dict[c_id]=len(c_seq)
        sum_of_nucleotides+=len(c_seq)
    
    return contig_length_dict, sum_of_nucleotides





def process_bin_folder(path_to_folder, bin_suffix):
    """
    takes the path to a folder containing metagenomic bins and picks out all
    nucleotide fasta files. Returns a dictionary that contains the bin ids as
    keys and a set of all contig ids that belong in that bin as values. 
    Important: Only contains the binned sequences. Every contig that is not
    in the output dictionary is unbinned.
    @Tina: Don't we have a function from the BAT workflow that does this?
    """
    bin_dict={}
    bins=os.listdir(path_to_folder)
    
    for b in bins:
        # grabs all fasta files and gets the bin id
        if b.split('.')[-1]==bin_suffix.split('.')[-1] and not b.rsplit('.', 1)[0].endswith('unbinned'):
            bin_id=b.strip()
            bin_dict[bin_id]=set()
            
            # open fasta file and split it into contigs
            contigs=open(path_to_folder+b).read().split('>')[1:]
            
            # add all contig ids to set
            for contig in contigs:
                bin_dict[bin_id].add(contig.split()[0])
                
    return bin_dict


def invert_bin_dict(bin_dict):
    # WORKS

    """
    @Tina: this should work as well:
    d_rev = {v: k for k, v in d.items()}
    return d

    It's shorter, but of course you should make an extra check to see if the
    values of the first dictionary are unique. I do like unversal functions (e.g.
    invert_dict as opposed to invert_bin_dict.
    """
    
    contig2bin={}
    for b in bin_dict:
        for contig in bin_dict[b]:
            contig2bin[contig]=b
    return contig2bin


if __name__ == '__main__':
    sys.exit('Run \'CAT\' to run CAT, BAT, or RAT.')

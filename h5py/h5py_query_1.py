"""
    Data is stored in the hierarchy of Trait/Study/DATA
    where DATA:
    under each directory we store 3 (or more) vectors
    snparray will hold the snp ids
    pvals will hold each snps pvalue for this study
    chr will hold each snps position
    or_array will hold each snps odds ratio for this study
    we can add any other information that we want

    the positions in the vectors correspond to each other
    snparray[0], pvals[0], chr[0], and or_array[0] hold the information for SNP 0

    Query 1: Retrieve all information for trait: input = query number (1) and trait name
    Query 2: Retrieve all the information for a study: input = query number (2) and study name and trait name
    Query 3: Retrieve all information (trait, study, pval, chr, or) for a single SNP: input = query number (3) and snp id
    Query 4: Retrieve all information (trait, study, pval, chr, or) for a set of SNPs that belong to a chromosome:
                input = query number (4) and chr (could do this wth other location information)
    Query 5: Retrieve all information for a trait and a single SNP: input = query number (5), trait and snp id
    Query 6: Retrieve all information for a trait and a set of SNPs that belong to a chromosome:
                input = query number (6), trait and chr

    If a p-value threshold is given, all returned values need to be restricted to this threshold
"""

import h5py
import numpy as np
import utils_q_1 as qu
import utils_q as utils


def main():

    qu.argument_checker()
    args = qu.argument_parser()

    # open h5 file in read mode
    f = h5py.File(args.h5file, mode="r")

    trait = args.trait
    study = args.study
    snp = args.snp
    chr = args.chr
    if chr is not None:
        chr = int(chr)
    upper_limit = args.pu
    if upper_limit is not None:
        upper_limit = float(upper_limit)
    lower_limit = args.pl
    if lower_limit is not None:
        lower_limit = float(lower_limit)

    if args.query == "1":
        # info_array = all_trait_info(f, args.trait)
        snps, pvals, chr, orvals, studies, bp, effect, other = query_for_trait(f, trait)
    elif args.query == "2":
        snps, pvals, chr, orvals, studies, bp, effect, other = query_for_study(f, trait, study)
    elif args.query == "3":
        snps, pvals, chr, orvals, studies, bp, effect, other = query_for_snp(f, snp)
    elif args.query == "4":
        snps, pvals, chr, orvals, studies, bp, effect, other = query_for_chromosome(f, chr)
    elif args.query == "5":
        snps, pvals, chr, orvals, studies, bp, effect, other = query_for_snp(f, snp, trait)
    elif args.query == "6":
        snps, pvals, chr, orvals, studies, bp, effect, other = query_for_chromosome(f, chr, trait)

    mask = utils.cutoff_mask(pvals, upper_limit, lower_limit)

    if mask is not None:
        print utils.filter_by_mask(snps, mask)
        print utils.filter_by_mask(pvals, mask)
        print utils.filter_by_mask(chr, mask)
        print utils.filter_by_mask(orvals, mask)
        print utils.filter_by_mask(np.asarray(studies, dtype = None), mask)
        print utils.filter_by_mask(bp, mask)
        print utils.filter_by_mask(effect, mask)
        print utils.filter_by_mask(other, mask)
    else:
        print snps
        print pvals
        print chr
        print orvals
        print studies
        print bp
        print effect
        print other


def query_for_trait(f, trait):
    print "Retrieving info for trait:", trait
    trait_group = f.get(trait)
    if trait_group is None:
        print "Trait does not exist", trait
        raise SystemExit(1)
    return get_trait_info(trait_group)


def query_for_study(f, trait, study):
    print "Retrieving info for study:", study
    study_group = f.get(trait + "/" + study)
    if study_group is not None:
        return get_study_group_info(study, study_group)
    else:
        print "Not valid trait/study combination"
        raise SystemExit(1)


def query_for_snp(f, snp, trait=None):
    print "Retrieving info for snp:", snp
    if trait is None:
        snps, pvals, chr, orvals, studies, bp, effect, other = get_file_info(f)
    else:
        snps, pvals, chr, orvals, studies, bp, effect, other = query_for_trait(f, trait)

    mask = snps == snp

    return qu.filter_vector(snps, mask), qu.filter_vector(pvals, mask), qu.filter_vector(chr, mask), qu.filter_vector(orvals, mask), qu.filter_vector(studies, mask), \
           qu.filter_vector(bp, mask), qu.filter_vector(effect, mask), qu.filter_vector(other, mask)


def query_for_chromosome(f, chromosome, trait=None):
    print "Retrieving info for chromosome:", chromosome
    if trait is None:
        snps, pvals, chr, orvals, studies, bp, effect, other = get_file_info(f)
    else:
        snps, pvals, chr, orvals, studies, bp, effect, other = query_for_trait(f, trait)

    mask = chr == float(chromosome)

    return qu.filter_vector(snps, mask), qu.filter_vector(pvals, mask), qu.filter_vector(chr, mask), qu.filter_vector(orvals, mask), qu.filter_vector(studies, mask), \
           qu.filter_vector(bp, mask), qu.filter_vector(effect, mask), qu.filter_vector(other, mask)


def get_file_info(f):
    snps = []
    pvals = []
    chr = []
    orvals = []
    studies = []
    bp = []
    effect = []
    other = []
    for x, trait_group in f.iteritems():
        snps_r, pvals_r, chr_r, orvals_r, studies_r, bp_r, effect_r, other_r = get_trait_info(trait_group)
        snps.extend(snps_r)
        pvals.extend(pvals_r)
        chr.extend(chr_r)
        orvals.extend(orvals_r)
        studies.extend(studies_r)
        bp.extend(bp_r)
        effect.extend(effect_r)
        other.extend(other_r)

    return np.array(snps), np.array(pvals), np.array(chr), np.array(orvals), np.array(studies), np.array(bp), np.array(effect), np.array(other)


def get_trait_info(trait_group):
    snps = []
    pvals = []
    chr = []
    orvals = []
    studies = []
    bp = []
    effect = []
    other = []

    print "looping through trait"
    for study_group_name, study_group in trait_group.iteritems():
        snps_r, pvals_r, chr_r, orvals_r, studies_r, bp_r, effect_r, other_r = get_study_group_info(study_group_name, study_group)
        snps.extend(snps_r)
        pvals.extend(pvals_r)
        chr.extend(chr_r)
        orvals.extend(orvals_r)
        studies.extend(studies_r)
        bp.extend(bp_r)
        effect.extend(effect_r)
        other.extend(other_r)

    return np.array(snps), np.array(pvals), np.array(chr), np.array(orvals), np.array(studies), np.array(bp), np.array(effect), np.array(other)


def get_study_group_info(study_group_name, study_group):
    snps = study_group["snp"][:]
    pvals = study_group["pval"][:]
    chr = study_group["chr"][:]
    orvals = study_group["or"][:]
    studies = [study_group_name for i in xrange(len(snps))]
    bp = study_group["bp"][:]
    effect = study_group["effect"][:]
    other = study_group["other"][:]
    return snps, pvals, chr, orvals, np.array(studies), bp, effect, other


if __name__ == "__main__":
    main()
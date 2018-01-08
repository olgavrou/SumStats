#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color
clear
echo ""
echo "Final file creation starting..."
file=$1

if [ -z $file ] ;
then
    echo "$0 You need to provide the correct arguments! Exiting..."
    exit
fi

options=("variant"
        "pval"
        "chr"
        "or"
        "bp"
        "effect"
        "other"
        "freq"
        "beta"
        "range"
        "se")

for opt in "${options[@]}"; do

    if [ ! -s "$opt"_"$file" ];then
        awk '{print "NA"}' variant_"$file" > "$opt"_"$file"
    fi

done

paste variant_"$file" pval_"$file" chr_"$file" or_"$file" bp_"$file" effect_"$file" other_"$file" freq_"$file" beta_"$file" range_"$file" se_"$file" > loadable_$file

echo -e "variant\tpval\tchr\tor\tbp\teffect\tother\tfreq\tbeta\trange\tse" | cat - loadable_$file > .tmp
mv .tmp loadable_$file
echo -e "The final format of the file is saved here: ${GREEN}loadable_$file${NC}"
echo ""
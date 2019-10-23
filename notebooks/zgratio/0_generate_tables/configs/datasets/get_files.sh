#!/bin/bash
outpath="mv_v2.txt"
for daspath in $(cat mc.txt); do
    echo $daspath
    files=$(dasgoclient --query "file dataset=${daspath}")
    summary=$(dasgoclient --query "summary dataset=${daspath}")
    echo "[DATASET]" >> $outpath
    echo "$daspath" >> $outpath
    echo "[FILES]" >> $outpath
    echo $files >> $outpath
    echo "[SUMMARY]" >> $outpath
    echo $summary >> $outpath
    echo "" >> $outpath
done

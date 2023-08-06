#!/bin/bash

source /project/ralabota/cogs/img2img/args.sh

COGFOLDER="/project/ralabota/cogs/img2img/"
OUTFOLDER="/project/ralabota/cogs/img2img/output"


IMGREQUEST="'$IMGREQUEST'"

echo $IMGREQUEST

#read -p "please enter what you want" request

python /project/ralabota/stable-diffusion/optimizedSD/optimized_img2img.py --turbo --prompt "$IMGREQUEST" --init-img /project/ralabota/most-recent-attachment --strength 0.8 --H 512 --W 512 --n_iter 1 --n_samples 1 --outdir "$OUTFOLDER"

cd $COGFOLDER
cd ./output

mv * output_folder

cd ./output_folder

#This is all stuff for going more than a single image
#montage * -geometry 512x512 output.jpg
#find . ! -iname output.jpg -exec rm -rf {} \;
#mv output.jpg $COGFOLDER + "/output"

mv * output.png

mv output.png ../

cd ..

rm -r output_folder


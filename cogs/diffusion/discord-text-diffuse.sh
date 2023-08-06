#!/bin/bash

source /project/ralabota/cogs/diffusion/args.sh

COGFOLDER="/project/ralabota/cogs/diffusion/"
OUTFOLDER="/project/ralabota/cogs/diffusion/output"

REQUEST="'$REQUEST'"

echo $REQUEST

#read -p "please enter what you want" request

python /project/ralabota/stable-diffusion/optimizedSD/optimized_txt2img.py --turbo --prompt "$REQUEST" --H 512 --W 512 --n_iter 1 --n_samples 1 --ddim_steps 50 --outdir "$OUTFOLDER"

cd $COGFOLDER
cd ./output

mv * output_folder

cd ./output_folder

#This is all stuff for going more than a single image
#montage * -geometry 512x512 output.jpg
#find . ! -iname output.jpg -exec rm -rf {} \;
#mv output.jpg $COGFOLDER + "/output"

mv *.png output.png

mv output.png ../

cd ..

rm -r output_folder


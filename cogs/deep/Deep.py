import subprocess
from discord.ext import commands
import discord
import os
import yaml
import inspect
from skimage.transform import resize
from skimage import img_as_ubyte
from .demo import make_animation
from .demo import load_checkpoints
from .modules.util import from_script_dir
from PIL import Image
import imageio
import gc
import torch
import sys

script_dir = './cogs/deep/'
cwd = './'


class Deep(commands.Cog):
    @from_script_dir
    def __init__(self, bot):
        self.bot = bot

        # Create list if it does not already exist
        with open('list.yaml', 'a+') as file:
            file.close()

        # Parse list
        with open('list.yaml', 'r') as file:
            self.my_list = yaml.load(file, Loader=yaml.FullLoader) or []
            if self.my_list != []:
                print('\n'.join(self.my_list))


    
    @commands.command()
    async def deep(self, message, *args):
        cmd = args[0]

        if cmd == 'list':
            await self.show_list(message)
 

        elif cmd == 'create':
            if len(args) == 3:
                await self.create_reference(message, args[1], args[2])
            elif len(args) == 4:
                await self.create_reference(message, args[1], args[2], args[3])
            elif len(args) == 5:
                await self.create_reference(message, args[1], args[2], args[3], args[4])
            else:
                await message.channel.send("ERROR: Invalid number of arguments. Do ``.deep help`` for more information.")

        elif cmd == 'delete':
            await self.delete_reference(message, args[1])

        elif cmd == 'help':
            await self.help(message)

        elif cmd in self.my_list:

            await self.deep_create(message, cmd)

        else:
            await message.channel.send("Unrecognised command.")

    async def show_list(self, message):
        if self.my_list:
            await message.channel.send('\n'.join(self.my_list))
        else:
            await message.channel.send("There are currently no references created.")

    @from_script_dir
    async def create_reference(self, message, new_command, youtube_link, timestamp1='00:00:00', timestamp2=''):
        # Check for valid YouTube link
        if 'youtube.com' not in youtube_link and 'youtu.be' not in youtube_link:
            await message.channel.send("ERROR: Video reference must be a YouTube URL.")
            await message.channel.send(".deep addreference <.name> <YouTube URL> [Start Timestamp] [End Timestamp]")

        # Check if command already exists
        elif new_command in self.my_list:
            await message.channel.send("ERROR: Command with that name already exists. Try using another name.")

        else:
            valid_input = True

            # Check start timestamp format
            if len(timestamp1) != 8:
                await message.channel.send("ERROR: Timestamp must be in format hh:mm:ss. Aborting.")
                valid_input = False

            # Check end timestamp format
            if timestamp2 != '' and len(timestamp2) != 8:
                await message.channel.send("ERROR: Timestamp must be in format hh:mm:ss. Aborting.")
                valid_input = False

            if valid_input:
                await message.channel.send("Creating new reference...")
                # Download video
                os.system('youtube-dl -f worst --output "video/raw.mp4" --recode-video mp4 ' + youtube_link)
                # Cut to length
                if timestamp2 == '':
                    os.system('ffmpeg -ss ' + timestamp1 + ' -i video/raw.mp4 video/cut.mp4 -y')
                else:
                    os.system('ffmpeg -ss ' + timestamp1 + ' -to ' + timestamp2 + ' -i video/raw.mp4 video/cut.mp4 -y')

                # Crop for best face alignment
                # Suggest potential crops
                out = os.popen('python crop-video.py --inp video/cut.mp4')
                crops = out.read().split('\n')
                out.close()
                crops[:] = [x for x in crops if x]
                print(crops)

                # Analyse suggestions
                if crops:
                    hi = 0
                    indx = 0
                    for i in range(len(crops)):
                        crop = crops[i].split()
                        if crop:
                            # Choose best fit
                            if float(crop[6]) > hi:
                                hi = float(crop[6])
                                indx = i
                                print(hi, indx)

                    # Crop video
                    new_crop = crops[indx].split()[8][6:-1]
                    print('New crop: ' + new_crop)
                    os.system('ffmpeg -i video/cut.mp4 -filter:v "crop=' + new_crop + ', scale=256:256" crop.mp4 -y')

                    # Save new reference
                    os.system('ffmpeg -i crop.mp4 -q:a 0 -map a ./cogs/deep/driving_video/' + new_command + '_sound.mp3')
                    os.system('ffmpeg -i crop.mp4 -c copy ./cogs/deep/driving_video/' + new_command + '.mp4 -y')

                    # Save new reference
                    rel_path = "list.yaml"
                    abs_yaml_path = os.path.join(script_dir, rel_path)
                    with open('list.yaml', 'r') as file:
                        up_list = list(yaml.load(file, Loader=yaml.FullLoader))
                        up_list.append(new_command)
                        self.my_list.append(new_command)
                        print(up_list)
                    with open(abs_yaml_path, 'w') as file:
                        yaml.dump(up_list, file)

                    print('New Reference Created')
                    await message.channel.send("New reference created, " + new_command)

                # No suitable crops found
                else:
                    await message.channel.send('No faces recognised in clip. The clip may be too short or contain too many cuts.')

                # Clean up unnecessary resources
                os.remove("crop.mp4")
                os.remove("video/raw.mp4")
                os.remove("video/cut.mp4")

    @from_script_dir
    async def delete_reference(self, message, reference):
        # Check if reference exists
        if reference in self.my_list:
            # Update list
            with open('list.yaml', 'r') as file:
                up_list = yaml.load(file, Loader=yaml.FullLoader)
                up_list.remove(reference)
                self.my_list.remove(reference)
                print(up_list)

            with open('list.yaml', 'w') as file:
                yaml.dump(up_list, file)

            # Delete files
            try:
                os.remove('driving_video/' + reference + '.mp4')
                os.remove('driving_video/' + reference + '_sound.mp3')
            except OSError as e:
                print("Failed with:", e.strerror)

            await message.channel.send("Reference deleted, ``" + reference + "``.")

        else:
            await message.channel.send("No reference found with name ``" + reference + "``.")

    @staticmethod
    async def help(message):
        e = {
            "title": "DeepBot Help",
            "description": "**See list of available reference videos**\n```.deep list```\n**Create a deepfake video**\nPost an image and then use the following command: \n```.deep <name of reference>```\n**Create a new reference video**\nCreate a new reference from a YouTube video, and crop it using optional timestamp parameters.\n```.deep create <name> <YouTube URL> [timestamp1] [timestamp2]``` \n**Delete an existing reference video**. \n```.deep delete <reference name>```\n",
            "color": 14071166,
            "author": "Quibble"
        }
        embed = discord.Embed(title=e["title"], description=e["description"], color=e["color"])
        await message.channel.send(embed=embed)

    @staticmethod
    async def deep_create(message, cmd):
        await message.channel.send("Processing...")
        print(os.getcwd())
        print("Beginning video")
        os.system(
            "python cogs/deep/demo.py --config cogs/deep/config/vox-adv-256.yaml --driving_video cogs/deep/driving_video/" + cmd + ".mp4 --source_image most-recent-attachment --result_video cogs/deep/result.mp4 --checkpoint cogs/deep/checkpoints/vox-adv-cpk.pth.tar --relative --adapt_scale")
        print("Video done")
        os.system(
            "ffmpeg -i cogs/deep/result.mp4 -i cogs/deep/driving_video/" + cmd + "_sound.mp3 -vcodec copy -acodec copy cogs/deep/final.mp4 -y")
        print("Audio added")
        await message.channel.send(file=discord.File('cogs/deep/final.mp4'))

    @staticmethod
    async def deep_create_2(message, cmd):
        await message.channel.send("Processing...")
        print("Beginning video")

        source_image = imageio.imread('./most-recent-attachment')
        print("image read")
        reader = imageio.get_reader('./cogs/deep/driving_video/' + cmd + '.mp4')
        print("video read")
        fps = reader.get_meta_data()['fps']
        print("fps read")
        driving_video = []
        try:
            for im in reader:
                driving_video.append(im)
        except RuntimeError:
            pass
        reader.close()
        print("image stuff done")
        source_image = resize(source_image, (256, 256))[..., :3]
        driving_video = [resize(frame, (256, 256))[..., :3] for frame in driving_video]
        generator, kp_detector = load_checkpoints(config_path='./cogs/deep/config/vox-adv-256.yaml', checkpoint_path='./cogs/deep/checkpoints/vox-adv-cpk.pth.tar')
        predictions = make_animation(source_image, driving_video, generator, kp_detector, relative=False, adapt_movement_scale=False)

        imageio.mimsave('result.mp4', [img_as_ubyte(frame) for frame in predictions], fps=fps)

        del generator
        del kp_detector
        del predictions

        gc.collect()
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()

        print("Video done")
        os.system(
            "ffmpeg -i result.mp4 -i " + script_dir + "driving_video/" + cmd + "_sound.mp3 -vcodec copy -acodec copy " + script_dir + "/final.mp4 -y")
        print("Audio added")


        await message.channel.send(file=discord.File(script_dir + '/final.mp4'))
        #os.system("nvidia-smi | grep 'python' | awk '{ print $5 }' | xargs -n1 kill -9")
        generator = kp_detector = predictions = driving_forward = driving_backward = predictions_forward = predictions_backward = None


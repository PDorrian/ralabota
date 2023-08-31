from discord.ext import commands
import subprocess
import os
import discord

cogdir="./cogs/diffusion"
cwd = os.getcwd()

class Diffusion(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        print('txt2img cog loaded')

    @commands.command()
    async def diffuse(self, ctx, *messages):
        #Define a variable for just a space
        separator = ' '
        
        #Send message to alert user a process is happening
        await ctx.send("processing prompt")

        #This joins all arguments together into the full message
        todiffuse = separator.join(messages)
        
        #Re-define the message variable to have quotes around it
        #todiffuse = '"' + message + '"' 

        #Debug, nice for logging what is being sent
        print (todiffuse + ' is being sent for processing')

        #This runs the command using subprocess
        print(os.getcwd())
        subprocess.call(["conda","run","-n","diffusion","python","./cogs/diffusion/stable-diffusion/optimizedSD/optimized_txt2img.py","--turbo","--prompt",todiffuse,"--H","512","--W","512","--n_iter","1","--n_samples","1","--ddim_steps","50","--outdir","./cogs/diffusion/output/"])
        #Sends the complete image back into the discord
        for folder in os.listdir(cogdir+"/output/"):
            print(folder)
            for file in os.listdir(cogdir+"/output/"+folder+"/"):
                print(file)
                os.rename((cogdir+"/output/"+folder+"/"+file),(cogdir+"/output.png"))
            os.rmdir(cogdir+"/output/"+folder)
        
        await ctx.send(file=discord.File("./cogs/diffusion/output.png"))
        print(os.getcwd())
        todiffuse = todiffuse.replace(" ","")
        os.rename(cogdir+"/output.png",cogdir+"/diffusion-archive/"+todiffuse+".png")
        #Remove the image for cleanup

        



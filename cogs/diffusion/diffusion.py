from discord.ext import commands
import subprocess
import os
import discord

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
        message = separator.join(messages)
        
        #Re-define the message variable to have quotes around it
        message = '"' + message + '"' 

        #Debug, nice for logging what is being sent
        print (message + ' is being sent for processing')
        
        #This is horrid, but it was the easiest way I could find to pass the message into the bash script
        #that runs the diffusion
        #We open args.sh, and then insert the contents of the discord message into it, where it can be read
        #from discord-text-diffuse.sh and run the prompt
        write_args = open("/project/ralabota/cogs/diffusion/args.sh", "w")
        write_args.write("REQUEST=" + message)
        write_args.close()

        #This runs the command using subprocess
        subprocess.run("/project/ralabota/cogs/diffusion/discord-text-diffuse.sh")
        
        #Sends the complete image back into the discord
        await ctx.send(file=discord.File("/project/ralabota/cogs/diffusion/output/output.png"))
        
        #Remove the image for cleanup
        os.remove("/project/ralabota/cogs/diffusion/output/output.png")

        



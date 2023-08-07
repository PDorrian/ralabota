import discord
from discord.ext import commands
import aiohttp
import aiofiles
import asyncio

from cogs.deep.Deep import Deep
from cogs.diffusion.diffusion import Diffusion

from cogs.img2img.diffimage import DiffIMG

intents = discord.Intents.all()

if __name__ == '__main__':
    with open('key.txt') as k:
        key = k.readline()

    client = discord.Client(intents=intents)
    bot = commands.Bot(command_prefix='.', description='QuibBot', intents=intents)
    
    async def setup():
        await bot.add_cog(Diffusion(bot))
        await bot.add_cog(DiffIMG(bot))
        #print('loaded diffusion')
        await bot.add_cog(Deep(bot))
        # print('loaded Deep')

    asyncio.run(setup())

    @bot.event
    async def on_message(message):
        if message.author.bot:
            return

        if message.content:
            last_message = message
            print(last_message)

        if message.attachments:
            attachment = message.attachments[0]
            print("Attachment received: " + attachment.url)
            # Save attachment
            async with aiohttp.ClientSession() as session:
                async with session.get(attachment.url) as resp:
                    if resp.status == 200:
                        f = await aiofiles.open('./most-recent-attachment', mode='wb')
                        await f.write(await resp.read())
                        await f.close()

        await bot.process_commands(message)

    bot.run(key, reconnect=True)





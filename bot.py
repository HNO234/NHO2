import os
from dotenv import load_dotenv
from discord.ext import commands

bot = commands.Bot(command_prefix='nho2 ')
cogs = ['crawler']

@bot.event
async def on_message(message):
	print(message.content)
	if message.content == 'nho2':
		await message.channel.send("Hi! This is Discord bot developed by HNO2.\nYou can find my soure code at https://github.com/HNO234/NHO2.")
	await bot.process_commands(message)

if __name__ == '__main__':
    for cog in cogs:
        bot.load_extension(cog)

    load_dotenv()
    bot.run(os.getenv('BOT_TOKEN'))

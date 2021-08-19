import discord
import crawler
import notcommand
import os
from dotenv import load_dotenv
from tools import *

client = discord.Client()

def get_class(command):
    return {
        'track': crawler.CodeforcesRecentSubmissionsCrawler,
        'untrack': crawler.CodeforcesRecentSubmissionsCrawler
    }.get(command,notcommand.NotCommand)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # For testing purpose
    if str(message.author.id) != os.getenv('AUTHOR_ID'):
        return

    if message.content.strip() == 'nho2':
        await message.channel.send("Hello! This is Discord Bot developed by HNO2.\nYou can find my source code at https://github.com/HNO234/NHO2.")
    if not message.content.startswith('nho2 '):
        return

    arguments = BotArguments(message.content.strip().split()[1:])
    await get_class(arguments[0])(message.channel, arguments).run()

if __name__ == '__main__':
    load_dotenv()
    client.run(os.getenv('BOT_TOKEN'))

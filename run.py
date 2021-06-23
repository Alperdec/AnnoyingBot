import discord
from discord.ext import commands
import re
import os
from dotenv import load_dotenv
from spellcheck import SpellChecker
from util import pointSystem, normalize_name
import json

load_dotenv()

APItoken = os.getenv('TOKEN')
client = discord.Client()

sp_obj = SpellChecker()
point_sys_obj = pointSystem()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if '$hello' == message.content.lower():
        await message.channel.send(f"hello, {normalize_name(str(message.author))}, type '$help' for a list of commands")
        return

    if '$help' == message.content.lower():
        await message.channel.send('type:\t*$show leaderboard*\tto show the leaderboard\nMore commands coming soon!\notherwise, get typing!')
        return
        
    if '$show leaderboard' == message.content.lower():
        inputs = point_sys_obj.get_all_users()
        output = ""
        counter = 1

        for item in inputs:
            output += ('name:\t' 
                    + item['name'] 
                    + '\tpoints:\t' 
                    + str(item['points']) 
                    + '\tposition:\t' 
                    + str(counter) 
                    +'\n')
            counter += 1
        await message.channel.send(output)
        return

    spelling_errors = sp_obj.check_for_errors(message.content)
    if len(spelling_errors) != 0:
        output = "you may have mispelled "
        output2 = " did you mean to say "
        for category in spelling_errors:
            output += ' *' + category +'* '
            output2 += ' *' + spelling_errors[category] + '* '

        output += output2 + '?'
        point_sys_obj.increment_user(normalize_name(str(message.author)), -1)
        await message.channel.send(output)
    else:
        point_sys_obj.increment_user(normalize_name(str(message.author)), 1)
        await message.channel.send('Nice job, you can spell!')



client.run(APItoken)
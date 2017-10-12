'''
DoctorSpaceBot by MadScotty

BEGIN LICENSE

By existing on the same mortal coil as the author of this software you hereby
allow the author, henceforth known as Dr. Awesomeweiner, to sleep on your couch, 
watch your television, and use your microwave.  By reading this license you agree 
that Lord Satan isn't as bad as everyone says #fakenews

END LICENSE
'''

import discord
import trivia
import logging
import ship_lookup

# Enables logging.  Code shamelessly stolen from the discord.py API documentation site.
# Source:  http://discordpy.readthedocs.io/en/latest/logging.html#logging-setup
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

description = "Hopefully I don't explode"

client = discord.Client()

# Cleans up main file and makes bot easier to extend
trivia_command_list = [".help", ".triviastart", ".triviastop", ".score", ".leaderboard"]

@client.event
async def on_message(message):

    # Bot is misbehaving.  Time to DIE
    if message.content == '.die' and message.author == discord.utils.get(message.server.members, name = "MadScotty"):
        await client.send_message(message.channel, "Committing Sudoku")
        await client.logout()

    # The bot is gonna ignore itself
    if message.author == client.user:
        return

    if message.content == '.prodschedule':
        await client.send_message(message.channel, "https://robertsspaceindustries.com/schedule-report")

    if message.content.startswith(".ship"):
        ship_name = str(message.content)
        try:
            await client.send_message(message.channel, embed = await ship_lookup.ship_finder(ship_name[6:]))
        except:
            await client.send_message(message.channel, "Ship not found")

    # Reset idle counter if anything is said in the trivia channel by anyone other than the bot
    if str(message.channel) == "trivia":
        trivia.idle_counter = 0
        
        # Check for trivia commands
        if message.content in trivia_command_list:
            await trivia.listen(client, message, message.channel, message.author)

        # Check for trivia report.  Seperate to allow .startswith()
        elif message.content.startswith(".report"):
            await trivia.listen(client, message, message.channel, str(message.author))

        # A little less graceful to do things this way, but I want all the "listening" done in one place
        if not trivia.is_answered and str(message.content).lower() == str(trivia.answer).lower():
                await trivia.question_answered(client, message.author, message.channel)

@client.event
async def on_server_join(server):
    print("Joined " + str(server))

# Reminds me in console that the damn thing is running so I don't accidentially double it up
@client.event
async def on_ready():
    print(client.user.name, "Logged in and running")

tFile = open('to.ken')
token = tFile.read()

client.run(token)
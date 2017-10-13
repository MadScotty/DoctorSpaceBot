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
version_number = "1.2"

client = discord.Client()
admins = ["MadScotty#1628", "TheMezMeister#6711"]

# Cleans up main file and makes bot easier to extend
trivia_command_list = [".triviastart", ".triviastop", ".score", ".leaderboard"]

@client.event
async def on_message(message):

    # Bot is misbehaving.  Time to DIE
    if message.content == '.die' and str(message.author) in admins:
        await client.send_message(message.channel, "Committing Sudoku...")
        await client.logout()

    # The bot is gonna ignore itself
    elif message.author == client.user:
        return

    elif message.content == '.prodschedule':
        await client.send_message(message.channel, "https://robertsspaceindustries.com/schedule-report")

    elif message.content.startswith(".ship"):
        ship_name = str(message.content)
        try:
            await client.send_message(message.channel, embed = await ship_lookup.ship_finder(ship_name[6:]))
        except:
            if ship_lookup.has_error:
                await client.send_message(message.channel, "An error has occured.  I most likely wasn't able to connect to the wiki.\nMy owner has been notified.")
                await client.send_message(owner, "Check your console, something borked.")
            else:
                await client.send_message(message.channel, "Ship not found")

    elif message.content == ".help":
        await client.send_message(message.channel, "Okay, PM'ing you the list of commands.")
        await client.send_message(message.author, await helpbox())

    elif message.content == ".changelog":
        await client.send_message(message.channel, "Okay, PM'ing you this bot's current changelog.  (Current version: " + version_number + ")")
        await client.send_message(message.author, await changelog())

    elif str(message.channel) == "trivia":
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

# Returns a help box using Discord's code formatting.
async def helpbox():    
    formatted_string = "```"
    formatted_string += "General Commands:\n" + \
                        ".help                        - Displays this box\n" + \
                        ".prodschedule                - Posts link to current production schedule\n" + \
                        ".ship (Ship Name)            - Displays info about a ship\n" + \
                        ".changelog                   - Sends a PM with this bot's current changelog\n\n" + \
                        'Trivia Commands: (if enabled)\n' + \
                        ".triviastart                 - Starts the trivia game\n" + \
                        ".triviastop                  - Stops the trivia game\n" + \
                        ".score                       - Displays your current score\n" + \
                        ".leaderboard                 - Displays the current top players\n" + \
                        ".report (question #)(reason) - Reports a bad/incorrect question or answer"
    formatted_string += "```"
    return formatted_string

async def changelog():
    formatted_string = "```"

    try:
        with open("changelog.txt", "r") as logfile:
            loglist = logfile.readlines()
    except:
        print("Changelog file operation failed")
        return "Changelog file operation borked. =["

    for i in loglist:
        formatted_string += i

    formatted_string += "```"
    return formatted_string
                

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
'''
DoctorSpaceBot by MadScotty

BEGIN LICENSE

By existing on the same mortal coil as the author of this software you hereby
allow the author, henceforth known as Dr. Awesomeweiner, to sleep on your couch, 
watch your television, and use your microwave.  By reading this license you agree 
that Lord Satan isn't as bad as everyone says #fakenews

END LICENSE
'''

# Ship lookup module for DoctorSpaceBot
# All data pulled from the Star Citizen Wiki at http://starcitizen.tools
# It will return a message for the bot to say and it will be called by client.send_message(message,channel, ship_lookup(message.content))

import asyncio
import aiohttp
import discord
from async_timeout import timeout
from bs4 import BeautifulSoup as soup # BeautifulSoup is too much to type.  Who has time for the shift key?

# Other globals
ship_index = []

# Grab the ship name from the index
async def ship_finder(ship_name):
    global ship_index

    ship_name = ship_name.lower()

    await get_ship_index()

    # Neat boolean trick to see if list is empty
    if not ship_index:
        print("Ship lookup borked. ship_index is empty")
        return "Something borked with the ship lookup.  Scotty has been notified"

    # Grab the index of ship name 
    ship_index_location = -1
    for i in range(0, len(ship_index) - 1):
        index_lowercase = str(ship_index[i]).lower()
        if ship_name in index_lowercase:
            ship_index_location = i
            break
    if ship_index_location == -1:
        return

    # Seperate link from rest of text.  Start with the entire thing and trim pieces.
    raw_link = str(ship_index[ship_index_location])
    trim_start = raw_link[9:]                           # Trim <a href=" from the beginning
    end_quote = trim_start.find('"')
    link = trim_start[:end_quote]                       # Trim the rest of the fat

    ship_info = await parse_ship_info(link)
    if ship_info == -1:
        return "Something borked with ship stat parsing.  Scotty has been notified"
    else:
        return make_table(ship_info)

# Parse data from the Category:Ships page into a list of links
async def get_ship_index():

    global ship_index

    # Pull rendered version of page
    with timeout(10):
        async with aiohttp.ClientSession() as sesh:
            async with sesh.get('http://starcitizen.tools/Category:Ships?action=render') as page:
                try:
                    assert page.status == 200
                    raw_page = await page.text()

                except:
                    print("Failed to load Category:Ships with satus code ") + str(page.status)
                    return

    # Pass to BeautifulSoup then scrape just the table, then make a list of the hyperlinks
    # Example item:
    # <a href="https://starcitizen.tools/300i" title="300i">300i</a>
    souped = soup(raw_page, 'html.parser')
    tabled = souped.table
    ship_index = tabled.find_all('a')

    # At the moment, the Category:Ships page also has a link to the Alpha 3.0 page.
    # Hacky solution, I know.  I'll fix it later
    for i in range(0, len(ship_index) - 1):
        if '3.0' in str(ship_index[i]):
            ship_index.pop(i)


# Pull info from the infobox on the ship page
async def parse_ship_info(link):

    rendered_link = link + "?action=render"

    # Pull rendered version of page
    with timeout(10):
        async with aiohttp.ClientSession() as sesh:
            async with sesh.get(rendered_link) as page:
                try:
                    assert page.status == 200
                    raw_page = await page.text()
                except:
                    print("Failed to load ship page " + link + " with satus code ") + str(page.status)
                    return -1

    # Pass to BeautifulSoup then scrape the infobox table
    souped = soup(raw_page, 'html.parser')
    tabled = souped.table
    infobox = souped.table.find_all('tr')

    # Info dict
    ship_info = {"link" : link, \
                 "img_link" : "", \
                 "name" : "", \
                 "manf" : "", \
                 "focus" : "", \
                 "prod_state" : "", \
                 "crew" : "", \
                 "cargo" : "", \
                 "price" : "", \
                 "mass" : "", \
                 "speed" : "", \
                 "ab_speed": "", \
                 "length" : "", \
                 "height" : "", \
                 "beam" : "", \
                }

    # -------------------------------------------------
    # Parse data from infobox
    # -------------------------------------------------

    # Image link
    infobox_item = str(infobox[0])
    start = infobox_item.find('src')
    end = infobox_item.find('"', start + 5, len(infobox_item))
    if start == -1 or end == -1:
        ship_info['img_link'] = "Unknown"
    else:
        ship_info["img_link"] = "https://starcitizen.tools/" + infobox_item[start + 6:end]
        
    # Ship name
    ship_info["name"] = infobox[1].text

    # Ship manufacturer
    infobox_item = ""
    for i in infobox:
        if "Manufacturer" in i.text:
            infobox_item = i.text
    if infobox_item == "":
        ship_info["manf"] = "Unknown"
    else:
        end = infobox_item.find('\xa0')
        ship_info["manf"] = infobox_item[12:end]
        # Because MISC breaks the damn formatting
        if ship_info["manf"] == "Musashi Industrial and Starflight Concern":
            ship_info["manf"] = "MISC"

    # Ship focus
    infobox_item = ""
    for i in infobox:
        # Workaround for whips with a primary/secondary focus
        if "Primary Focus" in i.text:
            infobox_item = i.text
            ship_info['focus'] = infobox_item[13:]
            break
        elif "Focus" in i.text:
            infobox_item = i.text
    if infobox_item == "":
        ship_info["focus"] = "Unknown"
    elif ship_info['focus'] == "":
        ship_info["focus"] = infobox_item[5:]

    # Production State
    infobox_item = ""
    for i in infobox:
        if "Production State" in i.text:
            infobox_item = i.text
    if infobox_item == "":
        ship_info["prod_state"] = "Unknown"
    else:
        ship_info["prod_state"] = infobox_item[16:]

    # Maximum Crew
    infobox_item = ""
    for i in infobox:
        if "Maximum Crew" in i.text:
            infobox_item = i.text
    if infobox_item == "":
        ship_info["crew"] = "Unknown"
    else:
        ship_info["crew"] = infobox_item[12:]

    # Cargo
    infobox_item = ""
    for i in infobox:
        if "Cargo Capacity" in i.text:
            infobox_item = i.text
    if infobox_item == "":
        ship_info["cargo"] = "Unknown"
    else:
        ship_info["cargo"] = infobox_item[14:]

    # Pledge cost
    infobox_item = ""
    for i in infobox:
        if "Pledge Cost" in i.text:
            infobox_item = i.text
    if infobox_item == "":
        ship_info["price"] = "Unknown"
    else:
        ship_info["price"] = infobox_item[11:]

    # Mass
    infobox_item = ""
    for i in infobox:
        if "Null-cargo Mass" in i.text:
            infobox_item = i.text
    if infobox_item == "":
        ship_info["mass"] = "Unknown"
    else:
        ship_info["mass"] = infobox_item[15:]

    # Max SCM speed
    infobox_item = ""
    for i in infobox:
        if "Max. SCM Speed" in i.text:
            infobox_item = i.text
    if infobox_item == "":
        ship_info["speed"] = "Unknown"
    else:
        ship_info["speed"] = infobox_item[14:]

    # Max afterburner speed
    infobox_item = ""
    for i in infobox:
        if "Max. Afterburner Speed" in i.text:
            infobox_item = i.text
    if infobox_item == "":
        ship_info["ab_speed"] = "Unknown"
    else:
        ship_info["ab_speed"] = infobox_item[22:]

    # Length
    infobox_item = ""
    for i in infobox:
        if "Length" in i.text:
            infobox_item = i.text
    if infobox_item == "":
        ship_info["length"] = "Unknown"
    else:
        ship_info["length"] = infobox_item[6:]

    # Height
    infobox_item = ""
    for i in infobox:
        if "Height" in i.text:
            infobox_item = i.text
    if infobox_item == "":
        ship_info["height"] = "Unknown"
    else:
        ship_info["height"] = infobox_item[6:]

    # Beam
    infobox_item = ""
    for i in infobox:
        if "Beam" in i.text:
            infobox_item = i.text
    if infobox_item == "":
        ship_info["beam"] = -1
    else:
        ship_info["beam"] = infobox_item[4:]

    return ship_info

# Prettifies data using a Discord embed object
def make_table(ship_info):
    ship_embed = discord.Embed(title = ship_info['name'], url = str(ship_info['link']), description = "--------------------", color = 0x23af40,)
    
    ship_embed.add_field(name = "Manufacturer", value = ship_info["manf"], inline = True)
    ship_embed.add_field(name = "Focus", value = ship_info["focus"], inline = True)

    ship_embed.add_field(name = "Production State", value = ship_info["prod_state"], inline = True)
    ship_embed.add_field(name = "Crew", value = ship_info["crew"], inline = True)

    ship_embed.add_field(name = "Cargo", value = ship_info["cargo"], inline = True)
    ship_embed.add_field(name = "Null-cargo Mass", value = ship_info["mass"], inline = True)

    ship_embed.add_field(name = "Max SCM Speed", value = ship_info["speed"], inline = True)
    ship_embed.add_field(name = "Max AFB Speed", value = ship_info["ab_speed"], inline = True)

    ship_embed.add_field(name = "Pledge Cost", value = ship_info["price"], inline = True)
    ship_embed.add_field(name = "Length", value = ship_info["length"], inline = True)

    ship_embed.add_field(name = "Height", value = ship_info["height"], inline = True)
    ship_embed.add_field(name = "Beam", value = ship_info["beam"], inline = True)

    ship_embed.set_image(url=str(ship_info['img_link']))

    return ship_embed
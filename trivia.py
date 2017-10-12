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
import asyncio
import time
import random
import linecache
import os

# Global variables
is_running = False
is_answered = True
timer = 0
question = ""
answer = ""
hint = ""
q_number = -1
idle_counter = 0
score_reset_day = "2017-09-23"

# Create scorecard from file
scorecard = []
try:
    score_file = open("score.card", "r")
    scorecard = score_file.readlines()
    score_file.close()
except:
    print("Scorecard file operation failed")

# Kill the newline characters
for i in range(0, len(scorecard)):
    if scorecard[i].endswith("\n"):
        scorecard[i] = scorecard[i][:-1]


# Trivia listener
async def listen(client, message, channel, user):

    global is_running
    global is_answered
    global q_number
    global idle_counter

    if message.content == ".help":
        await client.send_message(channel, helpbox())

    if message.content == ".triviastart" and not is_running:
        is_running = True
        is_answered = True
        await client.send_message(channel, "OK!  Let's get this party started!\n" + "DoctorSpaceBot Trivia v1.1 because v0.1 and v0.2 didn't work at all, and 1.0 had shit code.\n*Type .help for a list of commands*")
        while is_running:
            if idle_counter >= 5:
                is_running = False
                await client.send_message(channel, "Trivia stopped due to inactivity.  Type .triviastart to start!")
                return
            if is_answered:
                idle_counter += 1
                await next_question(client, channel)
        await client.send_message(channel, "Trivia stopped =[")

    if message.content == ".triviastop" and is_running:
        is_running = False
        await client.send_message(channel, "OK, I'll stop after this question =[")

    if message.content == ".score":
        await client.send_message(channel, "<@" + user.id + "> " + "has a score of " + str(get_score(str(user))))

    if message.content == ".leaderboard":
        await client.send_message(channel, get_leaderboard())

    if message.content.startswith(".report"):
        await client.send_message(channel, "OK, Report sent!")
        report_message = str(user) + " sent a report: "
        if len(message.content) > 7:
            report_message += message.content[7:]
        else:
            report_message += "(no additional info given)"
        await client.send_message(discord.utils.get(message.server.members, name="MadScotty"), report_message)

# Returns the user's score
def get_score(user):

    global scorecard

    for i in range(0, len(scorecard)):
        temp_score_holder = scorecard[i].split('`')
        if temp_score_holder[0] == user:
            return temp_score_holder[1]
    else:
        return 0

# Returns the leaderboard as a Discord formatted code box
# This is an ugly way to do this, but whatevs, maybe I'll
# fix it later (lol) and I'm a few beers in so whatevs. 1v1
# me irl if you got beef, n00b scrub.
def get_leaderboard():
    
    global scorecard
    global score_reset_day

    # Check to see if leaderboard is empty
    if not scorecard:
        return "The leaderboard is empty!  Scores last reset on: " + score_reset_day

    top_length = min(10, len(scorecard))
    only_scores = []
    temp_score_holder = []

    # Separate users from scores
    for i in range(0, len(scorecard)):
        temp_score_holder = scorecard[i].split('`')
        # Kill the newline character if it somehow managed to sneak in
        if temp_score_holder[1].endswith("\n"):
            only_scores.append(int(temp_score_holder[1][:-1]))
        else:
            only_scores.append(int(temp_score_holder[1]))

    # Sort and put in descending order
    only_scores.sort()
    only_scores.reverse()

    # Now reattach scores
    lead_list = []
    for i in range(0, top_length):
        for j in range(0, len(scorecard)):
            temp_score_holder = scorecard[j].split('`')
            if int(temp_score_holder[1]) == only_scores[i] and scorecard[j] not in lead_list:
                lead_list.append(scorecard[j])

    # Format leaderbox
    leaderbox = "```Current top " + str(top_length) + "! (Last reset on: " + str(score_reset_day) + ")\n"
    for i in range(0, top_length):
        temp_score_holder = lead_list[i].split('`')
        name_splitter = temp_score_holder[0].split('#')
        leaderbox += str(i + 1) + ": " + name_splitter[0] + " with a score of " + str(temp_score_holder[1])
        if i < top_length - 1:
            leaderbox += "\n"

    leaderbox += "```"

    return leaderbox

# Reads from the question flie and sets the question and answer 
# variables and returns the question as a string
def get_question(q_number):
    
    global question
    global answer

    try:
        q_line = linecache.getline("question.txt", q_number)
        q_and_a = q_line.split('*')
        question = q_and_a[0]
        answer = q_and_a[1][:-1] #Slicing necessary to kill the newline character at the end
    except:
        print("Question file operation failed")

def get_hint(hint_number):
    
    global hint
    global answer

    # First hint - Give dashes
    if hint_number == 1:
        for i in range(0, len(answer)):
            if answer[i] == " ":
                hint += " "
            else:
                hint += "-"
        return

    # Second and third hints
    if hint_number == 2:
        reveal_number = max(int(len(answer) * 0.2), 1)
    else:
        reveal_number = max(int(len(answer) * 0.4), 2)

    if reveal_number > len(answer):
        reveal_number = len(answer)

    # Turn reveal_number of the dashes into letters
    letters_given = []
    while len(letters_given) < reveal_number:
        random_dash = random.randint(0, len(answer) - 1)        
        if hint[random_dash] == "-" and random_dash not in letters_given:
            letters_given.append(random_dash)

    # Rebuild the hint because of all the things python can do, it can't change a character in a string by index
    temp_hint = ""
    for i in range(0, len(answer)):
        if i in letters_given:
            temp_hint += answer[i]
        else:
            temp_hint += hint[i]

    hint = temp_hint

# Handles question asking and hint giving.
async def next_question(client, channel):

    global q_number
    global hint
    global question
    global answer
    global is_answered
    global timer
        
    await asyncio.sleep(3)
    timer = int(time.time())
    is_answered = False
    hint = ""
    q_number = random.randint(1,8658)
    get_question(q_number)

    await client.send_message(channel, "**Next Question!**\n" + str(q_number) + ": " + question)
    get_hint(1)
    await client.send_message(channel, "**Hint #1:**  " + hint)
        
    if not is_answered:
        await asyncio.sleep(10)

    if not is_answered:
        get_hint(2)
        await client.send_message(channel, "**Hint #2:**  " + hint)
    
    if not is_answered:
        await asyncio.sleep(10)

    if not is_answered:
        get_hint(3)
        await client.send_message(channel, "**Hint #3:**  " + hint)

    if not is_answered:
        await asyncio.sleep(10)

    if not is_answered:
        is_answered = True
        await client.send_message(channel, "Time's up!  The answer was:  **" + answer + "**")

# Somebody got the question right!!  Yay!!
async def question_answered(client, winner, channel):
    
    global is_answered
    global timer
    global scorecard

    is_answered = True
    answer_time = int(time.time()) - timer
    points_earned = (30 - answer_time) * 33 + 1

    # Create win message
    smartass = str(winner)
    smartass_id_formatted = "<@" + winner.id + ">"
    win_message = "**DING DING DING!!** " + smartass_id_formatted

    if answer_time < 10:
        win_message += " with the quick wit and lightning fingers got "
    elif answer_time < 20:
        win_message += " got "
    else:
        win_message += " subtly googled "

    win_message += "the right answer, **" + answer + "**, in **" + str(answer_time) + " seconds** and earned **" + str(points_earned) + " points!**"

    await client.send_message(channel, win_message)

    # Update score
    was_found = False
    for i in range(0, len(scorecard)):
        temp_score_holder = scorecard[i].split('`')
        if temp_score_holder[0] == smartass:
            was_found = True
            score_converter = int(temp_score_holder[1]) + points_earned
            scorecard[i] = temp_score_holder[0] + "`" + str(score_converter)

    # User wasn't found
    if not was_found:
        scorecard.append(smartass + "`" + str(points_earned))

    #Update scorecard
    #Yeah, there's a better way to do this, I know.
    #Yes, I know I'm playing with dangerous forces.
    #Yes, I know that everyone's gonna have a sad if this borks and kills everyone's highscores

    try:
        os.remove("score.bak")
        os.rename("score.card", "score.bak")
        score_file = open("score.card", "w")
        score_file.writelines(scorecard)
        score_file.close()
    except e:
        print("Scorecard writing operation failed")
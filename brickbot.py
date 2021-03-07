import discord
import os
import requests
import sqlite3
from random import randint
from tabulate import tabulate

#some constants used throughout the bot
client = discord.Client()

#game version
version="11.3.1"

#DON'T UPLOAD THESE TO VERSION CONTROL
#Riot Games API key
api_key = ''
#Discord Bot token
token = ''

#set up member database
connection = sqlite3.connect("members.db")
cursor = connection.cursor()
cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='members' ")
if cursor.fetchone()[0]==0:
    cursor.execute("CREATE TABLE members (summoner TEXT, summoner_id TEXT)")

#tells us when bot has connected to Discord
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    #don't respond to messages written by the bot
    if message.author == client.user:
        return

    #simple hello
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('$help'):
        await message.channel.send('`'+tabulate(get_help_array(), ["Command", "Description"], tablefmt="pretty")+'`')
    
    #add user to member DB
    if message.content.startswith('$add'):
        member = message.content.split(' ',1)[1]
        try:
            add_member(member)
        except ValueError as err:
            await message.channel.send(err.args[0])
            return
        await message.channel.send(member+' sucessfully added!')
    
    #remove user from member DB
    if message.content.startswith('$remove'):
        member = message.content.split(' ',1)[1]
        remove_member(member)
        await message.channel.send(member+' sucessfully removed!')

    #print the level of a specific player
    if message.content.startswith('$level '):
        summoner = message.content.split(' ',1)[1]
        info = get_summoner_info(summoner)
        await message.channel.send(summoner+' is level '+str(info['summonerLevel'])+'.')

    #print table of sorted levels for all players in member DB
    if message.content.startswith('$levels'):
        ret_message=''
        member_array = get_members()
        level_array = []
        for member in member_array:
            level = get_summoner_info(member[0])['summonerLevel']
            level_array.append([member[0],level])
        await message.channel.send('`'+tabulate(sort(level_array,1), ["Summoner", "Level"], tablefmt="pretty")+'`')

    #print table of sorted total mastery scores for all players in member DB
    if message.content.startswith('$scores'):
        ret_message=''
        member_array = get_members()
        mastery_array = []
        for member in member_array:
            id = member[1]
            mastery = get_total_mastery(id)
            mastery_array.append([member[0],mastery])
        await message.channel.send('`'+tabulate(sort(mastery_array,1), ["Summoner", "Total Mastery"], tablefmt="pretty")+'`')
    
    #print table of sorted mastery scores for a specific champion for all players in member DB
    if message.content.startswith('$mastery'):
        ret_message=''
        member_array = get_members()
        mastery_array = []
        try:
            champ_id = get_champ_id(message.content.split(' ',1)[1])
        except ValueError as err:
            await message.channel.send(err.args[0])
            return
        for member in member_array:
            id = member[1]
            mastery = get_mastery(id,champ_id)
            mastery_array.append([member[0],mastery[0],mastery[1]])
        await message.channel.send('`'+tabulate(sort(mastery_array,1), ["Summoner", "Mastery Points", "Mastery Level"], tablefmt="pretty")+'`')

    #print table of sorted solo/duo ranks for all players in member DB
    if message.content.startswith('$ranks'):
        ret_message=''
        member_array = get_members()
        rank_array = []
        for member in member_array:
            id = member[1]
            rank_array.append(get_rank(id, member[0], "RANKED_SOLO_5x5"))
        await message.channel.send('`'+tabulate(sort_rank(rank_array), ["Summoner", "Tier", "Rank", "LP"], tablefmt="pretty")+'`')

    #print table of sorted flex ranks for all players in member DB
    if message.content.startswith('$flex'):
        ret_message=''
        member_array = get_members()
        rank_array = []
        for member in member_array:
            id = member[1]
            rank_array.append(get_rank(id, member[0], "RANKED_FLEX_SR"))
        await message.channel.send('`'+tabulate(sort_rank(rank_array), ["Summoner", "Tier", "Rank", "LP"], tablefmt="pretty")+'`')


#return json of summoner info from Riot API
def get_summoner_info(summoner):
    r = requests.get(url="https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/"+summoner, params={'api_key': api_key})
    return r.json()

#return json of total mastery from Riot API
def get_total_mastery(summoner_id):
    r = requests.get(url="https://na1.api.riotgames.com/lol/champion-mastery/v4/scores/by-summoner/"+summoner_id, params={'api_key': api_key})
    return r.json()

#get champion ID number by champion name using Riot lookup table
def get_champ_id(champion):
    champion = champion.capitalize()
    dragon = "http://ddragon.leagueoflegends.com/cdn/"+version+"/data/en_US/champion/"+champion+".json"
    r = requests.get(url=dragon)
    if r.status_code != 200:
        raise ValueError("Champion does not exist, check your spelling.")
    return r.json()['data'][champion]['key']

#get specific players mastery on a specific champion using Riot API
def get_mastery(id, champ_id):
    r = requests.get(url="https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/"+id+"/by-champion/"+champ_id, params={'api_key': api_key})
    try:
        return [r.json()['championPoints'], r.json()['championLevel']]
    except:
        return [0,0]

#get a given player's rank for a given queue using Riot API
def get_rank(summoner_id, summoner, queue_type):
    r = requests.get(url="https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/"+summoner_id, params={'api_key': api_key})
    for x in range(0, len(r.json())):
        if r.json()[x]['queueType']==queue_type:
            queue=x
    try:
        return [r.json()[queue]['summonerName'], r.json()[queue]['tier'], r.json()[queue]['rank'], r.json()[queue]['leaguePoints']]
    except:
        
        return [summoner, "UNRANKED", "~", 0]

#return help string
def get_help_array():
    return [["$help","Prints this message"],["$add <summoner name>", "Add player to database using their summoner name"], ["$remove <summomner name>", "Remove player from database using summoner name"],
        ["$level <summoner name>", "Get a specific player's summoner level"],["$levels", "Get summoner levels for everybody in the database"],["$scores", "Get total mastery scores for everybody in the database"],
        ["$mastery <champion name>", "Get mastery scores for a particular champion for everybody in the dateabse"], ["$ranks", "Get solo/duo ranks for everybody in the database"],
        ["$flex","Get flex ranks for everybody in the database"]]

#check status code for potential problems from Riot API 
def check_status_code(response):
    if response.status_code != 200:
        raise ValueError(response.json()['status']['message'])

#pull a list of members from the members DB
def get_members():
    member_array = []
    rows = cursor.execute("SELECT summoner, summoner_id FROM members").fetchall()
    return rows

#add a memeber to the members DB
def add_member(member):
    r = requests.get(url="https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/"+member, params={'api_key': api_key})
    check_status_code(r)
    summoner_id = r.json()['id']
    cursor.execute("INSERT INTO members VALUES (?, ?)", (member, summoner_id))

#remove a member from the members DB
def remove_member(member):
    cursor.execute("DELETE FROM members WHERE summoner = ?", (member,))

#sort an array of ints with quick sort
def sort(array, index):
    if len(array) < 2:
        return array
    low, same, high = [], [], []
    pivot = array[randint(0, len(array) - 1)][index]
    for item in array:
        if item[index] < pivot:
                low.append(item)
        elif item[index] == pivot:
                same.append(item)
        elif item[index] > pivot:
                high.append(item)
    return sort(high, index) + same + sort(low, index)

#ranked tier dictionaries to help sort ranks
tier_dict = {"UNRANKED": 0, "IRON": 1, "BRONZE": 2, "SILVER": 3, "GOLD": 4, "PLATINUM": 5, "DIAMOND": 6, "MASTER": 7, "GRANDMASTER": 8, "CHALLENGER": 9}
rank_dict = {"~": 0, "IV": 1, "III": 2, "II": 3, "I": 4}

def greater_than_rank(rank1, rank2):
    if tier_dict[rank1[1]] > tier_dict[rank2[1]]:
        return True
    elif tier_dict[rank1[1]] == tier_dict[rank2[1]] and rank_dict[rank1[2]] > rank_dict[rank2[2]]:
        return True
    elif tier_dict[rank1[1]] == tier_dict[rank2[1]] and rank_dict[rank1[2]] == rank_dict[rank2[2]] and rank1[3] > rank2[3]:
        return True
    return False

def less_than_rank(rank1, rank2):
    if tier_dict[rank1[1]] < tier_dict[rank2[1]]:
        return True
    elif tier_dict[rank1[1]] == tier_dict[rank2[1]] and rank_dict[rank1[2]] < rank_dict[rank2[2]]:
        return True
    elif tier_dict[rank1[1]] == tier_dict[rank2[1]] and rank_dict[rank1[2]] == rank_dict[rank2[2]] and rank1[3] < rank2[3]:
        return True
    return False

#sort an array of ranks using a slightly modified quicksort
def sort_rank(array):
    if len(array) < 2:
        return array
    low, same, high = [], [], []
    pivot = array[randint(0, len(array) - 1)]
    for item in array:
        if less_than_rank(item, pivot):
            low.append(item)
        elif greater_than_rank(item, pivot):
            high.append(item)
        else:
            same.append(item)
        
    return sort_rank(high) + same + sort_rank(low)

#run bot
client.run(token)
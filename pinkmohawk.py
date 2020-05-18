"""
Created on 16 May 2020
@author: John Thomas
"""
from os import environ
import discord
from discord.ext import commands
import random
import math
from lookup import *

TOKEN = environ['TOKEN']

bot = commands.Bot(command_prefix='>')
savedPool = []

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("Shadowrun"))


def check_glitch(rolls):
    glitches = 0
    print("Glitch Check Rolls: " + str(rolls))
    for r in range(len(rolls)):
        if rolls[r] == 1:
            glitches += 1
    print("exited for loop")
    if glitches > len(rolls) / 2:
        return True
    else:
        return False

def get_hits(dicePool):
    hits = 0
    for d in range(len(dicePool)):
        if dicePool[d] >= 5:
            hits += 1
    return hits

def roll_dice_pool(dice):
    dicePool = []
    for d in range(dice):
        val = random.randint(1, 6)
        dicePool.append(val)
    return dicePool
            

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

@bot.command(aliases=['s'])
async def search(ctx, entry_type=None, search=None):
    if entry_type is None:
        await ctx.send("Matrix Search usage: `>search [type] [entry]`\nIf the entry is multiple words, they must be wrapped in double quotes (\"\").\nAvailable types: weapon, armor, matrix, gear, augmentation, streetpedia.")
        return

    if entry_type.lower() not in ENTRY_TYPES:
        await ctx.send("Matrix Search failed: \"" + entry_type + "\" is not an avaiable type. Available types: weapon, armor, matrix, gear, augmentation, streetpedia.")
        return

    if entry_type.lower() == "weapon":
        if search is None:
            await ctx.send("Command requires `[entry]`. Please try your search again.")

        await ctx.send("Performing Matrix search for \"" + search + "\"...")    
        weapon = lookup_weapon(search)
   
        if weapon is None:
            await ctx.send("Couldn't find a Matrix entry for \"" + search + "\". Try again.")
            await ctx.message.delete()
            return

        attackRatings = weapon["attack_ratings"]["close"] + "/" + weapon["attack_ratings"]["near"] + "/" + weapon["attack_ratings"]["medium"] + "/" + weapon["attack_ratings"]["far"] + "/" + weapon["attack_ratings"]["extreme"]

        embed = discord.Embed(title=weapon["name"], description=weapon["description"], color=0x00ff00)
        embed.add_field(name="DV", value=weapon["damage_value"], inline=False)
        embed.add_field(name="Attack Ratings", value=attackRatings, inline=False)
        embed.add_field(name="Availability", value=weapon["availability"], inline=False)
        embed.add_field(name="Cost", value=weapon["cost"] + u'\u00A5', inline=False)
        await ctx.send(embed=embed)
        await ctx.message.delete()
    
    if entry_type.lower() in ENTRY_TYPES:
        await ctx.send("There are currently no armor entries for that type in the database.")

@bot.command(aliases=['r'])
async def roll(ctx, *args):
    
    dice = int(args[0])
    print("Dice: " + str(dice))
    #threshhold = 0
    if len(args) > 1:
        threshhold = int(args[1])

    try:
        if int(dice) > 100:
            await ctx.send("Woah there, chummer! That's a lot of dice. I can only roll 100 at a time, however. Try again!")
            return

        results = ("Rolling %i:game_die: for %s." % (dice, ctx.message.author.mention))

        dicePool = roll_dice_pool(dice)
        hits = get_hits(dicePool)
        isGlitch = check_glitch(dicePool)
        dicePool.sort()
        print(dicePool)
        results += ("\nHits: **" + str(hits) + "** " + str(dicePool))

        if isGlitch and hits == 0:
            results += ("\n:bangbang:**CRITICAL GLITCH**:bangbang:")
        elif isGlitch:
            results += ("\n:bang:**GLITCH**:bang:")
        # if threshhold:

        #     if hits >= threshhold:
        #         results += ("\n**SUCCESS**")
        #         if isGlitch:
        #             results += ("\n:bang:**GLITCH**:bang:")
        #     else:
        #         results += ("\n**FAILURE**") 
        #         if isGlitch and hits == 0:
        #             results += ("\n*:bangbang:*CRITICAL GLITCH**:bangbang:")
        #     await ctx.send("Rolling %i:game_die: for %s. (Threshhold: %i)" % (dice, ctx.message.author.mention, threshhold) )    
             
        # else:
        #     await ctx.send("Rolling %i:game_die: for %s" % (dice, ctx.message.author.mention))
        #     if isGlitch and hits == 0:
        #         results += ("\n:bangbang:**CRITICAL GLITCH**:bangbang:")
        #     elif isGlitch:
        #         results += ("\n:bang:**GLITCH**:bang:")

      
        await ctx.send(results)
        await ctx.message.delete()

    except Exception as e:
        print("Error: " + str(e))
        await ctx.send("Error: " + str(e))
        return
        
@bot.command(aliases=['rr'])
async def reroll(ctx, rollval : int):
    try:
        if len(savedPool) > 0:
            for r in savedPool:
                if savedPool[r] == rollval:
                    newval = random.randint(1, 6)
                    print("New value: " + str(newval))
                    savedPool[r] = newval
                    savedPool.sort()
                    await ctx.send("%s rerolled a %i and got a %i instead. The new dice pool is below:" % (ctx.message.author.mention, rollval, newval))
                    resultString = ("Hits: **" + str(get_hits(savedPool)) + "** " + str(savedPool))
                    await ctx.send(resultString)
                    return
                else:
                    await ctx.send("There are no %is in the active dice pool. Try again." % (rollval))
        else:
            await ctx.send("There is nothing to reroll. Try rolling first.")

    except Exception as e:
        print("Error: " + str(e))
        await ctx.send("Error: " + str(e))
        return


@bot.command()
async def buyhits(ctx, dice: int):
    hits = math.floor(dice / 4)
    await ctx.send("%s bought %i hits from %i:game_die:." % (ctx.message.author.mention, hits, dice))
    await ctx.message.delete()

@bot.command()
async def adp(ctx):
    # Prints the current active dice pool with hits and glitches
    await ctx.send("The current active dice pool is:")
    await ctx.send("Hits: **" + str(get_hits(savedPool)) + "** " + str(savedPool))
    await ctx.message.delete()

@bot.command()
async def legal(ctx):
    await ctx.send("The Topps Company, Inc. has sole ownership of the names, logo, artwork, marks, photographs, sounds, audio, video and/or any proprietary material used in connection with the game Shadowrun. The Topps Company, Inc. has granted permission to Pink Mohawk to use such names, logos, artwork, marks and/or any proprietary materials for promotional and informational purposes on its website but does not endorse, and is not affiliated with Pink Mohawk in any official capacity whatsoever.")
    await ctx.message.delete()

bot.run(TOKEN)

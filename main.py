import discord
from discord.ext import commands
import sqlite3
import random
import asyncio

conn = sqlite3.connect(":memory:")
c = conn.cursor()
token = "token"
bot = commands.Bot(command_prefix=("b.", "bank.", "b!"))
bot.remove_command('help')

c.execute("""CREATE TABLE bank(
            username text,
            money_in_hand integer,
            money_in_bank integer,
            items_bought text,
            fishing_items text,
            hunting_items text,
            restoration_code integer
    )""")
conn.commit()
c.execute("""CREATE TABLE shop(
            item text,
            seller text,
            cost integer
    )""")
conn.commit()
c.execute("""CREATE TABLE russianroulette(
            players_in_round text,
            round_starter text,
            bet integer,
            game_going integer
    )""")
conn.commit()
c.execute("""INSERT INTO russianroulette VALUES (?, ?, ?, ?)""", ("none", "none", 0, 0))
conn.commit()


@bot.command(aliases=["stp"])
async def setup(ctx):
    c.execute("SELECT * FROM bank WHERE username=?", (str(ctx.author),))
    user_db = c.fetchone()
    if not user_db:
        await ctx.send("What will your recovery key be? (Please only use a whole number)")

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        recovery_key = await bot.wait_for("message", check=check)
        try:
            int(recovery_key.content)
            works = True
        except ValueError:
            works = False
        if works:
            c.execute("""INSERT INTO bank VALUES (?, 50, 0, ?, ?, ?, ?)""",
                      (str(ctx.author), "nothing", "", "", int(recovery_key.content),))
            conn.commit()
            embed = discord.Embed(title="Successfully setup the account!", color=0x109414)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Please use a whole number for your recovery key.", color=0xee4f4f)
            await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="You have already setup your account!", color=0xee4f4f)
        await ctx.send(embed=embed)


@bot.command(aliases=["bal", "bl"])
async def balance(ctx, *, user=None):
    if user is None:
        user = str(ctx.author)
    user = str(user)
    c.execute("SELECT * FROM bank WHERE username=?", (user,))
    user_db = c.fetchone()
    if user_db:
        embed = discord.Embed(title=f"{user}", color=0x109414)
        embed.add_field(name="Money In Hand:", value=f":moneybag:{user_db[1]}", inline=False)
        embed.add_field(name="Money In Bank:", value=f":moneybag:{user_db[2]}", inline=False)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="Error:",
                              description="You have either not setup your account, that user doesn't exist, or you changed your username, to restore your money if you changed your username, please use command `bank.restore`",
                              color=0xee4f4f)
        await ctx.send(embed=embed)


@bot.command()
@commands.cooldown(1, 15, commands.BucketType.user)
async def work(ctx):
    number = random.randint(1, 100)
    c.execute("SELECT * FROM bank WHERE username=?", (str(ctx.author),))
    user_db = c.fetchone()
    if user_db:
        if number > 80:
            loss = random.randint(25, 50)
            amount_in_hand = user_db[1]
            new_amount = amount_in_hand - loss
            c.execute("""UPDATE bank
                        SET money_in_hand=?
                        WHERE username=?""", (new_amount, str(ctx.author),))
            conn.commit()
            embed = discord.Embed(title=f"You just lost {loss} dollars.", color=0xee4f4f)
            await ctx.send(embed=embed)
        elif number < 80:
            pay = random.randint(25, 150)
            amount_in_hand = user_db[1]
            new_amount = amount_in_hand + pay
            c.execute("""UPDATE bank
                        SET money_in_hand=?
                        WHERE username=?""", (new_amount, str(ctx.author),))
            conn.commit()
            embed = discord.Embed(title=f"You just earned {pay} dollars!", color=0x109414)
            await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="Error:",
                              description="You have either not setup your account, or you changed your username, if you changed your username, to restore your money if you changed your username, please use command `bank.restore`",
                              color=0xee4f4f)
        await ctx.send(embed=embed)


@bot.command(aliases=["dep"])
async def deposit(ctx, *, amount="all"):
    c.execute("SELECT * FROM bank WHERE username=?", (str(ctx.author),))
    user_db = c.fetchone()
    if user_db[1] > 0:
        if user_db:
            if amount == "all":
                old_amount = user_db[1]
                new_amount = user_db[1] + user_db[2]
                c.execute("""UPDATE bank
                            SET money_in_bank=?, money_in_hand=?
                            WHERE username=?""", (new_amount, 0, str(ctx.author),))
                conn.commit()
                embed = discord.Embed(title=f"Successfully deposited {old_amount} dollars!", color=0x109414)
                await ctx.send(embed=embed)
            elif int(amount) > 0 and user_db[1] <= int(amount):
                new_amount = int(amount) + user_db[2]
                c.execute("""UPDATE bank
                            SET money_in_bank=?, money_in_hand=?
                            WHERE username=?""", (new_amount, user_db[1] - int(amount), str(ctx.author),))
                conn.commit()
                embed = discord.Embed(title=f"Successfully deposited {amount} dollars!", color=0x109414)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title="You specified an invalid amount!", color=0xee4f4f)
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Error:",
                                  description="You have either not setup your account, or you changed your username, to restore your money if you changed your username, please use command `bank.restore`",
                                  color=0x109414)
            await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="You specified an invalid amount!", color=0xee4f4f)
        await ctx.send(embed=embed)


@bot.command(aliases=["wd"])
async def withdraw(ctx, *, amount="all"):
    c.execute("SELECT * FROM bank WHERE username=?", (str(ctx.author),))
    user_db = c.fetchone()
    if user_db[2] > 0:
        if user_db:
            if amount == "all":
                old_amount = user_db[2]
                new_amount = user_db[2] + user_db[1]
                c.execute("""UPDATE bank
                            SET money_in_bank=?, money_in_hand=?
                            WHERE username=?""", (0, new_amount, str(ctx.author),))
                conn.commit()
                embed = discord.Embed(title=f"Successfully withdrew {old_amount} dollars!", color=0x109414)
                await ctx.send(embed=embed)
            elif int(amount) > 0 and user_db[2] <= int(amount):
                new_amount = int(amount) + user_db[1]
                c.execute("""UPDATE bank
                            SET money_in_bank=?, money_in_hand=?
                            WHERE username=?""", (user_db[2] - int(amount), new_amount, str(ctx.author),))
                conn.commit()
                embed = discord.Embed(title=f"Successfully withdrew {amount} dollars!", color=0x109414)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title="You specified an invalid amount!", color=0xee4f4f)
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Error:",
                                  description="You have either not setup your account, or you changed your username, to restore your money if you changed your username, please use command `bank.restore`",
                                  color=0x109414)
            await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="You specified an invalid amount!", color=0xee4f4f)
        await ctx.send(embed=embed)


@bot.command()
async def sell(ctx, *, item_and_price):
    item_name = item_and_price.split(":")[0]
    try:
        item_price = int(item_and_price.split(":")[1])
        if item_price < 0:
            works = False
        else:
            works = True
    except ValueError:
        item_price = "MY FAVORITE"
        works = False
    item_in_shop = False
    c.execute("SELECT * FROM shop""")
    items_in_shop = c.fetchall()
    for item in items_in_shop:
        if item_name in item:
            item_in_shop = True
    c.execute("SELECT * FROM bank WHERE username=?", (str(ctx.author),))
    user_db = c.fetchone()
    if not item_in_shop:
        if user_db:
            if works:
                if item_price != "MY FAVORITE":
                    c.execute("""INSERT INTO shop VALUES (?, ?, ?)""", (item_name, str(ctx.author), item_price,))
                    conn.commit()
                    embed = discord.Embed(title="Successfully put the item on sale!", color=0x109414)
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(title="Please enter a whole number for the price.", color=0xee4f4f)
                    await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title="You can't put a price under 0!", color=0xee4f4f)
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Error:",
                                  description="You have either not setup your account, or you changed your username, to restore your money if you changed your username, please use command `bank.restore`",
                                  color=0xee4f4f)
            await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="There is already an item with that name!", color=0xee4f4f)
        await ctx.send(embed=embed)


@bot.command()
async def shop(ctx):
    c.execute("SELECT * FROM shop""")
    items_in_shop = c.fetchall()
    embed = discord.Embed(title="Items In The Shop:", color=0x109414)
    if items_in_shop:
        for item in items_in_shop:
            embed.add_field(name=f"Item Name: {item[0]}",
                            value=f"Sold By: `{item[1]}` Item Price: :moneybag:`{item[2]}`", inline=False)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="There are no items in the shop.", color=0x109414)
        await ctx.send(embed=embed)


@bot.command()
async def buy(ctx, *, item):
    c.execute("SELECT * FROM shop WHERE item=?""", (item,))
    item_stats = c.fetchone()
    if item_stats:
        if item_stats[1] == str(ctx.author):
            embed = discord.Embed(title="You can't buy from yourself!", color=0x109414)
            await ctx.send(embed=embed)
        else:
            c.execute("SELECT * FROM bank WHERE username=?", (str(ctx.author),))
            user_db = c.fetchone()
            if user_db:
                if user_db[1] >= item_stats[2]:
                    c.execute("DELETE FROM shop WHERE item=?""", (item,))
                    conn.commit()
                    c.execute("""UPDATE bank
                                    SET money_in_bank=?, money_in_hand=?, items_bought=?
                                    WHERE username=?""",
                              (0, user_db[1] - item_stats[2], f"{item_stats[0]}:", str(ctx.author),))
                    conn.commit()
                    embed = discord.Embed(title=f"Successfully bought the item {item_stats[0]}!", color=0x109414)
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(title="You don't have enough money in hand!", color=0x109414)
                    await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title="Error:",
                                      description="You have either not setup your account, or you changed your username, to restore your money if you changed your username, please use command `bank.restore`",
                                      color=0xee4f4f)
                await ctx.send(embed=embed)


@bot.command(aliases=["inv"])
async def inventory(ctx, *, user=None):
    if user is None:
        user = str(ctx.author)
    user = str(user)
    c.execute("SELECT * FROM bank WHERE username=?", (user,))
    user_db = c.fetchone()
    if user_db:
        items_bought = user_db[3].split(":")
        items_bought.pop(-1)
        embed = discord.Embed(title=f"User: {user}'s Inventory", color=0x109414)
        for item in items_bought:
            embed.add_field(name=f"Item Name: `{item}`", value=f"What a beautiful item!", inline=False)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="Error:",
                              description="You have either not setup your account, or you changed your username, to restore your money if you changed your username, please use command `bank.restore`",
                              color=0xee4f4f)
        await ctx.send(embed=embed)


@bot.command()
async def rob(ctx, *, user):
    c.execute("""SELECT * FROM bank WHERE username=?""", (user,))
    user_to_rob = c.fetchone()
    c.execute("""SELECT * FROM bank WHERE username=?""", (str(ctx.author),))
    user_db = c.fetchone()
    if user_db:
        if user_to_rob:
            if user_to_rob[1] >= 100:
                number = random.randint(1, 100)
                if number < 75:
                    c.execute("""UPDATE bank
                                SET money_in_hand=?
                                WHERE username=?""", (user_to_rob[1] - int(user_to_rob / 2), user,))
                    conn.commit()
                    c.execute("""UPDATE bank
                                SET money_in_hand=?
                                WHERE username=?""",
                              (user_db[1] + user_to_rob[1] - int(user_to_rob / 2), str(ctx.author),))
                    embed = discord.Embed(
                        title=f"You just pick-pocketed `{user}` for :moneybag:`{user_to_rob[1] - int(user_to_rob / 2)}`!",
                        color=0x109414)
                    await ctx.send(embed=embed)
                else:
                    c.execute("""UPDATE bank
                                SET money_in_hand=?
                                WHERE username=?""", (user_db[1] - 250, str(ctx.author),))
                    conn.commit()
                    embed = discord.Embed(
                        title="You were caught by the :cop:police and fined for :moneybag:`250` dollars!",
                        color=0x109414)
                    await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title="That person doesn't have enough money on hand.", color=0x109414)
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="That person hasn't setup their account yet.", color=0x109414)
            await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="Error:",
                              description="You have either not setup your account, or you changed your username, to restore your money if you changed your username, please use command `bank.restore`",
                              color=0xee4f4f)
        await ctx.send(embed=embed)


@bot.command(aliases=["num", "numg"])
async def numberguess(ctx):
    c.execute("""SELECT * FROM bank WHERE username=?""", (str(ctx.author),))
    user_db = c.fetchone()
    if user_db:
        number_to_be_shown = random.randint(1, 100)
        number_next = random.randint(1, 100)
        if number_next == number_to_be_shown:
            number_next += 1
        if number_next > number_to_be_shown:
            bigger = True
        else:
            bigger = False
        if number_next < number_to_be_shown:
            smaller = True
        else:
            smaller = False
        embed = discord.Embed(
            title=f"The first number is `{number_to_be_shown}`. Will the next number be lower or higher?",
            color=0x109414)
        await ctx.send(embed=embed)
        higher_or_lower = await bot.wait_for("message")
        if higher_or_lower.content == "lower" and smaller:
            c.execute("""UPDATE bank
                        SET money_in_hand=?
                        WHERE username=?""", (user_db[1] + 50, str(ctx.author),))
            conn.commit()
            embed = discord.Embed(title="You just earned :moneybag:`50` dollars!", color=0x109414)
            await ctx.send(embed=embed)
        elif higher_or_lower.content == "higher" and bigger:
            c.execute("""UPDATE bank
                                    SET money_in_hand=?
                                    WHERE username=?""", (user_db[1] + 50, str(ctx.author),))
            conn.commit()
            embed = discord.Embed(title="You just earned :moneybag:`50` dollars!", color=0x109414)
            await ctx.send(embed=embed)
        else:
            if smaller:
                embed = discord.Embed(title=f"The number was bigger than `{number_to_be_shown}`!", color=0x109414)
                await ctx.send(embed=embed)
            elif bigger:
                embed = discord.Embed(title=f"The number was smaller than `{number_to_be_shown}`!", color=0x109414)
                await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="Error:",
                              description="You have either not setup your account, or you changed your username, to restore your money if you changed your username, please use command `bank.restore`",
                              color=0xee4f4f)
        await ctx.send(embed=embed)


@bot.command(aliases=["bj"])
async def blackjack(ctx, bet="all"):
    c.execute("""SELECT * FROM bank WHERE username=?""", (str(ctx.author),))
    user_db = c.fetchone()
    if bet == "all" and user_db:
        bet = user_db[1]
    if user_db:
        if user_db[1] >= int(bet):
            cards = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
            values_of_cards = {"A": 10,
                               "2": 2,
                               "3": 3,
                               "4": 4,
                               "5": 5,
                               "6": 6,
                               "7": 7,
                               "8": 8,
                               "9": 9,
                               "10": 10,
                               "J": 10,
                               "Q": 10,
                               "K": 10}
            card_types = [":heart:", ":spades:", ":diamonds:", ":clubs:"]
            user_cards = [random.choice(cards), random.choice(cards)]
            dealer_cards = [random.choice(cards)]
            embed = discord.Embed(title=f"Blackjack game started by {ctx.author} with a bet of :moneybag:`{bet}`!",
                                  description="Say `stay` to stay or `hit` to draw another card.", color=0x109414)
            values_of_current_dealer_cards = sum([values_of_cards[x] for x in dealer_cards])
            values_of_current_user_cards = sum([values_of_cards[x] for x in user_cards])
            user_cards_formatted = " - ".join([x + random.choice(card_types) for x in user_cards])
            dealer_cards_formatted = f"{dealer_cards[0] + random.choice(card_types)} - XX"
            embed.add_field(name="Your Hand:", value=f"{user_cards_formatted}\nValue: {values_of_current_user_cards}",
                            inline=True)
            embed.add_field(name="Dealer Hand:",
                            value=f"{dealer_cards_formatted}\nValue: {values_of_current_dealer_cards}", inline=True)
            await ctx.send(embed=embed)

            def check(msg):
                return msg.author == ctx.author and msg.content == "hit" or "stay" and msg.channel == ctx.channel

            while True:
                pass_or_draw = await bot.wait_for("message", check=check)
                if pass_or_draw.content.lower() == "hit":
                    user_cards.append(random.choice(cards))
                    values_of_current_user_cards = sum([values_of_cards[x] for x in user_cards])
                    if values_of_current_user_cards > 21:
                        c.execute("""UPDATE bank
                                    SET money_in_hand=?
                                    WHERE username=?""",
                                  (user_db[1] - int(bet), str(ctx.author),))
                        conn.commit()
                        user_cards_formatted = " - ".join([x + random.choice(card_types) for x in user_cards])
                        embed = discord.Embed(
                            title=f"Blackjack game started by {ctx.author} with a bet of :moneybag:`{bet}`!",
                            description=f"You just lost :moneybag:`{bet}`.", color=0xee4f4f)
                        embed.add_field(name="Your Hand:",
                                        value=f"{user_cards_formatted}\nValue: {values_of_current_user_cards}",
                                        inline=False)
                        embed.add_field(name="Dealer Hand:",
                                        value=f"{dealer_cards_formatted}\nValue: {values_of_current_dealer_cards}",
                                        inline=False)
                        await ctx.send(embed=embed)
                        break
                    elif values_of_current_user_cards == 21:
                        c.execute("""UPDATE bank
                                    SET money_in_hand=?
                                    WHERE username=?""",
                                  (user_db[1] + int(bet), str(ctx.author),))
                        conn.commit()
                        user_cards_formatted = " - ".join([x + random.choice(card_types) for x in user_cards])
                        embed = discord.Embed(
                            title=f"Blackjack game started by {ctx.author} with a bet of :moneybag:`{bet}`!",
                            description=f"You just won :moneybag:`{bet}`!", color=0x109414)
                        embed.add_field(name="Your Hand:",
                                        value=f"{user_cards_formatted}\nValue: {values_of_current_user_cards}",
                                        inline=False)
                        embed.add_field(name="Dealer Hand:",
                                        value=f"{dealer_cards_formatted}\nValue: {values_of_current_dealer_cards}",
                                        inline=False)
                        await ctx.send(embed=embed)
                        break
                    user_cards_formatted = " - ".join([x + random.choice(card_types) for x in user_cards])
                    embed = discord.Embed(
                        title=f"Blackjack game started by {ctx.author} with a bet of :moneybag:`{bet}`!",
                        description="Say `stay` to stay or `hit` to draw another card.", color=0x006118)
                    embed.add_field(name="Your Hand:",
                                    value=f"{user_cards_formatted}\nValue: {values_of_current_user_cards}", inline=True)
                    embed.add_field(name="Dealer Hand:",
                                    value=f"{dealer_cards_formatted}\nValue: {values_of_current_dealer_cards}",
                                    inline=True)
                    await ctx.send(embed=embed)
                elif pass_or_draw.content.lower() == "stay":
                    while True:
                        dealer_cards.append(random.choice(cards))
                        values_of_current_dealer_cards = sum([values_of_cards[x] for x in dealer_cards])
                        if values_of_current_dealer_cards >= 17:
                            if values_of_current_dealer_cards > 21:
                                c.execute("""UPDATE bank
                                            SET money_in_hand=?
                                            WHERE username=?""",
                                          (user_db[1] + int(bet), str(ctx.author),))
                                conn.commit()
                                dealer_cards_formatted = " - ".join(
                                    [x + random.choice(card_types) for x in dealer_cards])
                                embed = discord.Embed(
                                    title=f"Blackjack game started by {ctx.author} with a bet of :moneybag:`{bet}`!",
                                    description=f"You just won :moneybag:`{bet}`!", color=0x109414)
                                embed.add_field(name="Your Hand:",
                                                value=f"{user_cards_formatted}\nValue: {values_of_current_user_cards}",
                                                inline=False)
                                embed.add_field(name="Dealer Hand:",
                                                value=f"{dealer_cards_formatted}\nValue: {values_of_current_dealer_cards}",
                                                inline=False)
                                await ctx.send(embed=embed)
                                break
                            elif values_of_current_dealer_cards > values_of_current_user_cards:
                                c.execute("""UPDATE bank
                                            SET money_in_hand=?
                                            WHERE username=?""",
                                          (user_db[1] - int(bet), str(ctx.author),))
                                conn.commit()
                                dealer_cards_formatted = " - ".join(
                                    [x + random.choice(card_types) for x in dealer_cards])
                                embed = discord.Embed(
                                    title=f"Blackjack game started by {ctx.author} with a bet of :moneybag:`{bet}`!",
                                    description=f"You just lost :moneybag:`{bet}`.", color=0xee4f4f)
                                embed.add_field(name="Your Hand:",
                                                value=f"{user_cards_formatted}\nValue: {values_of_current_user_cards}",
                                                inline=False)
                                embed.add_field(name="Dealer Hand:",
                                                value=f"{dealer_cards_formatted}\nValue: {values_of_current_dealer_cards}",
                                                inline=False)
                                await ctx.send(embed=embed)
                                break
                            elif values_of_current_dealer_cards < values_of_current_user_cards:
                                c.execute("""UPDATE bank
                                            SET money_in_hand=?
                                            WHERE username=?""",
                                          (user_db[1] + int(bet), str(ctx.author),))
                                conn.commit()
                                dealer_cards_formatted = " - ".join(
                                    [x + random.choice(card_types) for x in dealer_cards])
                                embed = discord.Embed(
                                    title=f"Blackjack game started by {ctx.author} with a bet of :moneybag:`{bet}`!",
                                    description=f"You just won :moneybag:`{bet}`!", color=0x109414)
                                embed.add_field(name="Your Hand:",
                                                value=f"{user_cards_formatted}\nValue: {values_of_current_user_cards}",
                                                inline=False)
                                embed.add_field(name="Dealer Hand:",
                                                value=f"{dealer_cards_formatted}\nValue: {values_of_current_dealer_cards}",
                                                inline=False)
                                await ctx.send(embed=embed)
                                break
                            elif values_of_current_dealer_cards == values_of_current_user_cards:
                                dealer_cards_formatted = " - ".join(
                                    [x + random.choice(card_types) for x in dealer_cards])
                                embed = discord.Embed(
                                    title=f"Blackjack game started by {ctx.author} with a bet of :moneybag:`{bet}`!",
                                    description=f"Tie game, you will receive your bet back.", color=0x767474)
                                embed.add_field(name="Your Hand:",
                                                value=f"{user_cards_formatted}\nValue: {values_of_current_user_cards}",
                                                inline=False)
                                embed.add_field(name="Dealer Hand:",
                                                value=f"{dealer_cards_formatted}\nValue: {values_of_current_dealer_cards}",
                                                inline=False)
                                await ctx.send(embed=embed)
                                break
                            break
    else:
        embed = discord.Embed(title="Error:",
                              description="You have either not setup your account, or you changed your username, to restore your money if you changed your username, please use command `bank.restore`",
                              color=0xee4f4f)
        await ctx.send(embed=embed)

    user_cards = []
    dealer_cards = []


@bot.command(aliases=["slt", "st", "slot"])
async def slots(ctx):
    c.execute("""SELECT * FROM bank WHERE username=?""", (str(ctx.author),))
    user_db = c.fetchone()
    if user_db:
        possible_combos = [":cherries:", ":lemon:", ":heart:", ":grapes:", ":diamond_shape_with_a_dot_inside:",
                           ":orange_circle:", ":watermelon:", ":bell:", ":four_leaf_clover:", "7", "BAR"]
        combinations = [random.choice(possible_combos) for _ in range(3)]
        seven_or_bar = 0
        for combo in combinations:
            if combo == "BAR" or combo == "7":
                seven_or_bar += 1
        if seven_or_bar == 3:
            you_won_or_lost = "won!"
        else:
            you_won_or_lost = "lost."
        if you_won_or_lost == "lost.":
            color = 0xee4f4f
        else:
            color = 0x109414
        embed = discord.Embed(title=f"You {you_won_or_lost}",
                              description=f"{combinations[0]} - {combinations[1]} - {combinations[2]}", color=color)
        await ctx.send(embed=embed)
        if you_won_or_lost == "won!":
            c.execute("""UPDATE bank
                        SET money_in_hand=?
                        WHERE username=?""",
                      (user_db[1] + 2000, str(ctx.author),))
            conn.commit()
            embed = discord.Embed(title="You just earned :moneybag:2000 dollars", color=0x109414)
            await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="Error:",
                              description="You have either not setup your account, or you changed your username, to restore your money if you changed your username, please use command `bank.restore`",
                              color=0xee4f4f)
        await ctx.send(embed=embed)


@bot.command(aliases=["rr", "russian", "roulette"])
async def russianroulette(ctx, *, args="start:50"):
    c.execute("""SELECT * FROM russianroulette""")
    russian_roulette = c.fetchone()
    c.execute("""SELECT * FROM bank WHERE username=?""", (str(ctx.author),))
    user_db = c.fetchone()
    if user_db:
        if "start" in args.lower():
            if russian_roulette[3] == 0:
                game_going = 1
                players_playing = f"{str(ctx.author)}`|`"
                bet = int(args.split(":")[1])
                player_started = str(ctx.author)
                c.execute("""UPDATE russianroulette
                            SET players_in_round=?, round_starter=?, bet=?, game_going=?""",
                          (players_playing, player_started, bet, game_going))
                conn.commit()
                embed = discord.Embed(
                    title=f"{player_started} has started a russian roulette game, with a bet of :moneybag:{bet}!",
                    color=0x109414)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title="A game is already going!", color=0xee4f4f)
                await ctx.send(embed=embed)
        elif "join" in args.lower():
            if user_db[1] >= russian_roulette[2]:
                if str(ctx.author) not in russian_roulette[0].split("`|`"):
                    players_playing = russian_roulette[0]
                    players_playing += f"{str(ctx.author)}`|`"
                    c.execute("""UPDATE russianroulette
                                SET players_in_round=?""", (players_playing,))
                    conn.commit()
                    c.execute("""UPDATE bank
                                SET money_in_hand=?
                                WHERE username=?""", (user_db[1] - russian_roulette[2], str(ctx.author),))
                    conn.commit()
                    embed = discord.Embed(title=f"Player {str(ctx.author)} joined the russian roulette match!",
                                          description="The players in the match are:", color=0x109414)
                    players_playing = players_playing.split("`|`")
                    players_playing.pop(-1)
                    for i in range(len(players_playing)):
                        embed.add_field(name=players_playing[i], value=f"Player number {i}.", inline=False)
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(title="You are already in the match!", color=0xee4f4f)
                    await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title="You specified an invalid amount!", color=0xee4f4f)
                await ctx.send(embed=embed)
        elif "force" in args.lower():
            if user_db[0] == russian_roulette[1]:
                players_playing = russian_roulette[0].split("`|`")
                print(players_playing)
                players_playing.pop(-1)
                print(players_playing)
                original_players_playing = players_playing[:]
                players_in_round = players_playing[:]
                while True:
                    if len(players_in_round) == 1:
                        c.execute("""UPDATE bank
                                    SET money_in_hand=?
                                    WHERE username=?""",
                                  (user_db[1] + int(russian_roulette[2]), str(players_in_round[0]),))
                        conn.commit()
                        embed = discord.Embed(title=f"User {str(players_in_round[0])}: won the game and earned :moneybag:{russian_roulette[2]}", color=0x109414)
                        await ctx.send(embed=embed)
                        break
                    for player in players_in_round:
                        await asyncio.sleep(1)
                        embed = discord.Embed(title=f"User {player} points the gun at themselves...", color=0x109414)
                        await ctx.send(embed=embed)
                        await asyncio.sleep(5)
                        number = random.randint(1, 100)
                        if number < 60:
                            embed = discord.Embed(title=f"**CLICK!** User {player} hasn't shot themselves!", color=0x109414)
                            await ctx.send(embed=embed)
                        elif number > 60:
                            players_in_round.remove(player)
                            embed = discord.Embed(title=f"**BANG!** User {player} shot themselves!", color=0xee4f4f)
                            await ctx.send(embed=embed)
                c.execute("""UPDATE russianroulette
                            SET game_going=0""")
                conn.commit()
                original_players_playing = [x for x in original_players_playing if x in players_playing]
                for player in original_players_playing:
                    c.execute("""UPDATE bank
                                SET money_in_hand=?
                                WHERE username=?""",
                              (user_db[1] - int(russian_roulette[2]), str(player),))
                    conn.commit()
            else:
                embed = discord.Embed(title="You cannot start the game!", color=0xee4f4f)
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="No such argument.", color=0xee4f4f)
            await ctx.send(embd=embed)
    else:
        embed = discord.Embed(title="Error:",
                              description="You have either not setup your account, or you changed your username, to restore your money if you changed your username, please use command `bank.restore`",
                              color=0xee4f4f)
        await ctx.send(embed=embed)

@bot.command(aliases=["fishinv", "fish_inv", "fishinventory", "fishing_inventory", "fishinginventory", "fi"])
async def fish_inventory(ctx, *, user=None):
    if user is None:
        user = str(ctx.author)
    c.execute("""SELECT * FROM bank WHERE username=?""", (user,))
    user_db = c.fetchone()
    if user_db:
        embed = discord.Embed(title="Your fishing inventory:", color=0x109414)
        fishing_inventory = user_db[4].split("`")
        fishing_inventory.pop(-1)
        if len(fishing_inventory) == 0:
            embed = discord.Embed(title="Your fishing inventory is empty!", color=0xee4f4f)
            await ctx.send(embed=embed)
        else:
            for fishing_item in fishing_inventory:
                embed.add_field(name=fishing_item, value="What a nice item!", inline=False)
            await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="Error:",
                              description="You have either not setup your account, or you changed your username, to restore your money if you changed your username, please use command `bank.restore`",
                              color=0xee4f4f)
        await ctx.send(embed=embed)

@bot.command()
async def fish(ctx):
    c.execute("""SELECT * FROM bank WHERE username=?""", (str(ctx.author),))
    user_db = c.fetchone()
    if user_db:
        items_you_can_catch_common = ["Common Octopus:octopus:", "Common Flounder:fish:", "Common Salmon:fish:", "Common Shark:shark:", "Common Trout:fish:", "Common Cod:fish:", "Common Duck:duck:"]
        items_you_can_catch_uncommon = ["Uncommon Octopus:octopus:", "Uncommon Flounder:fish:", "Uncommon Salmon:fish:", "Uncommon Shark:shark:", "Uncommon Trout:fish:", "Uncommon Cod:fish:", "Uncommon Duck:duck:"]
        items_you_can_catch_rare = ["Rare Octopus:octopus:", "Rare Flounder:fish:", "Rare Salmon:fish:", "Rare Shark:shark:", "Rare Trout:fish:", "Rare Cod:fish:", "Rare Duck:duck:"]
        number = random.randint(1, 100)
        if number < 50:
            item_you_caught = random.choice(items_you_can_catch_common)
        elif number < 75:
            item_you_caught = random.choice(items_you_can_catch_uncommon)
        else:
            item_you_caught = random.choice(items_you_can_catch_rare)
        c.execute("""UPDATE bank
                    SET fishing_items=?
                    WHERE username=?""", (user_db[4] + f"{item_you_caught}`", str(ctx.author),))
        conn.commit()
        embed = discord.Embed(title=f"You caught a(n) {item_you_caught}!", color=0x109414)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="Error:",
                              description="You have either not setup your account, or you changed your username, to restore your money if you changed your username, please use command `bank.restore`",
                              color=0xee4f4f)
        await ctx.send(embed=embed)

@bot.command(aliases=["sf", "sellfish", "fishsell"])
async def sell_fish(ctx, *, amount="all"):
    c.execute("""SELECT * FROM bank WHERE username=?""", (str(ctx.author),))
    user_db = c.fetchone()
    if user_db:
        fish_items = user_db[4].split("`")
        fish_items.pop(-1)
        if amount == "all":
            amount = len(fish_items)
        sold_items = []
        for _ in range(amount):
            sold_item = fish_items.pop(-1)
            sold_items.append(sold_item)
        money_made = 0
        for item in sold_items:
            if "Common" in item:
                money_made += 50
            elif "Uncommon" in item:
                money_made += 100
            elif "Rare" in item:
                money_made += 150
        c.execute("""UPDATE BANK
                    SET money_in_hand=?, fishing_items=?
                    WHERE username=?""", (user_db[1] + money_made, "".join(fish_items), str(ctx.author),))
        conn.commit()
        embed = discord.Embed(title=f"Successfully sold {amount} of your fishing items!", color=0x109414)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="Error:",
                              description="You have either not setup your account, or you changed your username, to restore your money if you changed your username, please use command `bank.restore`",
                              color=0xee4f4f)
        await ctx.send(embed=embed)

@bot.command(aliases=["huntinv", "hunt_inv", "huntinventory", "hunting_inventory", "huntinginventory", "hi"])
async def hunt_inventory(ctx, *, user=None):
    if user is None:
        user = str(ctx.author)
    c.execute("""SELECT * FROM bank WHERE username=?""", (user,))
    user_db = c.fetchone()
    if user_db:
        embed = discord.Embed(title="Your hunting inventory:", color=0x109414)
        fishing_inventory = user_db[5].split("`")
        fishing_inventory.pop(-1)
        if len(fishing_inventory) == 0:
            embed = discord.Embed(title="Your hunting inventory is empty!", color=0xee4f4f)
            await ctx.send(embed=embed)
        else:
            for fishing_item in fishing_inventory:
                embed.add_field(name=fishing_item, value="What a nice item!", inline=False)
            await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="Error:",
                              description="You have either not setup your account, or you changed your username, to restore your money if you changed your username, please use command `bank.restore`",
                              color=0xee4f4f)
        await ctx.send(embed=embed)

@bot.command()
async def hunt(ctx):
    c.execute("""SELECT * FROM bank WHERE username=?""", (str(ctx.author),))
    user_db = c.fetchone()
    if user_db:
        items_you_can_catch_common = ["Common Deer:deer:", "Common Bear:bear:", "Common Elk:deer:", "Common Moose:deer:", "Common Fox:fox:", "Common Mouse:mouse:", "Common Duck:duck:"]
        items_you_can_catch_uncommon = ["Uncommon Deer:deer:", "Uncommon Bear:bear:", "Uncommon Elk:deer:", "Uncommon Moose:deer:", "Uncommon Fox:fox:", "Uncommon Mouse:mouse:", "Uncommon Duck:duck:"]
        items_you_can_catch_rare = ["Rare Deer:deer:", "Rare Bear:bear:", "Rare Elk:deer:", "Rare Moose:deer:", "Rare Fox:fox:", "Rare Mouse:mouse:", "Rare Duck:duck:"]
        number = random.randint(1, 100)
        if number < 50:
            item_you_caught = random.choice(items_you_can_catch_common)
        elif number < 75:
            item_you_caught = random.choice(items_you_can_catch_uncommon)
        else:
            item_you_caught = random.choice(items_you_can_catch_rare)
        c.execute("""UPDATE bank
                    SET hunting_items=?
                    WHERE username=?""", (user_db[4] + f"{item_you_caught}`", str(ctx.author),))
        conn.commit()
        embed = discord.Embed(title=f"You shot a(n) {item_you_caught}!", color=0x109414)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="Error:",
                              description="You have either not setup your account, or you changed your username, to restore your money if you changed your username, please use command `bank.restore`",
                              color=0xee4f4f)
        await ctx.send(embed=embed)

@bot.command(aliases=["sh", "sellhunt", "huntsell"])
async def sell_hunt(ctx, *, amount="all"):
    c.execute("""SELECT * FROM bank WHERE username=?""", (str(ctx.author),))
    user_db = c.fetchone()
    if user_db:
        fish_items = user_db[5].split("`")
        fish_items.pop(-1)
        if amount == "all":
            amount = len(fish_items)
        sold_items = []
        for _ in range(amount):
            sold_item = fish_items.pop(-1)
            sold_items.append(sold_item)
        money_made = 0
        for item in sold_items:
            if "Common" in item:
                money_made += 50
            elif "Uncommon" in item:
                money_made += 100
            elif "Rare" in item:
                money_made += 150
        c.execute("""UPDATE BANK
                    SET money_in_hand=?, hunting_items=?
                    WHERE username=?""", (user_db[1] + money_made, "".join(fish_items), str(ctx.author),))
        conn.commit()
        embed = discord.Embed(title=f"Successfully sold {amount} of your hunting items!", color=0x109414)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="Error:",
                              description="You have either not setup your account, or you changed your username, to restore your money if you changed your username, please use command `bank.restore`",
                              color=0xee4f4f)
        await ctx.send(embed=embed)

bot.run(token)

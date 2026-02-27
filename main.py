import discord
from discord.ext import commands
import random as rd
import json
import datetime
import os

from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Le bot est actif !"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()



token = os.environ['token']
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("Bot lancé")

@bot.command()
async def top(ctx):
    with open("Coins.json", "r") as f:
        data = json.load(f)
    sorted_data_values = json.dumps({k: v for k, v in sorted(data.items(), key=lambda item: item[1], reverse=True)})
    description = ""
    count = 1
    for i in sorted_data_values.replace("{", "").replace("}", "").split(",")[0:11]:
        i = i.split(":")
        user = await bot.fetch_user(int(i[0].replace('"', "")))
        description += "Top "+str(count)+" : " + str(user) + " avec " + str(i[1]) + " <:Torgcoins:1304720774753554432> " + "\n"
        count += 1
    embed = discord.Embed(
        colour=discord.Colour.dark_gold(),
        title="Voici le top 10 des joueurs avec le plus de TorgCoins",
        description=description

    )
    await ctx.send(embed=embed)

@bot.command()
async def coins(ctx, *, players=None):
    with open("Coins.json", "r") as f:
        data = json.load(f)
    playerss = ""

    for i in str(players):
        if i.isdigit():
            playerss += i
    if players==None or playerss == str(ctx.message.author.id):
        player = ctx.message.author.id
        if str(player) in data:

            await ctx.send(
                "Vous possédez " + str(data[str(player)]) + " TorgCoins <:Torgcoins:1304720774753554432>")
        else:

            data[str(player)] = 0
            with open("Coins.json", "w") as f:
                json.dump(data, f)
            await ctx.send(
                "Vous possédez " + str(data[str(player)]) + " TorgCoins <:Torgcoins:1304720774753554432>")
    else:
        player = ""
        for i in str(players):
            if i.isdigit():
                player += i


        try:
            user = await bot.fetch_user(int(player))
            if str(player) in data:

                await ctx.send("Le joueur **"+ str(user) + "** possède "+ str(data[str(player)])+ " TorgCoins <:Torgcoins:1304720774753554432>")
            else:

                data[str(player)] = 0
                with open("Coins.json", "w") as f:
                    json.dump(data, f)
                await ctx.send("Le joueur **"+ str(user) + "** possède "+ str(data[str(player)])+ " TorgCoins <:Torgcoins:1304720774753554432>")
        except:
            await ctx.send("J'ai pas trouvé ton mec ")

@bot.command()
async def free(ctx):
    with open("Cool.json", "r") as c:
        cool = json.load(c)

    if str(ctx.message.author.id) in cool and (datetime.datetime.now()-datetime.datetime.strptime(cool[str(ctx.message.author.id)], "%Y-%m-%d %H:%M:%S")).total_seconds() < 43200:

        t = str(datetime.timedelta(hours=12)-(datetime.datetime.now()-datetime.datetime.strptime(cool[str(ctx.message.author.id)], "%Y-%m-%d %H:%M:%S"))).split(".")[0].split(":")
        embed = discord.Embed(
            colour=discord.Colour.dark_grey(),
            title="Booster en cooldown",
            description= "Veuillez attendre " + t[0] + "h"+ t[1]+"min"+t[2]+"s")

        await ctx.send(embed=embed)
        return

    embed = discord.Embed(
        colour=discord.Colour.green(),
        title="Ouvrir votre Booster quotidien",
        description="Contient une carte et des TorgCoins <:Torgcoins:1304720774753554432>"
    )
    embed.set_image(url="https://media.discordapp.net/attachments/1246831135959547944/1305834347433037846/booster-pokemon-booster-noir-et-blanc-frontieres-f.png?ex=67347881&is=67332701&hm=993c4b5c80ecde9335570d9e687bfb0a348b7510e73428f96f967e0f47fbbb56&=&format=webp&quality=lossless&width=329&height=582")
    view = Daily(ctx)
    await ctx.send(embed=embed, view=view)

class SimpleView(discord.ui.View):
    def __init__(self, player, count, user):
        super().__init__()
        self.player = player
        self.count = count
        self.user = user

    @discord.ui.button(label="⬅️")
    async def move_left(self, interaction: discord.Interaction, button: discord.ui.Button):

        with open("Cards.json", "r") as f:
            data = json.load(f)

        embed = discord.Embed(
            colour=discord.Colour.dark_blue(),
            title="Collection de " + str(self.user)
        )
        if self.count <= 0:
            self.count = len(data[self.player]) -1
        else: self.count -= 1

        embed.set_image(url=urls[data[self.player][self.count]])
        embed.set_footer(text=str(self.count + 1) + "/" + str(len(data[self.player])))
        await interaction.response.edit_message(embed=embed)


    @discord.ui.button(label="➡️")
    async def move_right(self, interaction: discord.Interaction, button: discord.ui.Button):
        with open("Cards.json", "r") as f:
            data = json.load(f)

        embed = discord.Embed(
            colour=discord.Colour.dark_blue(),
            title="Collection de " + str(self.user)
        )
        if self.count >= len(data[self.player])-1:
            self.count = 0
        else:
            self.count += 1

        embed.set_image(url=urls[data[self.player][self.count]])
        embed.set_footer(text=str(self.count + 1) + "/" + str(len(data[self.player])))
        await interaction.response.edit_message(embed=embed)

class Daily(discord.ui.View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    @discord.ui.button(label="Ouvrir", style=discord.ButtonStyle.green)
    async def ouvrir(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.ctx.author:
            with open("Cool.json", "r") as c:
                cool = json.load(c)

            if str(self.ctx.message.author.id) in cool and (
                datetime.datetime.now() - datetime.datetime.strptime(cool[str(self.ctx.message.author.id)], "%Y-%m-%d %H:%M:%S")).total_seconds() < 43200 :
                t = str(datetime.timedelta(hours=12) - (datetime.datetime.now() - datetime.datetime.strptime(cool[str(self.ctx.message.author.id)], "%Y-%m-%d %H:%M:%S"))).split(".")[0].split(":")
                embed = discord.Embed(
                    colour=discord.Colour.dark_grey(),
                    title="Booster en cooldown",
                    description="Veuillez attendre " + t[0] + "h"+ t[1]+"min"+t[2]+"s")

                await interaction.response.edit_message(embed=embed, view=None)
                return
            cool[str(self.ctx.message.author.id)] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open("Cool.json", "w") as c:
                json.dump(cool, c)
            with open("Cards.json", "r") as c:
                cards = json.load(c)
            if str(self.ctx.message.author.id) not in cards:
                cards[str(self.ctx.message.author.id)] = []
            rng = rd.randint(0, 1230)
            rng2 = rd.randint(10, 100)
            with open("Coins.json", "r") as f:
                data = json.load(f)
            if str(self.ctx.message.author.id) not in data:
                data[str(self.ctx.message.author.id)] = 0
            data[str(self.ctx.message.author.id)] += rng2
            with open("Coins.json", "w") as f:
                json.dump(data, f)

            if rng < 751:


                num = rd.randint(0, len(nul) - 1)
                embed = discord.Embed(
                    colour=discord.Colour.dark_orange(),
                    title="Carte Commune (+60)",
                    description=names[nul[num]] + " a été ajouté à votre collection" + "\n+" + str(
                        rng2) + " <:Torgcoins:1304720774753554432>" + " "
                )
                url = nul[num]
                embed.set_footer(text="")
                embed.set_image(url=nul[num])

            elif rng < 1201:
                num = rd.randint(0, len(mal) - 1)
                embed = discord.Embed(
                    colour=discord.Colour.dark_grey(),
                    title="Carte Rare (+72)",
                    description=names[mal[num]] + " a été ajouté à votre collection" + "\n+" + str(
                        rng2) + " <:Torgcoins:1304720774753554432>" + " "
                )
                embed.set_footer(text="")

                url = mal[num]
                embed.set_image(url=mal[num])

            elif rng < 1219:
                num = rd.randint(0, len(good) - 1)
                embed = discord.Embed(
                    colour=discord.Colour.dark_grey(),
                    title="Carte Epique (+79)",
                    description=names[good[num]] + " a été ajouté à votre collection" + "\n+" + str(
                        rng2) + " <:Torgcoins:1304720774753554432>" + " "

                )
                embed.set_footer(text="")

                url = good[num]
                embed.set_image(url=good[num])

            elif rng < 1224:
                num = rd.randint(0, len(omg) - 1)
                embed = discord.Embed(
                    colour=discord.Colour.dark_grey(),
                    title="Carte Légendaire (+89)",
                    description=names[omg[num]] + " a été ajouté à votre collection" + "\n+" + str(
                        rng2) + " <:Torgcoins:1304720774753554432>" + " "

                )
                embed.set_footer(text="")

                url = omg[num]
                embed.set_image(url=omg[num])
            elif rng < 1230:
                num = rd.randint(0, len(leg) - 1)
                embed = discord.Embed(
                    colour=discord.Colour.dark_grey(),
                    title="Carte Spéciale (+??)",
                    description=names[leg[num]] + " a été ajouté à votre collection" + "\n+" + str(
                        rng2) + " <:Torgcoins:1304720774753554432>" + " "

                )
                embed.set_footer(text="")

                url = leg[num]
                embed.set_image(url=leg[num])



            await interaction.response.edit_message(embed=embed, view=None)
            cards[str(self.ctx.message.author.id)].append(names[url])

            with open("Cards.json", "w") as c:
                json.dump(cards, c)

class tamer3(discord.ui.View):
    def __init__(self, lis, actual):
        super().__init__()
        self.lis = lis
        self.actual = actual

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.grey)
    async def right(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.actual = self.actual - 1
        v = tamer2(self.lis, self.actual)
        await interaction.response.edit_message(embed=self.lis[self.actual], view=v)

class tamer2(discord.ui.View):
    def __init__(self, lis, actual):
        super().__init__()
        self.lis = lis
        self.actual = actual

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.grey)
    async def left(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.actual = self.actual - 1
        v = tamer1(self.lis, self.actual)
        await interaction.response.edit_message(embed=self.lis[self.actual], view=v)
    @discord.ui.button(label="➡️", style=discord.ButtonStyle.grey)
    async def right(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.actual = self.actual +1
        v = tamer3(self.lis, self.actual)
        await interaction.response.edit_message(embed=self.lis[self.actual], view=v)

class tamer1(discord.ui.View):
    def __init__(self, lis, actual):
        super().__init__()
        self.lis = lis
        self.actual = actual

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.grey)
    async def right(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.actual = self.actual + 1
        v = tamer2(self.lis, self.actual)
        await interaction.response.edit_message(embed=self.lis[self.actual], view=v)

class Booster(discord.ui.View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.actual = 0

    @discord.ui.button(label="Acheter et Ouvrir", style=discord.ButtonStyle.green)
    async def ouvrir(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.ctx.author:

            with open("Cards.json", "r") as c:
                cards = json.load(c)
            if str(self.ctx.message.author.id) not in cards:
                cards[str(self.ctx.message.author.id)] = []

            with open("Coins.json", "r") as f:
                data = json.load(f)
            if str(self.ctx.message.author.id) not in data:
                data[str(self.ctx.message.author.id)] = 0
                with open("Coins.json", "w") as f:
                    json.dump(data, f)
                embed = discord.Embed(
                    title="Pas assez d'argent",
                    description="Vous posséde 0 TorgCoins <:Torgcoins:1304720774753554432>"
                )
                await interaction.response.edit_message(embed=embed, view=None)
                return

            balance = data[str(self.ctx.message.author.id)]
            if balance >= 75:
                balance -= 75
            else:
                embed= discord.Embed(
                    title="Pas assez d'argent",
                    description="Vous ne possedez que " + str(balance) + " TorgCoins <:Torgcoins:1304720774753554432>"
                )
                await interaction.response.edit_message(embed=embed, view=None)
                return

            data[str(self.ctx.message.author.id)] = balance
            with open("Coins.json", "w") as f:
                json.dump(data, f)



            rng1 = rd.randint(0, 1781)
            rng2 = rd.randint(0, 1781)
            rng3 = rd.randint(0, 1781)

            if rng1 < 851:
                url1 = nul[rd.randint(0, len(nul) - 1)]
            elif rng1 < 1651:
                url1 = mal[rd.randint(0, len(mal) - 1)]
            elif rng1 < 1741:
                url1 = good[rd.randint(0, len(good) - 1)]
            elif rng1 < 1761:
                url1 = omg[rd.randint(0, len(omg) - 1)]
            else:
                url1 = leg[rd.randint(0, len(leg) - 1)]

            if rng2 < 851:
                url2 = nul[rd.randint(0, len(nul) - 1)]
            elif rng2 < 1651:
                url2 = mal[rd.randint(0, len(mal) - 1)]
            elif rng2 < 1741:
                url2 = good[rd.randint(0, len(good) - 1)]
            elif rng2 < 1761:
                url2 = omg[rd.randint(0, len(omg) - 1)]
            else:
                url2 = leg[rd.randint(0, len(leg) - 1)]

            if rng3 < 851:
                url3 = nul[rd.randint(0, len(nul) - 1)]
            elif rng3 < 1651:
                url3 = mal[rd.randint(0, len(mal) - 1)]
            elif rng3 < 1741:
                url3 = good[rd.randint(0, len(good) - 1)]
            elif rng3 < 1761:
                url3 = omg[rd.randint(0, len(omg) - 1)]
            else:
                url3 = leg[rd.randint(0, len(leg) - 1)]


            embed1 = discord.Embed(
                colour=discord.Colour.dark_gold(),
                title="Ouverture d'un booster",
                description=names[url1] + " a été ajouté à votre collection",

            )
            embed2 = discord.Embed(
                colour=discord.Colour.dark_gold(),
                title="Ouverture d'un booster",
                description=names[url2] + " a été ajouté à votre collection",
            )
            embed3 = discord.Embed(
                colour=discord.Colour.dark_gold(),
                title="Ouverture d'un booster",
                description=names[url3] + " a été ajouté à votre collection",
            )


            embed1.set_image(url=url1)
            embed2.set_image(url=url2)
            embed3.set_image(url=url3)

            embed1.set_footer(text="1/3")
            embed2.set_footer(text="2/3")
            embed3.set_footer(text="3/3")

            self.lis = [embed1, embed2, embed3]

            cards[str(self.ctx.message.author.id)].append(names[url1])
            cards[str(self.ctx.message.author.id)].append(names[url2])
            cards[str(self.ctx.message.author.id)].append(names[url3])

            with open("Cards.json", "w") as c:
                json.dump(cards, c)
            v = tamer1(self.lis, self.actual)
            await interaction.response.edit_message(embed=embed1, view=v)

@bot.command()
async def booster(ctx):

    embed = discord.Embed(
        colour=discord.Colour.green(),
        title="Acheter un booster à 75 TorgCoins <:Torgcoins:1304720774753554432> ?",
        description="Contient 3 cartes"
    )
    embed.set_image(url="https://media.discordapp.net/attachments/1246831135959547944/1305712288438943814/booster-pokemon-booster-noir-et-blanc-frontieres-franchies_5_2_1.png?ex=6734af94&is=67335e14&hm=c92cf710b51c3ceb38a2016cf94c8b22865f997f0b1cceb9f7a0d965c5bdf6b3&=&format=webp&quality=lossless&width=329&height=582")
    view = Booster(ctx)
    await ctx.send(embed=embed, view=view)

@bot.command()
@commands.has_role('coins manager')
async def remove(ctx, players=None, coins=None):
    if players == None:
        await ctx.send("faut ping qlq connard")

    try:
        player = ""
        for i in str(players):
            if i.isdigit():
                player += i
        user = await bot.fetch_user(int(player))

        if coins == None:
            await ctx.send("nn mais faut dire cb tu veux lui enlever ")
            return

        with open("Coins.json", "r") as f:
            data = json.load(f)
        if str(player) in data:
            data[str(player)] -= int(coins)
            with open("Coins.json", "w") as f:
                json.dump(data, f)
            await ctx.send("Le solde de la personne à été mis à jour ! ")


        else:

            data[str(player)] = int(coins)
            with open("Coins.json", "w") as f:
                json.dump(data, f)
            await ctx.send("Le solde de la personne à été mis à jour ! ")
    except:
        await ctx.send("J'ai pas trouvé ton mec ou montant à retirer invalide")

@bot.command()
@commands.has_role('coins manager')
async def add(ctx, players=None, coins=None):
    if players == None:
        await ctx.send("faut ping qlq")

    try:
        player = ""
        for i in str(players):
            if i.isdigit():
                player += i
        user = await bot.fetch_user(int(player))

        if coins == None:
            await ctx.send("nn mais faut dire cb tu veux lui enlever ( ou bien t'as pas ping enft)")
            return

        with open("Coins.json", "r") as f:
            data = json.load(f)
        if str(player) in data:
            data[str(player)] += int(coins)
            with open("Coins.json", "w") as f:
                json.dump(data, f)
            await ctx.send("Le solde de la personne à été mis à jour ! ")


        else:

            data[str(player)] = int(coins)
            with open("Coins.json", "w") as f:
                json.dump(data, f)
            await ctx.send("Le solde de la personne à été mis à jour ! ")
    except:
        await ctx.send("J'ai pas trouvé ton mec ou montant à retirer invalide")

@bot.command()
async def collection(ctx, players=None, counts=None):
    count=""
    if counts != None:
        for i in str(counts):
            if i.isdigit():
                count += i
        count = int(count) -1
    else:
        count=0
    if players == None:
        player = str(ctx.message.author.id)
    else:
        player = ""
        for i in str(players):
            if i.isdigit():
                player += i
        if len(player) != 18:
            count = int(player)



            try:

                user = await bot.fetch_user(int(ctx.message.author.id))
                embed = discord.Embed(
                    colour=discord.Colour.dark_blue(),
                    title="Collection de " + str(user),

                    )
                with open("Cards.json", "r") as f:
                    data = json.load(f)
                if count < 0:
                    count = len(data[player]) - 1
                if count >= len(data[player]):
                    count = 0

                embed.set_image(url=urls[data[player][count]])
                embed.set_footer(text=str(count+1)+"/"+str(len(data[player])))

                view = SimpleView(player, count, user)


                await ctx.send(embed=embed, view=view)

            except:
                await ctx.send("Collection vide ou index fourni invalide")

    try:

        user = await bot.fetch_user(int(player))
        if user == None:
            await ctx.send("Bof j'ai pas trouvé ton mec")
            return
        embed = discord.Embed(
            colour=discord.Colour.dark_blue(),
            title="Collection de " + str(user),

        )
        with open("Cards.json", "r") as f:
            data = json.load(f)
        if count < 0:
            count = len(data[player]) - 1
        if count >= len(data[player]):
            count = 0

        embed.set_image(url=urls[data[player][count]])
        embed.set_footer(text=str(count + 1) + "/" + str(len(data[player])))

        view = SimpleView(player, count, user)

        await ctx.send(embed=embed, view=view)

    except:
        await ctx.send("Collection vide ou index fourni invalide")
urls = {"BlackLolo":"https://media.discordapp.net/attachments/1246831135959547944/1305642407303319642/5_BlackLolo.png?ex=67346e7f&is=67331cff&hm=d828c8853d2e28c16018ce09a6e5dd6bcf484db85ad2d4a46324d51583fe1d34&=&format=webp&quality=lossless&width=416&height=582",
    "Totay":"https://media.discordapp.net/attachments/1246831135959547944/1305642407806631956/13_Totay.png?ex=67346e7f&is=67331cff&hm=dafdd7cd49a5b9ddccf50a4f5272450636993a8713bfa865c742207f99394ee8&=&format=webp&quality=lossless&width=416&height=582",
    "Chapi":"https://media.discordapp.net/attachments/1246831135959547944/1305642408301563904/3_Chapi.png?ex=67346e7f&is=67331cff&hm=d4992e79ff50640789c0750cdcabf8d288abdb94f72596233d400d2af9688c7f&=&format=webp&quality=lossless&width=416&height=582",
    "MrGwak":"https://media.discordapp.net/attachments/1246831135959547944/1305642408821788742/16_MrGwak.png?ex=67346e7f&is=67331cff&hm=cb86f1efa430d52b90190b5d49aa6838bb77c4775bce19a721d243539bffe2fc&=&format=webp&quality=lossless&width=416&height=582",
    "Kenzo":"https://media.discordapp.net/attachments/1246831135959547944/1305642409446609037/21_Kenzo.png?ex=67346e80&is=67331d00&hm=6b0c8250410c925f5e16b78461998e5bf4e5017d8203dfba074a6d3654486ef0&=&format=webp&quality=lossless&width=416&height=582",
    "Layte":"https://media.discordapp.net/attachments/1246831135959547944/1305642410230939648/26_Layte.png?ex=67346e80&is=67331d00&hm=3728fa1df6b8de7698d4a5004aafca076a788dec8de04d1197589a5e7b94f4c1&=&format=webp&quality=lossless&width=416&height=582",
    "Cramptox":"https://media.discordapp.net/attachments/1246831135959547944/1305642410755493948/27_Cramptox.png?ex=67346e80&is=67331d00&hm=6220a8b7007cc3cc87625b4625dd234e18dc542ab07790e100d131e9fdb88eb0&=&format=webp&quality=lossless&width=416&height=582",
    "Yoddle":"https://media.discordapp.net/attachments/1246831135959547944/1305642411245961356/28_Yoddle.png?ex=67346e80&is=67331d00&hm=40009331b3818114b7066e5c98503219b9bcbd293be7b485f181bac6415f4f33&=&format=webp&quality=lossless&width=416&height=582",
    "Cha":"https://media.discordapp.net/attachments/1246831135959547944/1305642411690561606/29_Cha.png?ex=67346e80&is=67331d00&hm=c59c36554848b980849a3eb8134d562529e8bbc4faa91c46673a6fa58db6a7f9&=&format=webp&quality=lossless&width=416&height=582",
    "Scan":"https://media.discordapp.net/attachments/1246831135959547944/1305642412206456913/31_Scan.png?ex=67346e80&is=67331d00&hm=dcfd5f932aa6d60b295cba5247bd3409210c3fcdd2627d832addf3f69fa79555&=&format=webp&quality=lossless&width=416&height=582",
    "Black":"https://media.discordapp.net/attachments/1246831135959547944/1305642494163288205/33_Black.png?ex=67346e94&is=67331d14&hm=155c54654feb659b765c5be89b040d99847a700948b7feedf433b2c8c6991f87&=&format=webp&quality=lossless&width=416&height=582",
    "Natsu":"https://media.discordapp.net/attachments/1246831135959547944/1305642494708678776/34_Natsu.png?ex=67346e94&is=67331d14&hm=e2d67cdf35282dbf830d84ebe94aec08483f9dfba09a570aa9a30ec77d4e3afc&=&format=webp&quality=lossless&width=416&height=582",
    "Saltay":"https://media.discordapp.net/attachments/1246831135959547944/1305642495329177660/35_Saltay.png?ex=67346e94&is=67331d14&hm=e631e82b2074c78e02737ee7fb0a78b261e4c1c0918c3c1fa96b0bd763e41f57&=&format=webp&quality=lossless&width=416&height=582",
    "TMH":"https://media.discordapp.net/attachments/1246831135959547944/1305642496004587571/36_TMH.png?ex=67346e94&is=67331d14&hm=99ceb011d82544aeba05a97f2600e9efb975c3045b4cd8640ef2f3c603636245&=&format=webp&quality=lossless&width=416&height=582",
    "Xiao":"https://media.discordapp.net/attachments/1246831135959547944/1305642496608702474/39_Xiao.png?ex=67346e94&is=67331d14&hm=5c3787bc3bff1f074a8ef887b3edb233b168ef123f5daa4e2ba3a8d3f4ef2517&=&format=webp&quality=lossless&width=416&height=582",
    "Dabi":"https://media.discordapp.net/attachments/1246831135959547944/1305642497174802452/43_Dabi.png?ex=67346e94&is=67331d14&hm=808d010798a52c3d3372c17ef07e87c6b6fd5844dd8f23a782ce2e99771cadb0&=&format=webp&quality=lossless&width=416&height=582",
    "Apollo":"https://media.discordapp.net/attachments/1246831135959547944/1305642497820852224/45_Apollo.png?ex=67346e95&is=67331d15&hm=26798b3ec0fd831e8af7869166ce829dc8b3eb44f0e169123747fd9e6804f816&=&format=webp&quality=lossless&width=416&height=582",
    "TreekoZ":"https://media.discordapp.net/attachments/1246831135959547944/1305642575897559061/48_TreekoZ.png?ex=67346ea7&is=67331d27&hm=aafbf2d2da23db9ae4b9edf89d3f2d25567985a3f846c05058eb6eef59bf9c84&=&format=webp&quality=lossless&width=416&height=582",
    "Sensei":"https://media.discordapp.net/attachments/1246831135959547944/1305642576417787945/49_Sensei.png?ex=67346ea7&is=67331d27&hm=85909d328fb3e6a48e44f9acac20bf0c49f492677562e03d39cf18a91269f8c8&=&format=webp&quality=lossless&width=416&height=582",
    "Kchouuu":"https://media.discordapp.net/attachments/1246831135959547944/1305642577906896906/50_Kchouuu.png?ex=67346ea8&is=67331d28&hm=4d38255a44463b3f57594dee14bc550c5c42f5c8fb62f99e44b95bc72742c624&=&format=webp&quality=lossless&width=416&height=582",
    "Luigi":"https://media.discordapp.net/attachments/1246831135959547944/1305642037705441370/4_Luigi.png?ex=67346e27&is=67331ca7&hm=8476b197d73787f8dbccad6f8346d2025a60d57cdd87b0287fe886fc8c98e69f&=&format=webp&quality=lossless&width=416&height=582",
    "Herope":"https://media.discordapp.net/attachments/1246831135959547944/1305642038179532960/6_Herope.png?ex=67346e27&is=67331ca7&hm=4824e1d94474dd2e49aa80eaf4ee28f706fc2043f2eb4f21196c2ff046212a65&=&format=webp&quality=lossless&width=416&height=582",
    "Nono":"https://media.discordapp.net/attachments/1246831135959547944/1305642038955348008/7_Nono.png?ex=67346e27&is=67331ca7&hm=f9f8f1b7327d9bb9d06782a89a9adb6eedeb2d78a4bf3518491576eb84a54399&=&format=webp&quality=lossless&width=416&height=582",
    "Sander":"https://media.discordapp.net/attachments/1246831135959547944/1305642039475437578/8_Sander.png?ex=67346e27&is=67331ca7&hm=e76593c44dc0357ec2fe9157ffdac399461bb229ed051ce9887b521995969368&=&format=webp&quality=lossless&width=416&height=582",
    "Raph":"https://media.discordapp.net/attachments/1246831135959547944/1305642040104718437/10_Raph.png?ex=67346e28&is=67331ca8&hm=e2c6af2530d97ce8902505c2497e967aeb7718a9ea4d44bebbd01098b80a65e0&=&format=webp&quality=lossless&width=416&height=582",
    "Nekoss":"https://media.discordapp.net/attachments/1246831135959547944/1305642040607903864/17_Nekoss.png?ex=67346e28&is=67331ca8&hm=dc724eaf2e626abef64bf7a8aa039f51f7d35b73a5940fb04392a361ff12c9f8&=&format=webp&quality=lossless&width=416&height=582",
    "Heros":"https://media.discordapp.net/attachments/1246831135959547944/1305642041094438973/19_Heros.png?ex=67346e28&is=67331ca8&hm=c74e82cf8ed47eaed0c445cee91207d8bdfab4223430f1e8ba874d9f7b2fcab2&=&format=webp&quality=lossless&width=416&height=582",
    "Regis":"https://media.discordapp.net/attachments/1246831135959547944/1305642041547558983/20_Regis.png?ex=67346e28&is=67331ca8&hm=490c851f2efd5371381a3896a06a00b0232538fbce0c42bfcb45277fb9a8c832&=&format=webp&quality=lossless&width=416&height=582",
    "Alan":"https://media.discordapp.net/attachments/1246831135959547944/1305642041966858341/24_Alan.png?ex=67346e28&is=67331ca8&hm=efbbe7da48f098f5796db93ccdb555ad3d3fa6adb9c6110a4a8573b303660441&=&format=webp&quality=lossless&width=416&height=582",
    "Ener":"https://media.discordapp.net/attachments/1246831135959547944/1305642117749801011/25_Ener.png?ex=67346e3a&is=67331cba&hm=62c6da7d1a286add66d77fc97208b685e3c25b0f8e4d306be70291626670ba84&=&format=webp&quality=lossless&width=416&height=582",
    "Hiroo":"https://media.discordapp.net/attachments/1246831135959547944/1305642118433476718/40_Hiroo.png?ex=67346e3a&is=67331cba&hm=a68aab238ea9e5ee7a21d096232309e464b464292249a2a03a28699c064df4f2&=&format=webp&quality=lossless&width=416&height=582",
    "Loni":"https://media.discordapp.net/attachments/1246831135959547944/1305642119129469049/41_Loni.png?ex=67346e3a&is=67331cba&hm=582f8ccebbc4a4c81bb37011718df7039c992d89313173fb29bbc31f30134915&=&format=webp&quality=lossless&width=416&height=582",
    "Guillem":"https://media.discordapp.net/attachments/1246831135959547944/1305642119720997027/44_Guillem.png?ex=67346e3a&is=67331cba&hm=eff647e478d06c21b105e4bede090942ecedbaebfbdf6ede07e8495a73828bde&=&format=webp&quality=lossless&width=416&height=582",
    "Nicovid":"https://media.discordapp.net/attachments/1246831135959547944/1305642120417382440/47_Nicovid.png?ex=67346e3b&is=67331cbb&hm=8b71512fa63880df5bfa7bdbb6920768a855510adfb49f054c463564c9bf836d&=&format=webp&quality=lossless&width=416&height=582",
    "Polo":"https://media.discordapp.net/attachments/1246831135959547944/1305642121008644187/51_Polo.png?ex=67346e3b&is=67331cbb&hm=ae6413e2fb5f1568b5518f575e77b3a3232e204b575044dd4cb2368b918ff0aa&=&format=webp&quality=lossless&width=416&height=582",
    "Redman":"https://media.discordapp.net/attachments/1246831135959547944/1305641710923026492/22_Redman.png?ex=67346dd9&is=67331c59&hm=f7ea55a6e09b970b82a979baf37bb883e83f1791e1d0b77286833a732ab17760&=&format=webp&quality=lossless&width=416&height=582",
    "GB1":"https://media.discordapp.net/attachments/1246831135959547944/1305641711493714020/37_GB1.png?ex=67346dd9&is=67331c59&hm=7d7d689eb5f47e8e31a4b952823a046f659087cca9dda7f1d8784f9bffcd596c&=&format=webp&quality=lossless&width=416&height=582",
    "Grenzo":"https://media.discordapp.net/attachments/1246831135959547944/1305641711984316446/1_Grenzo.png?ex=67346dd9&is=67331c59&hm=884341c00da3a3a7cb85a94621c53f40d7074101ec3b41a1c26e7ae0cf438444&=&format=webp&quality=lossless&width=416&height=582",
    "Thyx":"https://media.discordapp.net/attachments/1246831135959547944/1305641712785293403/2_Thyx.png?ex=67346dd9&is=67331c59&hm=796085776f282f065355ec2ced38a0b808eb82077adcb329502f5695d247c10e&=&format=webp&quality=lossless&width=416&height=582",
    "Saamito":"https://media.discordapp.net/attachments/1246831135959547944/1305641713330688040/9_Saamito.png?ex=67346dda&is=67331c5a&hm=61ee3a7463bd1bb5e4240082bd5d774d03a4a3cb44d317ae8a6fc58b295db682&=&format=webp&quality=lossless&width=416&height=582",
    "ChoKo":"https://media.discordapp.net/attachments/1246831135959547944/1305641714056433744/14_ChoKo.png?ex=67346dda&is=67331c5a&hm=746e5bd43d71e6b8069a34b3d664f3bc765a02169424932d39b8343994e35e60&=&format=webp&quality=lossless&width=416&height=582",
    "QV":"https://media.discordapp.net/attachments/1246831135959547944/1305641714815471687/15_QV.png?ex=67346dda&is=67331c5a&hm=c57033f5d38c92e1de820d93a67e0d6c368f576f9d3449bab54bbdf2c41270c9&=&format=webp&quality=lossless&width=416&height=582",
    "Aless":"https://media.discordapp.net/attachments/1246831135959547944/1305641715293753385/11_Aless.png?ex=67346dda&is=67331c5a&hm=73b05328018b13525f62c3a6078684a4843dc0eeaa21a4dad795bbf8d22bcbbc&=&format=webp&quality=lossless&width=416&height=582",
    "Skuter":"https://media.discordapp.net/attachments/1246831135959547944/1305641715926958130/42_Skuter.png?ex=67346dda&is=67331c5a&hm=79b548174873b3910dcb45d1e90efc0d1d0df6bb72227dc557e18b10b1cb70c2&=&format=webp&quality=lossless&width=416&height=582",
    "Amaury":"https://media.discordapp.net/attachments/1246831135959547944/1305641716463964230/46_Amaury.png?ex=67346dda&is=67331c5a&hm=a8b81cfd9dfac67233691b69429bfba3660f8e3ca21c6a6de7eb324bd84398c3&=&format=webp&quality=lossless&width=416&height=582",
    "Watson":"https://media.discordapp.net/attachments/1246831135959547944/1305896292190257253/38_Watson.png?ex=6734b232&is=673360b2&hm=b71d80a31c989de8d692a7956479e1c1d52d1176e066cd8e85f2f60eff04d052&=&format=webp&quality=lossless&width=416&height=582",
    "ByDyVix":"https://media.discordapp.net/attachments/1246831135959547944/1305641781936914594/18_ByDyVix.png?ex=67346dea&is=67331c6a&hm=f0551e4c3dcc5ebb00e443ac01487a0ed39d4fe05762927d879393040d9a94e1&=&format=webp&quality=lossless&width=416&height=582",
    "Alnwick":"https://media.discordapp.net/attachments/1246831135959547944/1305641227940790312/30_Alnwick.png?ex=67346d66&is=67331be6&hm=d0699b6b82e3804c991ff92971aca81af085aedb836285e4f965f3ab6e4ca12f&=&format=webp&quality=lossless&width=416&height=582",
    "Amin":"https://media.discordapp.net/attachments/1246831135959547944/1305641228796297216/12_Amin.png?ex=67346d66&is=67331be6&hm=8bad4732133447ef7289ea4d6cb6ff829b782defcb3a24ac8b139e625b42bdf6&=&format=webp&quality=lossless&width=416&height=582",
    "Yatho":"https://media.discordapp.net/attachments/1246831135959547944/1305641229538820197/23_Yatho.png?ex=67346d66&is=67331be6&hm=69fac93ca8214de1696316aa92f0b979776d1001d7948911bd39617dde03b5f0&=&format=webp&quality=lossless&width=416&height=582",
    "Gnagna":"https://media.discordapp.net/attachments/1246831135959547944/1305641230415302697/32_Gnagna.png?ex=67346d66&is=67331be6&hm=c74c80ad4951cab63113d605cbebf6066c201ff8338d16035b98dd4375ffa3ef&=&format=webp&quality=lossless&width=416&height=582",
    "Totay spécial":"https://media.discordapp.net/attachments/1246831135959547944/1305641341199585442/65_Totay.png?ex=67346d81&is=67331c01&hm=2f2eca3da6a431fb833dd49037f6d82544ae2a94846912767bd8e7a087a55b25&=&format=webp&quality=lossless&width=416&height=582",
    "Thyx spécial":"https://media.discordapp.net/attachments/1246831135959547944/1305641341803430009/68_Thyx.png?ex=67346d81&is=67331c01&hm=cab0f3021cc730fe7422536559da47bcdeff6af624a9a99fd91469a27c3db071&=&format=webp&quality=lossless&width=416&height=582",
    "QV spécial":"https://media.discordapp.net/attachments/1246831135959547944/1305641342466261092/64_QV.png?ex=67346d81&is=67331c01&hm=cd05074fe609b69a52937e4038fa81569c4654e9549b77b7448b2c46a22db96e&=&format=webp&quality=lossless&width=416&height=582",
    "Yatho spécial":"https://media.discordapp.net/attachments/1246831135959547944/1305641343355457597/66_Yatho.png?ex=67346d81&is=67331c01&hm=7906b433af4bb5d04001ad9081e760ad6e969508c09b7bac86195d27e4de021d&=&format=webp&quality=lossless&width=416&height=582",
    "Gnagna spécial":"https://media.discordapp.net/attachments/1246831135959547944/1305641344085135472/67_Gnagna.png?ex=67346d82&is=67331c02&hm=7c8cc8ccf959080e07e44582875b7159e6f190a606bdb1dfd681e5618bb9062c&=&format=webp&quality=lossless&width=416&height=582",
    "Watson spécial":"https://media.discordapp.net/attachments/1246831135959547944/1305899140055826432/72_Watson.png?ex=6734b4d9&is=67336359&hm=f3fd92cabc1aba3346a024d91d92ef4122ba70ceed7bf1e0703efc931253147d&=&format=webp&quality=lossless&width=416&height=582",
    "Black spécial (il fout quoi là lui mm)":"https://media.discordapp.net/attachments/1246831135959547944/1305899140860874913/69_Black.png?ex=6734b4d9&is=67336359&hm=eba7cbdf585b02bce86a9f01fdfb1767bc0308a0d6a10e717185c0f1256d708c&=&format=webp&quality=lossless&width=416&height=582",
    "Apollo spécial":"https://media.discordapp.net/attachments/1246831135959547944/1305899141607718922/70_Apollo.png?ex=6734b4d9&is=67336359&hm=54ce4244f1f5ab3aa2923192eebd4a35e7285f203d2d9eeee6f6c38a84d0599d&=&format=webp&quality=lossless&width=416&height=582",
    "ByDyVix spécial":"https://media.discordapp.net/attachments/1246831135959547944/1305899142274351154/71_ByDyVix.png?ex=6734b4d9&is=67336359&hm=55f91bd7265b94dbf659c0887ac7f5fc1d8c73ff6cf228f45299ffbc01c323d7&=&format=webp&quality=lossless&width=416&height=582"
           ,
        "Lettonie":"https://media.discordapp.net/attachments/1304268220089499693/1305958411493576715/carte_torg_save_9.png?ex=6734ec0c&is=67339a8c&hm=4186870f3d0993c6fee0c47041e80a927677427d1f574c2cf4a8de3bf1ee6238&=&format=webp&quality=lossless&width=224&height=314",
       "Luxembourg":"https://media.discordapp.net/attachments/1304268220089499693/1305956966866354267/61_Luxembourg.png?ex=6734eab4&is=67339934&hm=c0e66976bd889ed457b87944f7c2a8b2136f8f83c4140cd960fa3134f22f3bc6&=&format=webp&quality=lossless&width=224&height=314",
       "Uruguay":"https://media.discordapp.net/attachments/1304268220089499693/1305955894789406780/60_Uruguay.png?ex=6734e9b4&is=67339834&hm=39fcbf4dcfcc6e8aa06c8baca511891cbabbf4ac67ccef90961dfcb68d1c9709&=&format=webp&quality=lossless&width=224&height=314",
       "Guinee":"https://media.discordapp.net/attachments/1304268220089499693/1305954745080610846/59_Guinee.png?ex=6734e8a2&is=67339722&hm=29eddc277f7164e051374f23cc2a01e1035fd4fafd04a062c90cdce69bbbfdd4&=&format=webp&quality=lossless&width=224&height=314",
       "Islande":"https://media.discordapp.net/attachments/1304268220089499693/1305953959210651679/63_Islande.png?ex=6734e7e7&is=67339667&hm=fb8f57856bc3f5fe89919de7d4920e4cda87ed0423f442a0eb8dd1504dafcdd8&=&format=webp&quality=lossless&width=224&height=314",
       "Algerie":"https://media.discordapp.net/attachments/1304268220089499693/1305953947910930472/53_Algerie.png?ex=6734e7e4&is=67339664&hm=3c8857038264f9e9435391660f9bf88a1b88190ccdfb732506abf9209a4b63c0&=&format=webp&quality=lossless&width=416&height=582",
       "France":"https://media.discordapp.net/attachments/1304268220089499693/1305953948284489839/54_France.png?ex=6734e7e4&is=67339664&hm=3b88d91f7889fda7c9fdd116359d2357a135d97c44684229b8141dfb5b506a09&=&format=webp&quality=lossless&width=416&height=582",
       "Japon":"https://media.discordapp.net/attachments/1304268220089499693/1305953948678750279/55_Japon.png?ex=6734e7e4&is=67339664&hm=10a5978ad17ce8279db2c1ca95baa4ce4afa4daff3fe33b35e6d60ed2b496b6e&=&format=webp&quality=lossless&width=416&height=582",
       "Georgie":"https://media.discordapp.net/attachments/1304268220089499693/1305953946585530399/57_Georgie.png?ex=6734e7e4&is=67339664&hm=071e173770df0297ccd4d662b0acc39835ef4e0131a39081e11df539fdbaff3e&=&format=webp&quality=lossless&width=416&height=582",
       "Espagne":"https://media.discordapp.net/attachments/1304268220089499693/1305953947001032724/58_Espagne.png?ex=6734e7e4&is=67339664&hm=7d93896edfafbb830d68d95cf7e023db93b67ac43629dc484628b58dedcc26a9&=&format=webp&quality=lossless&width=416&height=582",
       "Bresil":"https://media.discordapp.net/attachments/1304268220089499693/1305953947449819147/52_Bresil.png?ex=6734e7e4&is=67339664&hm=4990a8867568ff053b695dbf74880514b7218c7866ab49636597d522d04bdc27&=&format=webp&quality=lossless&width=416&height=582"

}



names = {'https://media.discordapp.net/attachments/1246831135959547944/1305642407303319642/5_BlackLolo.png?ex=67346e7f&is=67331cff&hm=d828c8853d2e28c16018ce09a6e5dd6bcf484db85ad2d4a46324d51583fe1d34&=&format=webp&quality=lossless&width=416&height=582': 'BlackLolo', 'https://media.discordapp.net/attachments/1246831135959547944/1305642407806631956/13_Totay.png?ex=67346e7f&is=67331cff&hm=dafdd7cd49a5b9ddccf50a4f5272450636993a8713bfa865c742207f99394ee8&=&format=webp&quality=lossless&width=416&height=582': 'Totay', 'https://media.discordapp.net/attachments/1246831135959547944/1305642408301563904/3_Chapi.png?ex=67346e7f&is=67331cff&hm=d4992e79ff50640789c0750cdcabf8d288abdb94f72596233d400d2af9688c7f&=&format=webp&quality=lossless&width=416&height=582': 'Chapi', 'https://media.discordapp.net/attachments/1246831135959547944/1305642408821788742/16_MrGwak.png?ex=67346e7f&is=67331cff&hm=cb86f1efa430d52b90190b5d49aa6838bb77c4775bce19a721d243539bffe2fc&=&format=webp&quality=lossless&width=416&height=582': 'MrGwak', 'https://media.discordapp.net/attachments/1246831135959547944/1305642409446609037/21_Kenzo.png?ex=67346e80&is=67331d00&hm=6b0c8250410c925f5e16b78461998e5bf4e5017d8203dfba074a6d3654486ef0&=&format=webp&quality=lossless&width=416&height=582': 'Kenzo', 'https://media.discordapp.net/attachments/1246831135959547944/1305642410230939648/26_Layte.png?ex=67346e80&is=67331d00&hm=3728fa1df6b8de7698d4a5004aafca076a788dec8de04d1197589a5e7b94f4c1&=&format=webp&quality=lossless&width=416&height=582': 'Layte', 'https://media.discordapp.net/attachments/1246831135959547944/1305642410755493948/27_Cramptox.png?ex=67346e80&is=67331d00&hm=6220a8b7007cc3cc87625b4625dd234e18dc542ab07790e100d131e9fdb88eb0&=&format=webp&quality=lossless&width=416&height=582': 'Cramptox', 'https://media.discordapp.net/attachments/1246831135959547944/1305642411245961356/28_Yoddle.png?ex=67346e80&is=67331d00&hm=40009331b3818114b7066e5c98503219b9bcbd293be7b485f181bac6415f4f33&=&format=webp&quality=lossless&width=416&height=582': 'Yoddle', 'https://media.discordapp.net/attachments/1246831135959547944/1305642411690561606/29_Cha.png?ex=67346e80&is=67331d00&hm=c59c36554848b980849a3eb8134d562529e8bbc4faa91c46673a6fa58db6a7f9&=&format=webp&quality=lossless&width=416&height=582': 'Cha', 'https://media.discordapp.net/attachments/1246831135959547944/1305642412206456913/31_Scan.png?ex=67346e80&is=67331d00&hm=dcfd5f932aa6d60b295cba5247bd3409210c3fcdd2627d832addf3f69fa79555&=&format=webp&quality=lossless&width=416&height=582': 'Scan', 'https://media.discordapp.net/attachments/1246831135959547944/1305642494163288205/33_Black.png?ex=67346e94&is=67331d14&hm=155c54654feb659b765c5be89b040d99847a700948b7feedf433b2c8c6991f87&=&format=webp&quality=lossless&width=416&height=582': 'Black', 'https://media.discordapp.net/attachments/1246831135959547944/1305642494708678776/34_Natsu.png?ex=67346e94&is=67331d14&hm=e2d67cdf35282dbf830d84ebe94aec08483f9dfba09a570aa9a30ec77d4e3afc&=&format=webp&quality=lossless&width=416&height=582': 'Natsu', 'https://media.discordapp.net/attachments/1246831135959547944/1305642495329177660/35_Saltay.png?ex=67346e94&is=67331d14&hm=e631e82b2074c78e02737ee7fb0a78b261e4c1c0918c3c1fa96b0bd763e41f57&=&format=webp&quality=lossless&width=416&height=582': 'Saltay', 'https://media.discordapp.net/attachments/1246831135959547944/1305642496004587571/36_TMH.png?ex=67346e94&is=67331d14&hm=99ceb011d82544aeba05a97f2600e9efb975c3045b4cd8640ef2f3c603636245&=&format=webp&quality=lossless&width=416&height=582': 'TMH', 'https://media.discordapp.net/attachments/1246831135959547944/1305642496608702474/39_Xiao.png?ex=67346e94&is=67331d14&hm=5c3787bc3bff1f074a8ef887b3edb233b168ef123f5daa4e2ba3a8d3f4ef2517&=&format=webp&quality=lossless&width=416&height=582': 'Xiao', 'https://media.discordapp.net/attachments/1246831135959547944/1305642497174802452/43_Dabi.png?ex=67346e94&is=67331d14&hm=808d010798a52c3d3372c17ef07e87c6b6fd5844dd8f23a782ce2e99771cadb0&=&format=webp&quality=lossless&width=416&height=582': 'Dabi', 'https://media.discordapp.net/attachments/1246831135959547944/1305642497820852224/45_Apollo.png?ex=67346e95&is=67331d15&hm=26798b3ec0fd831e8af7869166ce829dc8b3eb44f0e169123747fd9e6804f816&=&format=webp&quality=lossless&width=416&height=582': 'Apollo', 'https://media.discordapp.net/attachments/1246831135959547944/1305642575897559061/48_TreekoZ.png?ex=67346ea7&is=67331d27&hm=aafbf2d2da23db9ae4b9edf89d3f2d25567985a3f846c05058eb6eef59bf9c84&=&format=webp&quality=lossless&width=416&height=582': 'TreekoZ', 'https://media.discordapp.net/attachments/1246831135959547944/1305642576417787945/49_Sensei.png?ex=67346ea7&is=67331d27&hm=85909d328fb3e6a48e44f9acac20bf0c49f492677562e03d39cf18a91269f8c8&=&format=webp&quality=lossless&width=416&height=582': 'Sensei', 'https://media.discordapp.net/attachments/1246831135959547944/1305642577906896906/50_Kchouuu.png?ex=67346ea8&is=67331d28&hm=4d38255a44463b3f57594dee14bc550c5c42f5c8fb62f99e44b95bc72742c624&=&format=webp&quality=lossless&width=416&height=582': 'Kchouuu', 'https://media.discordapp.net/attachments/1246831135959547944/1305642037705441370/4_Luigi.png?ex=67346e27&is=67331ca7&hm=8476b197d73787f8dbccad6f8346d2025a60d57cdd87b0287fe886fc8c98e69f&=&format=webp&quality=lossless&width=416&height=582': 'Luigi', 'https://media.discordapp.net/attachments/1246831135959547944/1305642038179532960/6_Herope.png?ex=67346e27&is=67331ca7&hm=4824e1d94474dd2e49aa80eaf4ee28f706fc2043f2eb4f21196c2ff046212a65&=&format=webp&quality=lossless&width=416&height=582': 'Herope', 'https://media.discordapp.net/attachments/1246831135959547944/1305642038955348008/7_Nono.png?ex=67346e27&is=67331ca7&hm=f9f8f1b7327d9bb9d06782a89a9adb6eedeb2d78a4bf3518491576eb84a54399&=&format=webp&quality=lossless&width=416&height=582': 'Nono', 'https://media.discordapp.net/attachments/1246831135959547944/1305642039475437578/8_Sander.png?ex=67346e27&is=67331ca7&hm=e76593c44dc0357ec2fe9157ffdac399461bb229ed051ce9887b521995969368&=&format=webp&quality=lossless&width=416&height=582': 'Sander', 'https://media.discordapp.net/attachments/1246831135959547944/1305642040104718437/10_Raph.png?ex=67346e28&is=67331ca8&hm=e2c6af2530d97ce8902505c2497e967aeb7718a9ea4d44bebbd01098b80a65e0&=&format=webp&quality=lossless&width=416&height=582': 'Raph', 'https://media.discordapp.net/attachments/1246831135959547944/1305642040607903864/17_Nekoss.png?ex=67346e28&is=67331ca8&hm=dc724eaf2e626abef64bf7a8aa039f51f7d35b73a5940fb04392a361ff12c9f8&=&format=webp&quality=lossless&width=416&height=582': 'Nekoss', 'https://media.discordapp.net/attachments/1246831135959547944/1305642041094438973/19_Heros.png?ex=67346e28&is=67331ca8&hm=c74e82cf8ed47eaed0c445cee91207d8bdfab4223430f1e8ba874d9f7b2fcab2&=&format=webp&quality=lossless&width=416&height=582': 'Heros', 'https://media.discordapp.net/attachments/1246831135959547944/1305642041547558983/20_Regis.png?ex=67346e28&is=67331ca8&hm=490c851f2efd5371381a3896a06a00b0232538fbce0c42bfcb45277fb9a8c832&=&format=webp&quality=lossless&width=416&height=582': 'Regis', 'https://media.discordapp.net/attachments/1246831135959547944/1305642041966858341/24_Alan.png?ex=67346e28&is=67331ca8&hm=efbbe7da48f098f5796db93ccdb555ad3d3fa6adb9c6110a4a8573b303660441&=&format=webp&quality=lossless&width=416&height=582': 'Alan', 'https://media.discordapp.net/attachments/1246831135959547944/1305642117749801011/25_Ener.png?ex=67346e3a&is=67331cba&hm=62c6da7d1a286add66d77fc97208b685e3c25b0f8e4d306be70291626670ba84&=&format=webp&quality=lossless&width=416&height=582': 'Ener', 'https://media.discordapp.net/attachments/1246831135959547944/1305642118433476718/40_Hiroo.png?ex=67346e3a&is=67331cba&hm=a68aab238ea9e5ee7a21d096232309e464b464292249a2a03a28699c064df4f2&=&format=webp&quality=lossless&width=416&height=582': 'Hiroo', 'https://media.discordapp.net/attachments/1246831135959547944/1305642119129469049/41_Loni.png?ex=67346e3a&is=67331cba&hm=582f8ccebbc4a4c81bb37011718df7039c992d89313173fb29bbc31f30134915&=&format=webp&quality=lossless&width=416&height=582': 'Loni', 'https://media.discordapp.net/attachments/1246831135959547944/1305642119720997027/44_Guillem.png?ex=67346e3a&is=67331cba&hm=eff647e478d06c21b105e4bede090942ecedbaebfbdf6ede07e8495a73828bde&=&format=webp&quality=lossless&width=416&height=582': 'Guillem', 'https://media.discordapp.net/attachments/1246831135959547944/1305642120417382440/47_Nicovid.png?ex=67346e3b&is=67331cbb&hm=8b71512fa63880df5bfa7bdbb6920768a855510adfb49f054c463564c9bf836d&=&format=webp&quality=lossless&width=416&height=582': 'Nicovid', 'https://media.discordapp.net/attachments/1246831135959547944/1305642121008644187/51_Polo.png?ex=67346e3b&is=67331cbb&hm=ae6413e2fb5f1568b5518f575e77b3a3232e204b575044dd4cb2368b918ff0aa&=&format=webp&quality=lossless&width=416&height=582': 'Polo', 'https://media.discordapp.net/attachments/1246831135959547944/1305641710923026492/22_Redman.png?ex=67346dd9&is=67331c59&hm=f7ea55a6e09b970b82a979baf37bb883e83f1791e1d0b77286833a732ab17760&=&format=webp&quality=lossless&width=416&height=582': 'Redman', 'https://media.discordapp.net/attachments/1246831135959547944/1305641711493714020/37_GB1.png?ex=67346dd9&is=67331c59&hm=7d7d689eb5f47e8e31a4b952823a046f659087cca9dda7f1d8784f9bffcd596c&=&format=webp&quality=lossless&width=416&height=582': 'GB1', 'https://media.discordapp.net/attachments/1246831135959547944/1305641711984316446/1_Grenzo.png?ex=67346dd9&is=67331c59&hm=884341c00da3a3a7cb85a94621c53f40d7074101ec3b41a1c26e7ae0cf438444&=&format=webp&quality=lossless&width=416&height=582': 'Grenzo', 'https://media.discordapp.net/attachments/1246831135959547944/1305641712785293403/2_Thyx.png?ex=67346dd9&is=67331c59&hm=796085776f282f065355ec2ced38a0b808eb82077adcb329502f5695d247c10e&=&format=webp&quality=lossless&width=416&height=582': 'Thyx', 'https://media.discordapp.net/attachments/1246831135959547944/1305641713330688040/9_Saamito.png?ex=67346dda&is=67331c5a&hm=61ee3a7463bd1bb5e4240082bd5d774d03a4a3cb44d317ae8a6fc58b295db682&=&format=webp&quality=lossless&width=416&height=582': 'Saamito', 'https://media.discordapp.net/attachments/1246831135959547944/1305641714056433744/14_ChoKo.png?ex=67346dda&is=67331c5a&hm=746e5bd43d71e6b8069a34b3d664f3bc765a02169424932d39b8343994e35e60&=&format=webp&quality=lossless&width=416&height=582': 'ChoKo', 'https://media.discordapp.net/attachments/1246831135959547944/1305641714815471687/15_QV.png?ex=67346dda&is=67331c5a&hm=c57033f5d38c92e1de820d93a67e0d6c368f576f9d3449bab54bbdf2c41270c9&=&format=webp&quality=lossless&width=416&height=582': 'QV', 'https://media.discordapp.net/attachments/1246831135959547944/1305641715293753385/11_Aless.png?ex=67346dda&is=67331c5a&hm=73b05328018b13525f62c3a6078684a4843dc0eeaa21a4dad795bbf8d22bcbbc&=&format=webp&quality=lossless&width=416&height=582': 'Aless', 'https://media.discordapp.net/attachments/1246831135959547944/1305641715926958130/42_Skuter.png?ex=67346dda&is=67331c5a&hm=79b548174873b3910dcb45d1e90efc0d1d0df6bb72227dc557e18b10b1cb70c2&=&format=webp&quality=lossless&width=416&height=582': 'Skuter', 'https://media.discordapp.net/attachments/1246831135959547944/1305641716463964230/46_Amaury.png?ex=67346dda&is=67331c5a&hm=a8b81cfd9dfac67233691b69429bfba3660f8e3ca21c6a6de7eb324bd84398c3&=&format=webp&quality=lossless&width=416&height=582': 'Amaury', 'https://media.discordapp.net/attachments/1246831135959547944/1305896292190257253/38_Watson.png?ex=6734b232&is=673360b2&hm=b71d80a31c989de8d692a7956479e1c1d52d1176e066cd8e85f2f60eff04d052&=&format=webp&quality=lossless&width=416&height=582': 'Watson', 'https://media.discordapp.net/attachments/1246831135959547944/1305641781936914594/18_ByDyVix.png?ex=67346dea&is=67331c6a&hm=f0551e4c3dcc5ebb00e443ac01487a0ed39d4fe05762927d879393040d9a94e1&=&format=webp&quality=lossless&width=416&height=582': 'ByDyVix', 'https://media.discordapp.net/attachments/1246831135959547944/1305641227940790312/30_Alnwick.png?ex=67346d66&is=67331be6&hm=d0699b6b82e3804c991ff92971aca81af085aedb836285e4f965f3ab6e4ca12f&=&format=webp&quality=lossless&width=416&height=582': 'Alnwick', 'https://media.discordapp.net/attachments/1246831135959547944/1305641228796297216/12_Amin.png?ex=67346d66&is=67331be6&hm=8bad4732133447ef7289ea4d6cb6ff829b782defcb3a24ac8b139e625b42bdf6&=&format=webp&quality=lossless&width=416&height=582': 'Amin', 'https://media.discordapp.net/attachments/1246831135959547944/1305641229538820197/23_Yatho.png?ex=67346d66&is=67331be6&hm=69fac93ca8214de1696316aa92f0b979776d1001d7948911bd39617dde03b5f0&=&format=webp&quality=lossless&width=416&height=582': 'Yatho', 'https://media.discordapp.net/attachments/1246831135959547944/1305641230415302697/32_Gnagna.png?ex=67346d66&is=67331be6&hm=c74c80ad4951cab63113d605cbebf6066c201ff8338d16035b98dd4375ffa3ef&=&format=webp&quality=lossless&width=416&height=582': 'Gnagna', 'https://media.discordapp.net/attachments/1246831135959547944/1305641341199585442/65_Totay.png?ex=67346d81&is=67331c01&hm=2f2eca3da6a431fb833dd49037f6d82544ae2a94846912767bd8e7a087a55b25&=&format=webp&quality=lossless&width=416&height=582': 'Totay spécial', 'https://media.discordapp.net/attachments/1246831135959547944/1305641341803430009/68_Thyx.png?ex=67346d81&is=67331c01&hm=cab0f3021cc730fe7422536559da47bcdeff6af624a9a99fd91469a27c3db071&=&format=webp&quality=lossless&width=416&height=582': 'Thyx spécial', 'https://media.discordapp.net/attachments/1246831135959547944/1305641342466261092/64_QV.png?ex=67346d81&is=67331c01&hm=cd05074fe609b69a52937e4038fa81569c4654e9549b77b7448b2c46a22db96e&=&format=webp&quality=lossless&width=416&height=582': 'QV spécial', 'https://media.discordapp.net/attachments/1246831135959547944/1305641343355457597/66_Yatho.png?ex=67346d81&is=67331c01&hm=7906b433af4bb5d04001ad9081e760ad6e969508c09b7bac86195d27e4de021d&=&format=webp&quality=lossless&width=416&height=582': 'Yatho spécial', 'https://media.discordapp.net/attachments/1246831135959547944/1305641344085135472/67_Gnagna.png?ex=67346d82&is=67331c02&hm=7c8cc8ccf959080e07e44582875b7159e6f190a606bdb1dfd681e5618bb9062c&=&format=webp&quality=lossless&width=416&height=582': 'Gnagna spécial', 'https://media.discordapp.net/attachments/1246831135959547944/1305899140055826432/72_Watson.png?ex=6734b4d9&is=67336359&hm=f3fd92cabc1aba3346a024d91d92ef4122ba70ceed7bf1e0703efc931253147d&=&format=webp&quality=lossless&width=416&height=582': 'Watson spécial', 'https://media.discordapp.net/attachments/1246831135959547944/1305899140860874913/69_Black.png?ex=6734b4d9&is=67336359&hm=eba7cbdf585b02bce86a9f01fdfb1767bc0308a0d6a10e717185c0f1256d708c&=&format=webp&quality=lossless&width=416&height=582': 'Black spécial (il fout quoi là lui mm)', 'https://media.discordapp.net/attachments/1246831135959547944/1305899141607718922/70_Apollo.png?ex=6734b4d9&is=67336359&hm=54ce4244f1f5ab3aa2923192eebd4a35e7285f203d2d9eeee6f6c38a84d0599d&=&format=webp&quality=lossless&width=416&height=582': 'Apollo spécial', 'https://media.discordapp.net/attachments/1246831135959547944/1305899142274351154/71_ByDyVix.png?ex=6734b4d9&is=67336359&hm=55f91bd7265b94dbf659c0887ac7f5fc1d8c73ff6cf228f45299ffbc01c323d7&=&format=webp&quality=lossless&width=416&height=582': 'ByDyVix spécial', 'https://media.discordapp.net/attachments/1304268220089499693/1305958411493576715/carte_torg_save_9.png?ex=6734ec0c&is=67339a8c&hm=4186870f3d0993c6fee0c47041e80a927677427d1f574c2cf4a8de3bf1ee6238&=&format=webp&quality=lossless&width=224&height=314': 'Lettonie', 'https://media.discordapp.net/attachments/1304268220089499693/1305956966866354267/61_Luxembourg.png?ex=6734eab4&is=67339934&hm=c0e66976bd889ed457b87944f7c2a8b2136f8f83c4140cd960fa3134f22f3bc6&=&format=webp&quality=lossless&width=224&height=314': 'Luxembourg', 'https://media.discordapp.net/attachments/1304268220089499693/1305955894789406780/60_Uruguay.png?ex=6734e9b4&is=67339834&hm=39fcbf4dcfcc6e8aa06c8baca511891cbabbf4ac67ccef90961dfcb68d1c9709&=&format=webp&quality=lossless&width=224&height=314': 'Uruguay', 'https://media.discordapp.net/attachments/1304268220089499693/1305954745080610846/59_Guinee.png?ex=6734e8a2&is=67339722&hm=29eddc277f7164e051374f23cc2a01e1035fd4fafd04a062c90cdce69bbbfdd4&=&format=webp&quality=lossless&width=224&height=314': 'Guinee', 'https://media.discordapp.net/attachments/1304268220089499693/1305953959210651679/63_Islande.png?ex=6734e7e7&is=67339667&hm=fb8f57856bc3f5fe89919de7d4920e4cda87ed0423f442a0eb8dd1504dafcdd8&=&format=webp&quality=lossless&width=224&height=314': 'Islande', 'https://media.discordapp.net/attachments/1304268220089499693/1305953947910930472/53_Algerie.png?ex=6734e7e4&is=67339664&hm=3c8857038264f9e9435391660f9bf88a1b88190ccdfb732506abf9209a4b63c0&=&format=webp&quality=lossless&width=416&height=582': 'Algerie', 'https://media.discordapp.net/attachments/1304268220089499693/1305953948284489839/54_France.png?ex=6734e7e4&is=67339664&hm=3b88d91f7889fda7c9fdd116359d2357a135d97c44684229b8141dfb5b506a09&=&format=webp&quality=lossless&width=416&height=582': 'France', 'https://media.discordapp.net/attachments/1304268220089499693/1305953948678750279/55_Japon.png?ex=6734e7e4&is=67339664&hm=10a5978ad17ce8279db2c1ca95baa4ce4afa4daff3fe33b35e6d60ed2b496b6e&=&format=webp&quality=lossless&width=416&height=582': 'Japon', 'https://media.discordapp.net/attachments/1304268220089499693/1305953946585530399/57_Georgie.png?ex=6734e7e4&is=67339664&hm=071e173770df0297ccd4d662b0acc39835ef4e0131a39081e11df539fdbaff3e&=&format=webp&quality=lossless&width=416&height=582': 'Georgie', 'https://media.discordapp.net/attachments/1304268220089499693/1305953947001032724/58_Espagne.png?ex=6734e7e4&is=67339664&hm=7d93896edfafbb830d68d95cf7e023db93b67ac43629dc484628b58dedcc26a9&=&format=webp&quality=lossless&width=416&height=582': 'Espagne', 'https://media.discordapp.net/attachments/1304268220089499693/1305953947449819147/52_Bresil.png?ex=6734e7e4&is=67339664&hm=4990a8867568ff053b695dbf74880514b7218c7866ab49636597d522d04bdc27&=&format=webp&quality=lossless&width=416&height=582': 'Bresil'}



nul = [
    "https://media.discordapp.net/attachments/1246831135959547944/1305642407303319642/5_BlackLolo.png?ex=67346e7f&is=67331cff&hm=d828c8853d2e28c16018ce09a6e5dd6bcf484db85ad2d4a46324d51583fe1d34&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305642407806631956/13_Totay.png?ex=67346e7f&is=67331cff&hm=dafdd7cd49a5b9ddccf50a4f5272450636993a8713bfa865c742207f99394ee8&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305642408301563904/3_Chapi.png?ex=67346e7f&is=67331cff&hm=d4992e79ff50640789c0750cdcabf8d288abdb94f72596233d400d2af9688c7f&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305642408821788742/16_MrGwak.png?ex=67346e7f&is=67331cff&hm=cb86f1efa430d52b90190b5d49aa6838bb77c4775bce19a721d243539bffe2fc&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305642409446609037/21_Kenzo.png?ex=67346e80&is=67331d00&hm=6b0c8250410c925f5e16b78461998e5bf4e5017d8203dfba074a6d3654486ef0&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305642410230939648/26_Layte.png?ex=67346e80&is=67331d00&hm=3728fa1df6b8de7698d4a5004aafca076a788dec8de04d1197589a5e7b94f4c1&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305642410755493948/27_Cramptox.png?ex=67346e80&is=67331d00&hm=6220a8b7007cc3cc87625b4625dd234e18dc542ab07790e100d131e9fdb88eb0&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305642411245961356/28_Yoddle.png?ex=67346e80&is=67331d00&hm=40009331b3818114b7066e5c98503219b9bcbd293be7b485f181bac6415f4f33&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305642411690561606/29_Cha.png?ex=67346e80&is=67331d00&hm=c59c36554848b980849a3eb8134d562529e8bbc4faa91c46673a6fa58db6a7f9&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305642412206456913/31_Scan.png?ex=67346e80&is=67331d00&hm=dcfd5f932aa6d60b295cba5247bd3409210c3fcdd2627d832addf3f69fa79555&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305642494163288205/33_Black.png?ex=67346e94&is=67331d14&hm=155c54654feb659b765c5be89b040d99847a700948b7feedf433b2c8c6991f87&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305642494708678776/34_Natsu.png?ex=67346e94&is=67331d14&hm=e2d67cdf35282dbf830d84ebe94aec08483f9dfba09a570aa9a30ec77d4e3afc&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305642495329177660/35_Saltay.png?ex=67346e94&is=67331d14&hm=e631e82b2074c78e02737ee7fb0a78b261e4c1c0918c3c1fa96b0bd763e41f57&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305642496004587571/36_TMH.png?ex=67346e94&is=67331d14&hm=99ceb011d82544aeba05a97f2600e9efb975c3045b4cd8640ef2f3c603636245&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305642496608702474/39_Xiao.png?ex=67346e94&is=67331d14&hm=5c3787bc3bff1f074a8ef887b3edb233b168ef123f5daa4e2ba3a8d3f4ef2517&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305642497174802452/43_Dabi.png?ex=67346e94&is=67331d14&hm=808d010798a52c3d3372c17ef07e87c6b6fd5844dd8f23a782ce2e99771cadb0&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305642497820852224/45_Apollo.png?ex=67346e95&is=67331d15&hm=26798b3ec0fd831e8af7869166ce829dc8b3eb44f0e169123747fd9e6804f816&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305642575897559061/48_TreekoZ.png?ex=67346ea7&is=67331d27&hm=aafbf2d2da23db9ae4b9edf89d3f2d25567985a3f846c05058eb6eef59bf9c84&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305642576417787945/49_Sensei.png?ex=67346ea7&is=67331d27&hm=85909d328fb3e6a48e44f9acac20bf0c49f492677562e03d39cf18a91269f8c8&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305642577906896906/50_Kchouuu.png?ex=67346ea8&is=67331d28&hm=4d38255a44463b3f57594dee14bc550c5c42f5c8fb62f99e44b95bc72742c624&=&format=webp&quality=lossless&width=416&height=582"




]



clubs = [

]



mal = [
    "https://media.discordapp.net/attachments/1246831135959547944/1305642037705441370/4_Luigi.png?ex=67346e27&is=67331ca7&hm=8476b197d73787f8dbccad6f8346d2025a60d57cdd87b0287fe886fc8c98e69f&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305642038179532960/6_Herope.png?ex=67346e27&is=67331ca7&hm=4824e1d94474dd2e49aa80eaf4ee28f706fc2043f2eb4f21196c2ff046212a65&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305642038955348008/7_Nono.png?ex=67346e27&is=67331ca7&hm=f9f8f1b7327d9bb9d06782a89a9adb6eedeb2d78a4bf3518491576eb84a54399&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305642039475437578/8_Sander.png?ex=67346e27&is=67331ca7&hm=e76593c44dc0357ec2fe9157ffdac399461bb229ed051ce9887b521995969368&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305642040104718437/10_Raph.png?ex=67346e28&is=67331ca8&hm=e2c6af2530d97ce8902505c2497e967aeb7718a9ea4d44bebbd01098b80a65e0&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305642040607903864/17_Nekoss.png?ex=67346e28&is=67331ca8&hm=dc724eaf2e626abef64bf7a8aa039f51f7d35b73a5940fb04392a361ff12c9f8&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305642041094438973/19_Heros.png?ex=67346e28&is=67331ca8&hm=c74e82cf8ed47eaed0c445cee91207d8bdfab4223430f1e8ba874d9f7b2fcab2&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305642041547558983/20_Regis.png?ex=67346e28&is=67331ca8&hm=490c851f2efd5371381a3896a06a00b0232538fbce0c42bfcb45277fb9a8c832&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305642041966858341/24_Alan.png?ex=67346e28&is=67331ca8&hm=efbbe7da48f098f5796db93ccdb555ad3d3fa6adb9c6110a4a8573b303660441&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305642117749801011/25_Ener.png?ex=67346e3a&is=67331cba&hm=62c6da7d1a286add66d77fc97208b685e3c25b0f8e4d306be70291626670ba84&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305642118433476718/40_Hiroo.png?ex=67346e3a&is=67331cba&hm=a68aab238ea9e5ee7a21d096232309e464b464292249a2a03a28699c064df4f2&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305642119129469049/41_Loni.png?ex=67346e3a&is=67331cba&hm=582f8ccebbc4a4c81bb37011718df7039c992d89313173fb29bbc31f30134915&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305642119720997027/44_Guillem.png?ex=67346e3a&is=67331cba&hm=eff647e478d06c21b105e4bede090942ecedbaebfbdf6ede07e8495a73828bde&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305642120417382440/47_Nicovid.png?ex=67346e3b&is=67331cbb&hm=8b71512fa63880df5bfa7bdbb6920768a855510adfb49f054c463564c9bf836d&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305642121008644187/51_Polo.png?ex=67346e3b&is=67331cbb&hm=ae6413e2fb5f1568b5518f575e77b3a3232e204b575044dd4cb2368b918ff0aa&=&format=webp&quality=lossless&width=416&height=582"
]

good = [
    "https://media.discordapp.net/attachments/1246831135959547944/1305641710923026492/22_Redman.png?ex=67346dd9&is=67331c59&hm=f7ea55a6e09b970b82a979baf37bb883e83f1791e1d0b77286833a732ab17760&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305641711493714020/37_GB1.png?ex=67346dd9&is=67331c59&hm=7d7d689eb5f47e8e31a4b952823a046f659087cca9dda7f1d8784f9bffcd596c&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305641711984316446/1_Grenzo.png?ex=67346dd9&is=67331c59&hm=884341c00da3a3a7cb85a94621c53f40d7074101ec3b41a1c26e7ae0cf438444&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305641712785293403/2_Thyx.png?ex=67346dd9&is=67331c59&hm=796085776f282f065355ec2ced38a0b808eb82077adcb329502f5695d247c10e&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305641713330688040/9_Saamito.png?ex=67346dda&is=67331c5a&hm=61ee3a7463bd1bb5e4240082bd5d774d03a4a3cb44d317ae8a6fc58b295db682&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305641714056433744/14_ChoKo.png?ex=67346dda&is=67331c5a&hm=746e5bd43d71e6b8069a34b3d664f3bc765a02169424932d39b8343994e35e60&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305641714815471687/15_QV.png?ex=67346dda&is=67331c5a&hm=c57033f5d38c92e1de820d93a67e0d6c368f576f9d3449bab54bbdf2c41270c9&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305641715293753385/11_Aless.png?ex=67346dda&is=67331c5a&hm=73b05328018b13525f62c3a6078684a4843dc0eeaa21a4dad795bbf8d22bcbbc&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305641715926958130/42_Skuter.png?ex=67346dda&is=67331c5a&hm=79b548174873b3910dcb45d1e90efc0d1d0df6bb72227dc557e18b10b1cb70c2&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305641716463964230/46_Amaury.png?ex=67346dda&is=67331c5a&hm=a8b81cfd9dfac67233691b69429bfba3660f8e3ca21c6a6de7eb324bd84398c3&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305896292190257253/38_Watson.png?ex=6734b232&is=673360b2&hm=b71d80a31c989de8d692a7956479e1c1d52d1176e066cd8e85f2f60eff04d052&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305641781936914594/18_ByDyVix.png?ex=67346dea&is=67331c6a&hm=f0551e4c3dcc5ebb00e443ac01487a0ed39d4fe05762927d879393040d9a94e1&=&format=webp&quality=lossless&width=416&height=582"
    , "https://media.discordapp.net/attachments/1304268220089499693/1305958411493576715/carte_torg_save_9.png?ex=6734ec0c&is=67339a8c&hm=4186870f3d0993c6fee0c47041e80a927677427d1f574c2cf4a8de3bf1ee6238&=&format=webp&quality=lossless&width=224&height=314",
    "https://media.discordapp.net/attachments/1304268220089499693/1305956966866354267/61_Luxembourg.png?ex=6734eab4&is=67339934&hm=c0e66976bd889ed457b87944f7c2a8b2136f8f83c4140cd960fa3134f22f3bc6&=&format=webp&quality=lossless&width=224&height=314",
    "https://media.discordapp.net/attachments/1304268220089499693/1305955894789406780/60_Uruguay.png?ex=6734e9b4&is=67339834&hm=39fcbf4dcfcc6e8aa06c8baca511891cbabbf4ac67ccef90961dfcb68d1c9709&=&format=webp&quality=lossless&width=224&height=314",
    "https://media.discordapp.net/attachments/1304268220089499693/1305954745080610846/59_Guinee.png?ex=6734e8a2&is=67339722&hm=29eddc277f7164e051374f23cc2a01e1035fd4fafd04a062c90cdce69bbbfdd4&=&format=webp&quality=lossless&width=224&height=314",
    "https://media.discordapp.net/attachments/1304268220089499693/1305953959210651679/63_Islande.png?ex=6734e7e7&is=67339667&hm=fb8f57856bc3f5fe89919de7d4920e4cda87ed0423f442a0eb8dd1504dafcdd8&=&format=webp&quality=lossless&width=224&height=314",
    "https://media.discordapp.net/attachments/1304268220089499693/1305953947910930472/53_Algerie.png?ex=6734e7e4&is=67339664&hm=3c8857038264f9e9435391660f9bf88a1b88190ccdfb732506abf9209a4b63c0&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1304268220089499693/1305953948284489839/54_France.png?ex=6734e7e4&is=67339664&hm=3b88d91f7889fda7c9fdd116359d2357a135d97c44684229b8141dfb5b506a09&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1304268220089499693/1305953948678750279/55_Japon.png?ex=6734e7e4&is=67339664&hm=10a5978ad17ce8279db2c1ca95baa4ce4afa4daff3fe33b35e6d60ed2b496b6e&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1304268220089499693/1305953946585530399/57_Georgie.png?ex=6734e7e4&is=67339664&hm=071e173770df0297ccd4d662b0acc39835ef4e0131a39081e11df539fdbaff3e&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1304268220089499693/1305953947001032724/58_Espagne.png?ex=6734e7e4&is=67339664&hm=7d93896edfafbb830d68d95cf7e023db93b67ac43629dc484628b58dedcc26a9&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1304268220089499693/1305953947449819147/52_Bresil.png?ex=6734e7e4&is=67339664&hm=4990a8867568ff053b695dbf74880514b7218c7866ab49636597d522d04bdc27&=&format=webp&quality=lossless&width=416&height=582"


]

omg = [
    "https://media.discordapp.net/attachments/1246831135959547944/1305641227940790312/30_Alnwick.png?ex=67346d66&is=67331be6&hm=d0699b6b82e3804c991ff92971aca81af085aedb836285e4f965f3ab6e4ca12f&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305641228796297216/12_Amin.png?ex=67346d66&is=67331be6&hm=8bad4732133447ef7289ea4d6cb6ff829b782defcb3a24ac8b139e625b42bdf6&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305641229538820197/23_Yatho.png?ex=67346d66&is=67331be6&hm=69fac93ca8214de1696316aa92f0b979776d1001d7948911bd39617dde03b5f0&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305641230415302697/32_Gnagna.png?ex=67346d66&is=67331be6&hm=c74c80ad4951cab63113d605cbebf6066c201ff8338d16035b98dd4375ffa3ef&=&format=webp&quality=lossless&width=416&height=582"

]

leg = [
"https://media.discordapp.net/attachments/1246831135959547944/1305641341199585442/65_Totay.png?ex=67346d81&is=67331c01&hm=2f2eca3da6a431fb833dd49037f6d82544ae2a94846912767bd8e7a087a55b25&=&format=webp&quality=lossless&width=416&height=582",
"https://media.discordapp.net/attachments/1246831135959547944/1305641341803430009/68_Thyx.png?ex=67346d81&is=67331c01&hm=cab0f3021cc730fe7422536559da47bcdeff6af624a9a99fd91469a27c3db071&=&format=webp&quality=lossless&width=416&height=582",
"https://media.discordapp.net/attachments/1246831135959547944/1305641342466261092/64_QV.png?ex=67346d81&is=67331c01&hm=cd05074fe609b69a52937e4038fa81569c4654e9549b77b7448b2c46a22db96e&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305641343355457597/66_Yatho.png?ex=67346d81&is=67331c01&hm=7906b433af4bb5d04001ad9081e760ad6e969508c09b7bac86195d27e4de021d&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305641344085135472/67_Gnagna.png?ex=67346d82&is=67331c02&hm=7c8cc8ccf959080e07e44582875b7159e6f190a606bdb1dfd681e5618bb9062c&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305899140055826432/72_Watson.png?ex=6734b4d9&is=67336359&hm=f3fd92cabc1aba3346a024d91d92ef4122ba70ceed7bf1e0703efc931253147d&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305899140860874913/69_Black.png?ex=6734b4d9&is=67336359&hm=eba7cbdf585b02bce86a9f01fdfb1767bc0308a0d6a10e717185c0f1256d708c&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305899141607718922/70_Apollo.png?ex=6734b4d9&is=67336359&hm=54ce4244f1f5ab3aa2923192eebd4a35e7285f203d2d9eeee6f6c38a84d0599d&=&format=webp&quality=lossless&width=416&height=582",
    "https://media.discordapp.net/attachments/1246831135959547944/1305899142274351154/71_ByDyVix.png?ex=6734b4d9&is=67336359&hm=55f91bd7265b94dbf659c0887ac7f5fc1d8c73ff6cf228f45299ffbc01c323d7&=&format=webp&quality=lossless&width=416&height=582"

]

keep_alive()
bot.run(token)




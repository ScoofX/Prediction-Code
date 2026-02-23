import discord
from discord.ext import commands
import requests
import datetime

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="$", intents=intents)

API_KEY = "2349d764cc2d4605abce73add1cb4ef3"
BASE_URL = "https://api.football-data.org/v4/teams"

USER_ID = 1408798307136049173
OWNER_IDS = [1392155206782947551, 1408798307136049173]  # IDs Li 3endhom perms
LOGS_CHANNEL_ID = 1464778272838783228  # channel dlogs

#   stocki predictions
predictions_data = {
    "Real Madrid": {},
    "Barcelona": {}
}

# stocki attempts   
attempts_data = {}

def is_owner(ctx):
    return ctx.author.id in OWNER_IDS

@bot.command()
async def reset(ctx):
    if ctx.author.id not in OWNER_IDS:
        await ctx.reply("** ⚠️ Jme3 ydik asahbi. **", ephemeral=True)
        return


    #  khwi predictions
    for team in predictions_data:
        predictions_data[team].clear()

    #  restart lattempts
    attempts_data.clear()

    embed = discord.Embed(
        title="♻️ Reset Done",
        color=discord.Color.red(),
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )

    owner = await bot.fetch_user(USER_ID)
    embed.set_footer(text="Pirates Prediction | Reset", icon_url=owner.display_avatar.url)

    await ctx.send(embed=embed)

# Modal for prediction input
class ResultModal(discord.ui.Modal, title="Prediction Form"):
    result = discord.ui.TextInput(label="Score Dyalk", placeholder="Ex : 2-1", required=True)

    def __init__(self, team):
        super().__init__()
        self.team = team

    async def on_submit(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        logs_channel = bot.get_channel(LOGS_CHANNEL_ID)
        owner = await bot.fetch_user(USER_ID)

        if user_id in predictions_data[self.team]:
            await interaction.response.send_message(
                f"⚠️ Deja 3ndk prediction D'{self.team}.",
                ephemeral=True
            )
            return

        predictions_data[self.team][user_id] = self.result.value

        embed = discord.Embed(
            title="📝 New Prediction",
            color=discord.Color.gold(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.add_field(name="👤 User", value=interaction.user.mention, inline=False)
        embed.add_field(name="⚽ Team", value=self.team, inline=False)
        embed.add_field(name="🔢 Prediction", value=self.result.value, inline=False)
        embed.set_footer(text="Pirates Prediction | Made By Scuuf", icon_url=owner.display_avatar.url)

        await logs_channel.send(embed=embed)
        await interaction.response.send_message("✅ Prediction dyalk tsjlat", ephemeral=True)

# View buttonsss
class PredictionView(discord.ui.View):
    @discord.ui.button(label="Real Madrid", style=discord.ButtonStyle.primary)
    async def madrid(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ResultModal("Real Madrid"))

    @discord.ui.button(label="Barcelona", style=discord.ButtonStyle.danger)
    async def barca(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ResultModal("Barcelona"))

# Function tjib liya matchat jayin mn API
def get_next_match(team_id):
    url = f"{BASE_URL}/{team_id}/matches?status=SCHEDULED&limit=1"
    headers = {"X-Auth-Token": API_KEY}
    response = requests.get(url, headers=headers)
    data = response.json()

    if "matches" in data and data["matches"]:
        match = data["matches"][0]
        home = match["homeTeam"]["name"]
        away = match["awayTeam"]["name"]
        competition = match["competition"]["name"]
        kickoff_str = match["utcDate"]

        kickoff_dt = datetime.datetime.fromisoformat(kickoff_str.replace("Z", "+00:00"))
        formatted_kickoff = kickoff_dt.strftime("%d %B %Y - %H:%M UTC")

        return home, away, competition, formatted_kickoff
    return None

@bot.command()
async def next(ctx):
    if ctx.author.id not in OWNER_IDS:
        await ctx.reply("** ⚠️ Jme3 ydik asahbi. **", ephemeral=True)
        return

    barca_match = get_next_match(81)   # Barcelona
    madrid_match = get_next_match(86)  # Real Madrid
    user = await bot.fetch_user(USER_ID)

    embed = discord.Embed(
        title="📊 Upcoming Matches",
        color=discord.Color.purple(),
    )

    if barca_match:
        home, away, competition, kickoff = barca_match
        embed.add_field(
            name="🔴 FC Barcelona",
            value=f"🏠 {home}\n🛫 {away}\n🏆 {competition}\n📅 {kickoff}",
            inline=True
        )

    embed.add_field(name="\u200b", value=" ", inline=True)  #  space mabin fields

    if madrid_match:
        home, away, competition, kickoff = madrid_match
        embed.add_field(
            name="⚪ Real Madrid",
            value=f"🏠 {home}\n🛫 {away}\n🏆 {competition}\n📅 {kickoff}",
            inline=True
        )

    embed.set_footer(text="Predict Now!", icon_url=user.display_avatar.url)
    await ctx.send(embed=embed, view=PredictionView())

@bot.command()
async def scores(ctx):
    if ctx.author.id not in OWNER_IDS:
        await ctx.reply("** ⚠️ Jme3 ydik asahbi. **", ephemeral=True)
        return

    embed = discord.Embed(
        title="📊 All Predictions",
        color=discord.Color.purple(),
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )

    # madrid 
    if predictions_data["Real Madrid"]:
        madrid_list = []
        for uid, res in predictions_data["Real Madrid"].items():
            try:
                member = ctx.guild.get_member(uid)
                if member:
                    madrid_list.append(f"{member.mention}: {res}")
                else:
                    user = await bot.fetch_user(uid)
                    madrid_list.append(f"{user.mention}: {res}")
            except Exception:
                madrid_list.append(f"ID {uid}: {res}")
        embed.add_field(name="⚪ Real Madrid", value="\n".join(madrid_list), inline=False)
    else:
        embed.add_field(name="⚪ Real Madrid", value="Makaynach 7ta chi prediction db", inline=False)

    # barcca
    if predictions_data["Barcelona"]:
        barca_list = []
        for uid, res in predictions_data["Barcelona"].items():
            try:
                member = ctx.guild.get_member(uid)
                if member:
                    barca_list.append(f"{member.mention}: {res}")
                else:
                    user = await bot.fetch_user(uid)
                    barca_list.append(f"{user.mention}: {res}")
            except Exception:
                barca_list.append(f"ID {uid}: {res}")
        embed.add_field(name="🔴 Barcelona", value="\n".join(barca_list), inline=False)
    else:
        embed.add_field(name="🔴 Barcelona", value="Makaynach 7ta chi prediction db", inline=False)

    user = await bot.fetch_user(USER_ID)
    embed.set_footer(text="Pirates Predictions | Made By Scuuf", icon_url=user.display_avatar.url)

    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

bot.run("MTQ3NDg5NDgxMDQ3NjQ0OTg4NA.GRjlM2.ZZjquiUuniROJQq81HNFaBVzyOKRHGH2vOmPyI")
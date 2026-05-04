import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import random
import datetime

load_dotenv()

raid_joins = {}
raid_messages = {}
RAID_JOIN_LIMIT = 5      # usuarios en X segundos
RAID_MSG_LIMIT = 7       # mensajes en X segundos
TIME_WINDOW = 5          # segundos


GUILD_ID = discord.Object(id=1492698037443756082)

class Client(commands.Bot):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

        await self.change_presence(
            status=discord.Status.dnd,  # 🔴 No molestar
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="Servidor de Gonza MFL II"
            )
        )

    async def setup_hook(self):
        try:
            synced = await self.tree.sync(guild=GUILD_ID)
            print(f"Sincronizados {len(synced)} comandos.")
        except Exception as e:
            print(e)
            

    async def on_message(self, message):
        if message.author == self.user:
            return
        await self.process_commands(message)

intents = discord.Intents.default()
intents.message_content = True

client = Client(command_prefix="!", intents=intents)

# =====================
# MODERACIÓN
# =====================

@app_commands.checks.has_permissions(kick_members=True)
@client.tree.command(name="kick", description="Expulsa a un usuario", guild=GUILD_ID)
async def kick(interaction: discord.Interaction, user: discord.Member, razon: str = "Sin razón"):
    await user.kick(reason=razon)
    await interaction.response.send_message(f"{user.mention} fue expulsado. 🥾")


@kick.error
async def kick_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("No tenés permisos.", ephemeral=True)


async def clear(interaction: discord.Interaction, cantidad: int):
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=cantidad)
    await interaction.followup.send(f"🧹 {len(deleted)} mensajes borrados")



@app_commands.checks.has_permissions(ban_members=True)
@client.tree.command(name="ban", description="Banea a un usuario", guild=GUILD_ID)
async def ban(interaction: discord.Interaction, user: discord.Member, razon: str = "Sin razón"):
    await user.ban(reason=razon)
    await interaction.response.send_message(f"{user.mention} fue baneado. 🔨")

@app_commands.checks.has_permissions(ban_members=True)
@client.tree.command(name="unban", description="Desbanea por ID", guild=GUILD_ID)
async def unban(interaction: discord.Interaction, user_id: str):
    user = await client.fetch_user(int(user_id))
    await interaction.guild.unban(user)
    await interaction.response.send_message(f"{user} fue desbaneado. 🔓")

@app_commands.checks.has_permissions(moderate_members=True)
@client.tree.command(name="mute", description="Silencia a un usuario", guild=GUILD_ID)
async def mute(interaction: discord.Interaction, user: discord.Member, minutos: int):
    until = discord.utils.utcnow() + datetime.timedelta(minutes=minutos)
    await user.timeout(until)
    await interaction.response.send_message(f"{user.mention} silenciado por {minutos} min 🔇")

# =====================
# UTILIDAD
# =====================

@client.tree.command(name="time", description="Hora actual", guild=GUILD_ID)
async def time(interaction: discord.Interaction):
    now = datetime.datetime.now()
    await interaction.response.send_message(f"🕒 {now.strftime('%H:%M:%S')}")

@client.tree.command(name="avatar", description="Ver avatar", guild=GUILD_ID)
async def avatar(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.send_message(user.display_avatar.url)

@client.tree.command(name="ship", description="Shippea gente", guild=GUILD_ID)
async def ship(interaction: discord.Interaction, user1: discord.Member, user2: discord.Member):
    porcentaje = random.randint(0,100)
    await interaction.response.send_message(f"💘 {user1.mention} + {user2.mention} = {porcentaje}%")


@client.tree.command(name="ping", description="Latencia del bot", guild=GUILD_ID)
async def ping(interaction: discord.Interaction):
    latency = round(client.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Latencia: **{latency}ms**",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="userinfo", description="Info de usuario", guild=GUILD_ID)
async def userinfo(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.send_message(
        f"👤 {user}\nID: {user.id}\nSe unió: {user.joined_at}"
    )

@client.tree.command(name="serverinfo", description="Info del servidor", guild=GUILD_ID)
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    await interaction.response.send_message(
        f"Servidor: {guild.name}\nMiembros: {guild.member_count}"
    )

# =====================
# FUN
# =====================

@client.tree.command(name="8ball", description="Haz una pregunta 🎱", guild=GUILD_ID)
async def eightball(interaction: discord.Interaction, pregunta: str):
    respuestas = ["Sí.", "No.", "Tal vez.", "Definitivamente.", "Ni en pedo."]

    embed = discord.Embed(
        title="🎱 Bola Mágica",
        color=discord.Color.purple()
    )
    embed.add_field(name="Pregunta", value=pregunta, inline=False)
    embed.add_field(name="Respuesta", value=random.choice(respuestas), inline=False)
    embed.set_footer(text=f"Preguntado por {interaction.user}")

    await interaction.response.send_message(embed=embed)

@client.tree.command(name="dado", description="Tira un dado", guild=GUILD_ID)
async def dado(interaction: discord.Interaction):
    await interaction.response.send_message(f"🎲 {random.randint(1,6)}")

@client.tree.command(name="coinflip", description="Cara o cruz", guild=GUILD_ID)
async def coinflip(interaction: discord.Interaction):
    await interaction.response.send_message(random.choice(["Cara 🪙", "Cruz 🪙"]))

# =====================
# OTROS
# =====================

@client.tree.command(name="say", description="Repito lo que digas", guild=GUILD_ID)
async def say(interaction: discord.Interaction, texto: str):
    await interaction.response.send_message(
    texto,
    allowed_mentions=discord.AllowedMentions.none()
)

@client.tree.command(name="gmfl", description="Canal de Gonza MFL", guild=GUILD_ID)
async def gmfl(interaction: discord.Interaction):
    await interaction.response.send_message("https://www.youtube.com/@gonzamfl")


client.run(os.getenv("TOKEN"))
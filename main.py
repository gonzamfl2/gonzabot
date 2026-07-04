import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import random
import datetime

load_dotenv()


class Client(commands.Bot):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

        await self.change_presence(
            status=discord.Status.dnd,
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="Servidor de Gonza MFL II"
            )
        )

    async def setup_hook(self):
        try:
            synced = await self.tree.sync()
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

@client.event
async def on_guild_channel_delete(channel):
    guild = channel.guild

    async for entry in guild.audit_logs(
        limit=3,
        action=discord.AuditLogAction.channel_delete
    ):
        usuario = entry.user

        ahora = time.time()
        eliminaciones[usuario.id].append(ahora)

        # Mantener solo los últimos 10 segundos
        eliminaciones[usuario.id] = [
            t for t in eliminaciones[usuario.id]
            if ahora - t <= 10
        ]

        # Si elimina 3 o más canales en 10 segundos
        if len(eliminaciones[usuario.id]) >= 3:
            await guild.ban(
                usuario,
                reason="Anti-raid: eliminación masiva de canales"
            )

# =====================
# MODERACIÓN
# =====================

@app_commands.checks.has_permissions(kick_members=True)
@client.tree.command(name="kick", description="Expulsa a un usuario")
async def kick(interaction: discord.Interaction, user: discord.Member, razon: str = "Sin razón"):
    await user.kick(reason=razon)
    await interaction.response.send_message(f"{user.mention} fue expulsado. 🥾")


@kick.error
async def kick_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("No tenés permisos.", ephemeral=True)


@app_commands.checks.has_permissions(manage_messages=True)
@client.tree.command(name="clear", description="Borra mensajes")
async def clear(interaction: discord.Interaction, cantidad: int):
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=cantidad)
    await interaction.followup.send(f"🧹 {len(deleted)} mensajes borrados")


@app_commands.checks.has_permissions(ban_members=True)
@client.tree.command(name="ban", description="Banea a un usuario")
async def ban(interaction: discord.Interaction, user: discord.Member, razon: str = "Sin razón"):
    await user.ban(reason=razon)
    await interaction.response.send_message(f"{user.mention} fue baneado. 🔨")

@app_commands.checks.has_permissions(ban_members=True)
@client.tree.command(name="unban", description="Desbanea por ID")
async def unban(interaction: discord.Interaction, user_id: str):
    user = await client.fetch_user(int(user_id))
    await interaction.guild.unban(user)
    await interaction.response.send_message(f"{user} fue desbaneado. 🔓")

@app_commands.checks.has_permissions(moderate_members=True)
@client.tree.command(name="mute", description="Silencia a un usuario")
async def mute(interaction: discord.Interaction, user: discord.Member, minutos: int):
    until = discord.utils.utcnow() + datetime.timedelta(minutes=minutos)
    await user.timeout(until)
    await interaction.response.send_message(f"{user.mention} silenciado por {minutos} min 🔇")

# =====================
# UTILIDAD
# =====================

@client.tree.command(name="time", description="Hora actual")
async def time(interaction: discord.Interaction):
    now = datetime.datetime.now()
    await interaction.response.send_message(f"🕒 {now.strftime('%H:%M:%S')}")


@client.tree.command(name="memide")
async def memide(interaction: discord.Interaction):
    cm = random.randint(5,20)
    await interaction.response.send_message("A {user.mention} le mide {cm}cm")

@client.tree.command(name="avatar", description="Ver avatar")
async def avatar(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.send_message(user.display_avatar.url)

@client.tree.command(name="ship", description="Shippea gente")
async def ship(interaction: discord.Interaction, user1: discord.Member, user2: discord.Member):
    porcentaje = random.randint(0,100)
    await interaction.response.send_message(f"💘 {user1.mention} + {user2.mention} = {porcentaje}%")


@client.tree.command(name="ping", description="Latencia del bot")
async def ping(interaction: discord.Interaction):
    latency = round(client.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Latencia: **{latency}ms**",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="userinfo", description="Info de usuario")
async def userinfo(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.send_message(
        f"👤 {user}\nID: {user.id}\nSe unió: {user.joined_at}"
    )

@client.tree.command(name="memide", description="¿Cuanto te mide?")
@app_commands.describe(usuario="Usuario")
async def memide(interaction: discord.Interaction, usuario: discord.Member):
    medida = random.randint(0, 30)

    await interaction.response.send_message(
        f"📏 A {usuario.mention} le mide **{medida} cm**."
    )


@client.tree.command(name="serverinfo", description="Info del servidor")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild

    embed = discord.Embed(
        title=f"📊 Información del servidor",
        description=f"**{guild.name}**",
        color=discord.Color.blurple()
    )

    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)

    embed.add_field(
        name="🆔 ID",
        value=guild.id,
        inline=True
    )

    embed.add_field(
        name="👥 Miembros",
        value=guild.member_count,
        inline=True
    )

    embed.add_field(
        name="👑 Owner",
        value=guild.owner.mention if guild.owner else "Desconocido",
        inline=True
    )

    embed.add_field(
        name="📅 Creado",
        value=guild.created_at.strftime("%d/%m/%Y"),
        inline=True
    )

    embed.add_field(
        name="💬 Canales",
        value=len(guild.channels),
        inline=True
    )

    embed.add_field(
        name="🔐 Roles",
        value=len(guild.roles),
        inline=True
    )

    embed.set_footer(text=f"Solicitado por {interaction.user}", icon_url=interaction.user.display_avatar.url)

    await interaction.response.send_message(embed=embed)
    
# =====================
# FUN
# =====================

@client.tree.command(name="8ball", description="Haz una pregunta 🎱")
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

@client.tree.command(name="dado", description="Tira un dado")
async def dado(interaction: discord.Interaction):
    await interaction.response.send_message(f"🎲 {random.randint(1,6)}")

@client.tree.command(name="coinflip", description="Cara o cruz")
async def coinflip(interaction: discord.Interaction):
    await interaction.response.send_message(random.choice(["Cara 🪙", "Cruz 🪙"]))

# =====================
# OTROS
# =====================

@client.tree.command(name="say", description="Repito lo que digas")
async def say(interaction: discord.Interaction, texto: str):
    await interaction.response.send_message(
    texto,
    allowed_mentions=discord.AllowedMentions.none()
)

@client.tree.command(name="gmfl", description="Canal de Gonza MFL")
async def gmfl(interaction: discord.Interaction):
    await interaction.response.send_message("https://www.youtube.com/@gonzamfl")

@client.tree.command(name="monitor", description="Monitor que usa Gonza MFL")
async def gmfl(interaction: discord.Interaction):
    await interaction.response.send_message("Flatron W1953S 75hz (Muy humilde lo se)")




client.run(os.getenv("TOKEN"))

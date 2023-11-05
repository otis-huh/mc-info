import os
from dotenv import load_dotenv
import discord
from discord import app_commands
from mcstatus import JavaServer
import io, base64
import datetime

load_dotenv()

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync()
    print(f'Ready! Logged in as {client.user}')

@tree.error
async def on_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    await interaction.followup.send(error)

@tree.command(name = "server", description = "Show server info.")
@app_commands.describe(server_ip="The IP of the server to lookup.")
async def server(interaction, server_ip: str):
    await interaction.response.defer()

    server = JavaServer.lookup(server_ip)
    status = server.status()

    if not status.icon:
        image = "https://media.minecraftforum.net/attachments/300/619/636977108000120237.png"
    else:
        file = discord.File(io.BytesIO(base64.b64decode(status.icon.lstrip("data:image/png;base64"))), filename="image.png")
        image = "attachment://image.png"

    embed = discord.Embed(
        title = f"{server_ip}",
        description = f"{status.motd.to_plain()}",
        timestamp=datetime.datetime.now()
    )
    embed.set_thumbnail(url=image)
    embed.add_field(name="Version", value=f"{status.version.name}", inline=True)
    embed.add_field(name="Latency", value=f"{round(status.latency, 2)}", inline=True)
    embed.add_field(name="Players", value=f"{status.players.online}/{status.players.max}", inline=True)
    embed.set_footer(text=f"{interaction.user.name}", icon_url=f"{interaction.user.display_avatar.url}")

    await interaction.followup.send(file=file, embed=embed)


@tree.command(name = "players", description = "Show players on server if possible.")
@app_commands.describe(server_ip="The IP of the server to lookup.")
async def players(interaction, server_ip: str):
    await interaction.response.defer()

    server = JavaServer.lookup(server_ip)
    
    try:
        query = server.query()
    except:
        status = server.status()

        if not status.players.sample:
            await interaction.followup.send("Cant find players list, no one online or the server disabled this.")
        else:
            await interaction.followup.send("Players online: " + ", ".join([player.name for player in status.players.sample]))
    else:
        await interaction.followup.send("Players online: " + ", ".join(query.players.names))

client.run(os.getenv("DISCORD_TOKEN"))
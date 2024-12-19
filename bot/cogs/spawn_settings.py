import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite

spawn_channel = 'data/spawn-channel'

class SpawnSettings(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def cog_load(self) -> None:
        async with aiosqlite.connect(spawn_channel) as db:
            await db.execute('CREATE TABLE IF NOT EXISTS settings (guild_id INTEGER, spawn_channel INTEGER)')
            await db.commit()

    @app_commands.command(name='set-spawn-channel', description='Sets the spawn channel')
    @app_commands.describe(channel='The channel to set as the spawn channel')
    @app_commands.default_permissions(manage_guild=True)
    async def set_spawn_channel(self, interaction: discord.Interaction, channel: discord.TextChannel) -> None:
        async with aiosqlite.connect(spawn_channel) as db:
            async with db.execute('SELECT * FROM settings WHERE guild_id = ?', (interaction.guild_id,)) as cursor:
                result = await cursor.fetchone()
                if result is None:
                    await db.execute('INSERT INTO settings (guild_id, spawn_channel) VALUES (?, ?)', (interaction.guild_id, channel.id))
                    embed = discord.Embed(title='Spawn Channel Set', description=f'Spawn channel set to {channel.mention}', color=discord.Color.green())
                else:
                    await db.execute('UPDATE settings SET spawn_channel = ? WHERE guild_id = ?', (channel.id, interaction.guild_id))
                    embed = discord.Embed(title='Spawn Channel Updated', description=f'Spawn channel updated to {channel.mention}', color=discord.Color.green())
                await db.commit()
                embed.set_thumbnail(url=interaction.guild.icon.url)
                embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)
                embed.timestamp = discord.utils.utcnow()
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name='remove-spawn-channel', description='Removes the spawn channel')
    @app_commands.default_permissions(manage_guild=True)
    async def remove_spawn_channel(self, interaction: discord.Interaction) -> None:
        async with aiosqlite.connect(spawn_channel) as db:
            async with db.execute('SELECT * FROM settings WHERE guild_id = ?', (interaction.guild_id,)) as cursor:
                result = await cursor.fetchone()
                if result is None:
                    embed = discord.Embed(title='Spawn Channel Not Set', description='Spawn channel not set', color=discord.Color.red())
                else:
                    await db.execute('DELETE FROM settings WHERE guild_id = ?', (interaction.guild_id,))
                    embed = discord.Embed(title='Spawn Channel Removed', description='Spawn channel removed', color=discord.Color.green())
                await db.commit()
                embed.set_thumbnail(url=interaction.guild.icon.url)
                embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)
                embed.timestamp = discord.utils.utcnow()
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name='current-spawn-channel', description='Shows the spawn channel')
    async def current_spawn_channel(self, interaction: discord.Interaction) -> None:
        async with aiosqlite.connect(spawn_channel) as db:
            async with db.execute('SELECT * FROM settings WHERE guild_id = ?', (interaction.guild_id,)) as cursor:
                result = await cursor.fetchone()
                if result is None:
                    embed = discord.Embed(title='Spawn Channel Not Set', description='Spawn channel not set', color=discord.Color.red())
                else:
                    channel = interaction.guild.get_channel(result[1])
                    embed = discord.Embed(title='Current Spawn Channel', description=f'Current spawn channel is {channel.mention}', color=discord.Color.green())
                await db.commit()
                embed.set_thumbnail(url=interaction.guild.icon.url)
                embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)
                embed.timestamp = discord.utils.utcnow()
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SpawnSettings(bot))
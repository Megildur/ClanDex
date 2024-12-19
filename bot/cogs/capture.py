import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite

captures = 'data/captures'

class Capture(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def cog_load(self) -> None:
        async with aiosqlite.connect(captures) as db:
            await db.execute('CREATE TABLE IF NOT EXISTS captures (user_id INTEGER, captures INTEGER)')
            await db.commit()

    @app_commands.command(name='dex', description='Shows the dex')
    @app_commands.describe(pokemon='Show captured Clans')
    async def dex(self, interaction: discord.Interaction) -> None:
        async with aiosqlite.connect(captures) as db:
            async with db.execute('SELECT * FROM captures WHERE user_id = ?', (interaction.user.id,)) as cursor:
                result = await cursor.fetchall()
                if result is None:
                    embed = discord.Embed(title='Dex Not Found', description='You have not captured any Clans', color=discord.Color.red())
                else:
                    embed = discord.Embed(title='Dex', description='Your captured Clans', color=discord.Color.green())
                    embed.set_thumbnail(url=interaction.user.avatar.url)
                    embed.set_footer(text=interaction.user.name, icon_url=interaction.user.avatar.url)
                    embed.timestamp = discord.utils.utcnow()
                    for i in result:
                        embed.add_field(name=f'{i[0]}', value=f'{i[1]}', inline=False)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Capture(bot))
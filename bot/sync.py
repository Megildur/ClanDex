import os
import discord
from discord.app_commands.commands import guilds
from discord.ext import commands
from discord import app_commands
import random
import asyncio

allowed_guilds = [1293647067998326936, 12624578879307162]

class SyncCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    async def cog_load(self) -> None:
        tree = self.bot.tree
        self._old_tree_error = tree.on_error
        tree.on_error = self.tree_on_error

    async def cog_unload(self) -> None:
        tree = self.bot.tree
        tree.on_error = self._old_tree_error

    async def tree_on_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ) -> None:
        if isinstance(error, app_commands.CommandOnCooldown):
            retry_after = int(error.retry_after)
            if retry_after <= 60:
                retry_after1 = f"{retry_after} seconds"
            elif retry_after <= 3600:
                retry_after1 = f"{retry_after // 60} minutes"
            else:
                retry_after1 = f"{retry_after // 3600} hours"
            if interaction.command.name == "daily":
                embed = discord.Embed(
                    title="Daily",
                    description=f"You have already claimed your daily reward. Please try again in {retry_after1}.",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            embed = discord.Embed(
                title="Command Cooldown",
                description=f"This command is on cooldown. Please try again in {retry_after1}.",
                color=discord.Color.red()
            )
            try:
                if interaction.response.is_done():
                    await interaction.followup.send(embed=embed, ephemeral=True)
                else:
                    await interaction.response.send_message(embed=embed, ephemeral=True)
            except discord.HTTPException:
                print(f"Failed to send cooldown message for {interaction.user.name}#{interaction.user.discriminator}")

    @commands.command(name='sync', description='Syncs the bot', hidden=True)
    @commands.is_owner()
    async def sync(self, ctx) -> None:
        synced = await self.bot.tree.sync(guild=None)
        print(f'Synced {len(synced)} commands')
        all_commands = [cmd.name for cmd in self.bot.tree.get_commands()]
        print(f'Synced commands: {all_commands}')
        mod_group = discord.utils.get(self.bot.tree.get_commands(), name='mod')
        if mod_group:
            mod_commands = [cmd.name for cmd in mod_group.commands]
            print(f'Synced mod commands: {mod_commands}')
        else:
            print('Mod group not found')
        embed = discord.Embed(title='Sync Complete', description='The bot has been synced successfully.', color=discord.Color.green())
        embed.add_field(name='**SYNCED COMMANDS**', value=f"Synced {len(synced)} command groups")
        embed.add_field(name='**GROUPS SYNCED**', value=f"Synced commands: {', '.join(all_commands)}")
        if mod_group:
            embed.add_field(name=f"{len(mod_commands)} MODERATION COMMANDS SYNCED", value=f"Synced commands: {', '.join(mod_commands)}")
        await ctx.send(embed=embed)
            
    @commands.command(name='syncg', description='Syncs the bot', hidden=True)
    @commands.is_owner()
    async def syncg(self, ctx, guild: discord.Guild) -> None:
        synced = await self.bot.tree.sync(guild=guild)
        print(f'Synced {len(synced)} commands')
        all_commands = [cmd.name for cmd in self.bot.tree.get_commands()]
        print(f'Synced commands: {all_commands}')
        embed = discord.Embed(title='Sync Complete', description='The bot has been synced successfully.', color=discord.Color.green())
        embed.add_field(name='**SYNCED COMMANDS**', value=f"Synced {len(synced)} command groups")
        embed.add_field(name='*GROUPS SYNCED*', value=f"Synced commands: {all_commands}")
        await ctx.send(embed=embed)

    @commands.command(name='clear', description='Clears all commands from the tree', hidden=True)
    @commands.is_owner()
    async def clear(self, ctx) -> None:
        ctx.bot.tree.clear_commands(guild=None)
        await ctx.send('Commands cleared.')

    async def cycle(self):
        while True:
            presences = [
                discord.Activity(type=discord.ActivityType.listening, name="your commands"),
                discord.Activity(type=discord.ActivityType.watching, name="your messages"),
                discord.Activity(type=discord.ActivityType.listening, name=f"to {len(self.bot.guilds)} servers"),
                discord.Activity(type=discord.ActivityType.listening, name="your messages"),
                discord.Activity(type=discord.ActivityType.watching, name=f"over {len(self.bot.guilds)} servers"),
                discord.Activity(type=discord.ActivityType.listening, name="your messages"),
                discord.Activity(type=discord.ActivityType.watching, name=f"over {len(self.bot.users)} users"),
                discord.Activity(type=discord.ActivityType.listening, name=f"{len(self.bot.users)} users")
            ]
            Statuses = [discord.Status.online, discord.Status.idle, discord.Status.do_not_disturb]
            Activity= random.choice(presences)
            Status = random.choice(Statuses)
            await self.bot.change_presence(activity=Activity, status=Status)
            print(f'Changed status to {Activity} {Status}')
            await asyncio.sleep(3600)
            
    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print(f'Logged in as {self.bot.user.name} (ID: {self.bot.user.id})')
        self.bot.loop.create_task(self.cycle())

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if ctx.guild.id not in allowed_guilds and isinstance(error, commands.NotOwner):
            print(f"Error: this user tried to use an owner command in another guild {ctx.author.name} in {ctx.guild.name}:{ctx.guild.id}")
            return
        if ctx.guild.id not in allowed_guilds:
            print(f"Error: this user tried to use a command in another guild {ctx.author.name} in {ctx.guild.name}:{ctx.guild.id}")
            return
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f"Invalid command. Type `!wchelp` for a list of available commands.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have the required permissions to use this command.")
        elif isinstance(error, commands.NotOwner):
            print(f"Error: this user tried to use an owner command {ctx.author.name}")
            await ctx.send("You cannot use this command because you are not the owner of this bot.")
        
async def setup(bot) -> None:
    await bot.add_cog(SyncCog(bot))


import discord
import datetime
import requests
from discord.ext import commands
from discord.commands import slash_command
from dotenv import load_dotenv
import aiosqlite


class Mod(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def made_backup(self, ctx):
        await ctx.send("Making the backup...")
        async with aiosqlite.connect("backup.db") as db:
            # Create backup table for channels
            await db.execute("CREATE TABLE IF NOT EXISTS channel_backup (category TEXT, channel TEXT, channel_id TEXT, channel_type TEXT)")
            await db.commit()

            # Backup channels
            for channel in ctx.guild.channels:
                try:
                    await db.execute("INSERT INTO channel_backup VALUES (?,?,?,?)", (str(channel.category.name), str(channel.name), int(channel.id), str(channel.type)))
                    await db.commit()
                except:
                    pass

            # Create backup table for roles
            await db.execute("CREATE TABLE IF NOT EXISTS role_backup (role_id TEXT, role_name TEXT, color INTEGER, permissions INTEGER, position INTEGER)")
            await db.commit()

            # Backup roles
            for role in ctx.guild.roles:
                if role.name != "@everyone":
                    await db.execute("INSERT INTO role_backup VALUES (?,?,?,?,?)", (int(role.id), role.name, role.color.value, role.permissions.value, role.position))
                    await db.commit()

            await ctx.send("Backup complete.")
            

              

    
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def restore(self, ctx):
        async with aiosqlite.connect("backup.db") as db:
            # Restore channels
            channel_rows = await db.execute("SELECT * FROM channel_backup")
            channel_rows = await channel_rows.fetchall()
            for row in channel_rows:
                try:
                    category_name, channel_name, channel_id, channel_type = row
                    category = discord.utils.get(ctx.guild.categories, name=category_name)
                    if category is None:
                        category = await ctx.guild.create_category(category_name)
                    if channel_type == "text":
                        await category.create_text_channel(channel_name, position=0)
                    elif channel_type == "voice":
                        await category.create_voice_channel(channel_name, position=0)
                except: 
                    pass

            # Restore roles
            role_rows = await db.execute("SELECT * FROM role_backup")
            role_rows = await role_rows.fetchall()
            for row in role_rows:
                try:
                    role_id, role_name, color, permissions, position = row
                    role = discord.utils.get(ctx.guild.roles, id=int(role_id))
                    if role is None:
                        role = await ctx.guild.create_role(id=int(role_id), name=role_name, color=discord.Color(color), permissions=discord.Permissions(permissions), position=position)
                    else:
                        await role.edit(name=role_name, color=discord.Color(color), permissions=discord.Permissions(permissions), position=position)
                except:
                    pass


        await ctx.send("Restore complete.")
        await ctx.send("Backup data has been restored. All hail lord tea for saving our asses")



def setup(client):
    client.add_cog(Mod(client))
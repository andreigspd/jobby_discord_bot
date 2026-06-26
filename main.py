import discord
import os
import datetime
import logging
import asyncio
from discord.ext import commands, tasks
from dotenv import load_dotenv

# Import database and scraper modules
from database import (
    init_db, add_job
)
from scraper import scrape_linkedin_jobs

# Initialize database
init_db()

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# Logging configuration
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  

bot = commands.Bot(command_prefix=['/'], intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_member_join(member):
    await member.send(f'Hello {member.name}, welcome to the server!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Existing moderation functionality
    if "shit" in message.content.lower():
        await message.delete()
        await message.channel.send(f" {message.author.mention} Please watch your language!")

    await bot.process_commands(message)

# --- Background Task ---


# --- Commands ---

@bot.command(name='search')
async def search(ctx, keywords: str, location: str):
    message = await ctx.send(f'Searching for jobs with keywords "{keywords}" in location "{location}"...')
    jobs = scrape_linkedin_jobs(keywords, location)
    await message.delete()
    if not jobs:
        await ctx.send(f'No jobs found for keywords "{keywords}" in location "{location}".')
        return
    await ctx.send(f'Found {len(jobs)} jobs for keywords "{keywords}" in location "{location}".')
    for job in jobs:
        embed = discord.Embed(
                title=f"💼 {job['title']}",
                url=job['link'],
                color=discord.Color.from_rgb(0, 119, 181),
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
        embed.add_field(name="Company", value=f"🏢 {job['company']}", inline=True)
        embed.add_field(name="Location", value=f"📍 {job['location']}", inline=True)
        embed.add_field(name="Posted", value=f"📅 {job['post_date']}", inline=True)
        embed.set_footer(text=f"Search Query: {keywords} in {location}")

        await ctx.send(embed=embed)
        await asyncio.sleep(1)  # Sleep for 1 second between messages to avoid rate limits

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
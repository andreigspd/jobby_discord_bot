import discord
import os
import datetime
import logging
import asyncio
from discord.ext import commands, tasks
from dotenv import load_dotenv

from database import (
    init_db, is_job_added, add_job,
    save_active_search, get_active_searches,
    toggle_job_selection, get_job_statuses
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

bot = commands.Bot(command_prefix=['!', '/'], intents=intents)

# --- Interactive View (Buttons) ---

class JobView(discord.ui.View):
    def __init__(self, job_id: str):
        super().__init__(timeout=None)
        self.job_id = job_id

    def _build_footer_text(self):
        statuses = get_job_statuses(self.job_id)
        selected_users = [s['user_name'] for s in statuses if s['status'] == "Selectat"]
        applied_users = [s['user_name'] for s in statuses if s['status'] == "Aplicat"]
        
        footer_parts = []
        if selected_users:
            footer_parts.append(f"📌 Selectat de: {', '.join(selected_users)}")
        if applied_users:
            footer_parts.append(f"✅ Aplicat de: {', '.join(applied_users)}")
            
        return " | ".join(footer_parts) if footer_parts else "Nicio selecție încă"

    @discord.ui.button(label="Selectează", style=discord.ButtonStyle.primary, emoji="📌")
    async def select_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        new_status = toggle_job_selection(self.job_id, user.id, user.name, "Selectat")
        
        embed = interaction.message.embeds[0]
        footer_text = self._build_footer_text()
        embed.set_footer(text=footer_text)
        
        if new_status == "Selectat":
            await interaction.response.send_message(f"📌 Ai selectat jobul: **{embed.title}**", ephemeral=True)
        else:
            await interaction.response.send_message(f"ℹ️ Ai deselectat jobul: **{embed.title}**", ephemeral=True)
            
        await interaction.message.edit(embed=embed, view=self)

    @discord.ui.button(label="Aplicat", style=discord.ButtonStyle.success, emoji="✅")
    async def apply_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        new_status = toggle_job_selection(self.job_id, user.id, user.name, "Aplicat")
        
        embed = interaction.message.embeds[0]
        footer_text = self._build_footer_text()
        embed.set_footer(text=footer_text)
        
        if new_status == "Aplicat":
            await interaction.response.send_message(f"✅ Ai marcat că ai aplicat la: **{embed.title}**", ephemeral=True)
        else:
            await interaction.response.send_message(f"ℹ️ Ai eliminat marcatul de Aplicat la: **{embed.title}**", ephemeral=True)
            
        await interaction.message.edit(embed=embed, view=self)

# --- Bot Events ---

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    if not auto_update_task.is_running():
        auto_update_task.start()
        print("Background auto-update loop started (checking every 15 mins).")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Basic language moderation
    if "shit" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} Te rugăm să păstrezi un limbaj adecvat!")

    await bot.process_commands(message)

# --- Background Auto-Update Task ---

@tasks.loop(minutes=15)
async def auto_update_task():
    """Checks LinkedIn for new jobs across registered active searches."""
    active_searches = get_active_searches()
    if not active_searches:
        return

    print(f"Running auto-update scan for {len(active_searches)} search queries...")
    for search in active_searches:
        channel_id = search['channel_id']
        keywords = search['keywords']
        location = search['location']
        
        channel = bot.get_channel(channel_id)
        if not channel:
            continue
            
        jobs = scrape_linkedin_jobs(keywords, location, limit=10)
        new_jobs = []
        
        for job in jobs:
            if job['job_id'] and not is_job_added(job['job_id']):
                add_job(job['job_id'], job['title'], job['company'], job['location'], job['post_date'], job['link'])
                new_jobs.append(job)
                
        if new_jobs:
            print(f"Auto-update: Found {len(new_jobs)} new jobs for channel {channel_id} ('{keywords}' in '{location}')")
            for job in new_jobs:
                embed = discord.Embed(
                    title=f"💼 {job['title']}",
                    url=job['link'],
                    description="🔔 **Job nou găsit!**",
                    color=discord.Color.from_rgb(0, 119, 181),
                    timestamp=datetime.datetime.now(datetime.timezone.utc)
                )
                embed.add_field(name="Companie", value=f"🏢 {job['company']}", inline=True)
                embed.add_field(name="Locație", value=f"📍 {job['location']}", inline=True)
                embed.add_field(name="Postat", value=f"📅 {job['post_date']}", inline=True)
                embed.set_footer(text="Nicio selecție încă")
                
                view = JobView(job_id=job['job_id'])
                await channel.send(embed=embed, view=view)
                await asyncio.sleep(1)

@auto_update_task.before_loop
async def before_auto_update():
    await bot.wait_until_ready()

# --- Simplified Search Command ---

@bot.command(name='search')
async def search(ctx, keywords: str, location: str):
    """
    Caută joburi pe LinkedIn după cuvinte cheie și locație.
    Setează totodată canalul pentru notificări automate când apar joburi noi.
    """
    msg = await ctx.send(f"🔍 Caut joburi pentru **\"{keywords}\"** în **\"{location}\"**...")
    
    # Save active search query for auto-updates in this channel
    save_active_search(ctx.channel.id, keywords, location)
    
    jobs = scrape_linkedin_jobs(keywords, location, limit=10)
    await msg.delete()
    
    if not jobs:
        await ctx.send(f"❌ Nu am găsit joburi pentru **\"{keywords}\"** în **\"{location}\"**.")
        return
        
    await ctx.send(f"✅ Am găsit {len(jobs)} joburi pentru **\"{keywords}\"** în **\"{location}\"**. Notificările automate pentru acest canal au fost de asemenea activate!")
    
    for job in jobs:
        # Save to database if new
        if job['job_id']:
            add_job(job['job_id'], job['title'], job['company'], job['location'], job['post_date'], job['link'])
            
        embed = discord.Embed(
            title=f"💼 {job['title']}",
            url=job['link'],
            color=discord.Color.from_rgb(0, 119, 181),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.add_field(name="Companie", value=f"🏢 {job['company']}", inline=True)
        embed.add_field(name="Locație", value=f"📍 {job['location']}", inline=True)
        embed.add_field(name="Postat", value=f"📅 {job['post_date']}", inline=True)
        embed.set_footer(text="Nicio selecție încă")
        
        view = JobView(job_id=job['job_id'])
        await ctx.send(embed=embed, view=view)
        await asyncio.sleep(1)

# Run bot
if __name__ == "__main__":
    if not token:
        print("ERROR: DISCORD_TOKEN missing in .env file.")
    else:
        bot.run(token, log_handler=handler, log_level=logging.DEBUG)
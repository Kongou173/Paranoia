import os
import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import timedelta
import asyncio
from keep_alive import keep_alive

# Botの初期設定
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # banやkickで必要
bot = commands.Bot(command_prefix="!", intents=intents)

# ステータス表示（presence）
@tasks.loop(seconds=20)
async def presence_loop():
    game = discord.Game("/help - Bot Help")
    await bot.change_presence(activity=game)

# コマンドの同期が一度だけ行われるように制御するためのフラグ
synced = False

# Bot起動時の処理
@bot.event
async def on_ready():
    global synced
    if not synced:
        await bot.tree.sync()  # スラッシュコマンドの同期
        synced = True  # 同期済みフラグを設定
        print("スラッシュコマンドを同期しました。")
    print(f"Logged in as {bot.user.name}")
    presence_loop.start()

# /help コマンド：利用可能なコマンド一覧を表示
@bot.tree.command(
    name="help",
    description="利用可能なコマンド一覧を表示します"
)
async def bot_help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="ボットの使い方", color=discord.Colour.blurple()
    ).add_field(name="/help", value="利用可能なコマンド一覧を表示します") \
     .add_field(name="/ban <user>", value="ユーザーをBANします") \
     .add_field(name="/kick <user>", value="ユーザーをキックします") \
     .add_field(name="/timeout <user> <duration>", value="指定された時間だけユーザーをタイムアウトします (1分〜1時間)")
    
    await interaction.response.send_message(embed=embed)

# /ban コマンド：ユーザーをBAN
@bot.tree.command(name="ban", description="ユーザーをBANします")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    if interaction.user.guild_permissions.ban_members:
        await member.ban(reason=reason)
        await interaction.response.send_message(f"{member.mention} をBANしました。")
    else:
        await interaction.response.send_message("BAN権限がありません。", ephemeral=True)

# /kick コマンド：ユーザーをキック
@bot.tree.command(name="kick", description="ユーザーをキックします")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    if interaction.user.guild_permissions.kick_members:
        await member.kick(reason=reason)
        await interaction.response.send_message(f"{member.mention} をキックしました。")
    else:
        await interaction.response.send_message("キック権限がありません。", ephemeral=True)

# /timeout コマンド：ユーザーをタイムアウト
@bot.tree.command(name="timeout", description="指定時間だけユーザーをタイムアウトします")
async def timeout(interaction: discord.Interaction, member: discord.Member, duration: int):
    if interaction.user.guild_permissions.moderate_members:
        if 1 <= duration <= 60:
            timeout_duration = discord.utils.utcnow() + timedelta(minutes=duration)
            await member.timeout(timeout_duration)
            await interaction.response.send_message(f"{member.mention} を {duration} 分間タイムアウトしました。")
        else:
            await interaction.response.send_message("タイムアウトの時間は1分〜60分の範囲で指定してください。", ephemeral=True)
    else:
        await interaction.response.send_message("タイムアウト権限がありません。", ephemeral=True)

# Botを実行
keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))

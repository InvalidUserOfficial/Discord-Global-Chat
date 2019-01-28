import discord
from discord.ext import commands
import configparser
import signal, os, sys
import random
	
config = configparser.ConfigParser()
config.read("./config.ini")

token = config["Tokens"]["bot"]
owner = config["Tokens"]["owner"]
channel_ids = config["Channels"]["globals"].split(",")
global_channels = {}
prefix = config["Settings"]["prefix"]

Client = discord.Client()
client = commands.Bot(command_prefix=prefix, owner_id=owner)


def handler(signum, frame):
	client.close()
	print("Bot logged out!")
	sys.exit()

def init_channels():
	for channel_id in channel_ids:
		if client.get_channel(channel_id) != None:
			global_channels[client.get_channel(channel_id).server.id] = [channel_id, "ONLINE"]

@client.event
async def on_message(message):
	sid = message.server.id
	cid = message.channel.id
	if message.content.startswith(prefix):
		await client.process_commands(message)
	elif message.author.id != client.user.id and cid == global_channels[sid][0]:
		for server_id, pair in global_channels.items():
			if pair[1] == "ONLINE":
				await client.send_message(client.get_channel(pair[0]), "{}, {}: {}".format(
					message.author.name, message.server.name, message.content))

@client.event
async def on_ready():
	init_channels()
	print("Bot logged in!")

@client.command(pass_context=True)
async def globalize(ctx):
	sid = ctx.message.server.id
	cid = ctx.message.channel.id
	if ctx.message.author.server_permissions.administrator == True:
		global_channels[sid] = [client.get_channel(cid).id, "ONLINE"]
		cname = client.get_channel(global_channels[sid][0]).name
		await client.send_message(ctx.message.channel, "Set global channel to **{}**".format(cname))

@client.command(pass_context=True)
async def mute(ctx):
	sid = ctx.message.server.id
	if ctx.message.author.server_permissions.administrator == True:
		global_channels[sid][1] = "OFFLINE"
		cname = client.get_channel(global_channels[sid][0]).name
		await client.send_message(ctx.message.channel, "Muted **{}**".format(cname))

@client.command(pass_context=True)
async def unmute(ctx):
	sid = ctx.message.server.id
	if ctx.message.author.server_permissions.administrator == True:
		global_channels[sid][1] = "ONLINE"
		cname = client.get_channel(global_channels[sid][0]).name
		await client.send_message(ctx.message.channel, "Unmuted **{}**".format(cname))

@client.command(pass_context=True)
async def status(ctx):
	embed = discord.Embed(colour = discord.Colour.gold())
	
	embed = embed.add_field(name="Server Name", value="\u200b", inline=True)
	embed = embed.add_field(name="Channel Name", value="\u200b", inline=True)
	embed = embed.add_field(name="Status", value="\u200b", inline=True)

	for sid, details in global_channels.items():
		sname = client.get_server(sid)
		cname = client.get_channel(details[0])
		status = details[1]
		embed = embed.add_field(name="\u200b", value=sname, inline=True)
		embed = embed.add_field(name="\u200b", value=cname, inline=True)
		embed = embed.add_field(name="\u200b", value=status, inline=True)
	
	await client.send_message(ctx.message.channel, embed=embed)

# utility commands below

# Will purge an entire channel's messages
@client.command(pass_context=True)
async def purge(ctx):
	if ctx.message.author.server_permissions == True:
		if client.user.server_permissions.administrator == True:
			deleted = await client.purge_from(ctx.message.channel, check=None)
			await client.send_message(ctx.message.channel, "Deleted {} message(s)".format(len(deleted)))
		else:
			await client.send_message(ctx.message.channel, "Need *Manage Messages* permission for this feature")

# Will create randomized teams based off of players in same voice channel as user
# !genteam <# of teams> <voice channel id>
@client.command(pass_context=True)
async def genteam(ctx):
	args = ctx.message.content.split(" ")[1:3]
	team_count = int(args[0])
	channel_id = args[1]

	if client.get_channel(args[1]).type == discord.ChannelType.voice:
		users = client.get_channel(channel_id).voice_members
		random.shuffle(users)
		for i in range(len(users)):
			if int(i / team_count) == 0:
				await client.send_message(ctx.message.channel, "Team {}: " .format(i % team_count + 1))
			await client.send_message(ctx.message.channel, users[i].name)
	else: 
		await client.send_message(ctx.message.channel, "You are not in a voice channel")

signal.signal(signal.SIGINT, handler)
client.run(token)

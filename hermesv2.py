import discord
from discord.ext import commands
import configparser
import sys

discription = ""
defualt_prefix = "!"

config = configparser.ConfigParser()
config.read("./config.ini")

# Check to see if bot token and owner id are defined before proceeding
if "owner" not in config["Tokens"] or "bot" not in config["Tokens"]:
	print("Make sure bot token AND owner id are defined!")
	sys.exit()

# Check to see if a token is defined or else just set the default token
if "prefix" in config["Settings"]:
	command_prefix = config["Settings"]["prefix"]
else:
	command_prefix = default_prefix

channel_ids = config["Channels"]["globals"].split(",")
global_dict = {}
channel_status = {}
Client = discord.Client()
client = commands.Bot(command_prefix = command_prefix, discription = discription)
admin_role = "@everyone"

@client.event
async def on_ready():
	for channel in channel_ids:
		if client.get_channel(channel) != None:
			global_dict[client.get_channel(channel).server.id] = channel
			channel_status[channel] = "ONLINE"
		else:
			print("Not a valid channel id: " + channel)
	print("Bot ready")
	print("Prefix: " + command_prefix)

######################## OWNER ONLY COMMANDS ########################

owner_cmds = ["role"]

@client.command(pass_context = True)
async def role(ctx):
	if ctx.message.author.id == config["Tokens"]["owner"]:
		admin_role = ctx.message.content

#####################################################################

######################## ADMIN ONLY COMMANDS ########################

admin_cmds = ["globalize", "mute", "unmute"]

# add current channel to global_dict
@client.command(pass_context = True)
async def globalize(ctx):
	if admin_role in [role.name for role in ctx.message.author.roles]:
		global_dict[ctx.message.server.id] = ctx.message.channel.id
	await client.send_message(ctx.message.channel, "Made **" + ctx.message.channel.name + "** the global channel.")

@client.command(pass_context = True)
async def mute(ctx):
	if admin_role in [role.name for role in ctx.message.author.roles]:
		channel_status[global_dict[ctx.message.server.id]] = "OFFLINE"

@client.command(pass_context = True)
async def unmute(ctx):
	if admin_role in [role.name for role in ctx.message.author.roles]:
		channel_status[global_dict[ctx.message.server.id]] = "ONLINE"

#####################################################################

######################## GENERAL COMMANDS ###########################

everyone_cmds = ["cmd", "show"] 

@client.command(pass_context = True)
async def cmd(ctx):
	embed = discord.Embed(colour = discord.Colour.gold())
	embed.add_field(name="Owner", value=owner_cmds, inline=True)
	embed.add_field(name="Admin", value=admin_cmds, inline=True)
	embed.add_field(name="Everyone", value=everyone_cmds, inline=True)
	await client.send_message(ctx.message.channel, embed=embed)

@client.command(pass_context = True)
async def show(ctx):
	embed = discord.Embed(colour = discord.Colour.orange())
	online = []
	offline = []
	embryo = []
	for key, value in global_dict.items():
		if channel_status[value] == "ONLINE":
			online.append(client.get_channel(value).name + ", " + client.get_channel(value).server.name)
		elif channel_status[value] == "OFFLINE":
			offline.append(client.get_channel(value).name + ", " + client.get_channel(value).server.name)
		else:
			embryo.append(client.get_channel(value).name + ", " + client.get_channel(value).server.name)

	embed.add_field(name="Online Channels", value=online, inline=False)
	embed.add_field(name="Offline Channels", value=offline, inline=False)	
	embed.add_field(name="Embryo Channels", value=embryo, inline=False)

	await client.send_message(ctx.message.channel, embed=embed)

#####################################################################


client.run(config["Tokens"]["bot"])

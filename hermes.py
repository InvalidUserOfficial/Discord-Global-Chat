import discord
from discord.ext import commands
import asyncio
import configparser

config = configparser.ConfigParser()
config.read('./config.ini')

#error check if bot token is defined
#error check if owner token is defined
#error check if prefix is defined
#set a default for game
#set a default for status

Client = discord.Client()
client = commands.Bot(command_prefix = config['Settings']['prefix'])
global_id_list = []

@client.event
async def on_ready():
	print("Wings Are Warmed Up, For I Am %s" % client.user.name)

#need filter out bot commands and bot output
@client.event
async def on_message(message):
	if message.content.startswith(config['Settings']['prefix']):
		await client.process_commands(message)
	elif message.author != client.user and message.channel.name == "global":
		for global_id in global_id_list:
			if message.channel != client.get_channel(global_id):
				await client.send_message(client.get_channel(global_id), '{}, {}: {}'.format( message.author.name,
				message.server.name, message.content))

#retrieve the global channels of all the servers the bot is registered to
#THIS IS CASE SENSITIVE TO: global, AT THE MOMENT 
@client.command(pass_context=True)
async def scan(ctx):
	for server in client.servers:
		for channel in server.channels:
			if channel.name == 'global' and channel.id not in global_id_list:
				global_id_list.append(channel.id)
	for global_id in global_id_list:
		if client.get_channel(global_id) == None:
			print(global_id)
			global_id_list.remove(global_id)
	print(global_id_list)

@client.command(pass_context=True)
async def who(ctx):
	for global_channel_id in global_id_list:
		await client.send_message(ctx.message.channel, '{} : {}'.format((client.get_channel(global_channel_id)).server.name,
		client.get_channel(global_channel_id)))		

@client.command(pass_context=True)
async def purge(ctx):
	deleted = await client.purge_from(ctx.message.channel, check=None)
	await client.send_message(ctx.message.channel, 'Deleted {} message(s)'.format(len(deleted)))

@client.command(pass_context=True)
async def servers(ctx): 
	for server in client.servers:
		await client.send_message(ctx.message.channel, "Name: {}, Region: {}, ID: {}".format(server.name, server.region,
		server.id))

@client.command(pass_context=True)
async def loli(ctx):
	await client.send_message(ctx.message.channel,
	"http://i0.kym-cdn.com/entries/icons/original/000/019/571/dailystruggg.jpg")

client.run(config["Tokens"]["bot"])

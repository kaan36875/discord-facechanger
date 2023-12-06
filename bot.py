import discord
from discord import app_commands
from discord.ext import commands
import json
from environs import Env
import image_synth


with open('config.json') as file:
    data = json.load(file)

with open('userdata.json', 'r') as json_file:
    userdata = json.load(json_file)

env = Env()
env.read_env()
bot = commands.Bot(command_prefix="!", intents= discord.Intents.all())
image_synth.bot = bot

#=======================
# Verification
#=======================
async def VerifyParameters(interaction):
    parameters = {
        'channel_id':interaction.channel.id,
        'user_id':interaction.user.id
    }
    return parameters

async def VerifyAttachment(interaction, face, image):
    
    valid_extensions = ['jpg','jpeg','png']

    file_extension = str(face.filename).split(".")
    file_extension2 = str(image.filename).split(".")
    if(file_extension[-1] not in valid_extensions):
        print('Invalid attachment type')
        await interaction.response.send_message('File type you sent is not supported. Supported file types: **JPG, JPEG, PNG**')
        return False
    if(file_extension2[-1] not in valid_extensions):
        print('Invalid attachment type')
        await interaction.response.send_message('File type you sent is not supported. Supported file types: **JPG, JPEG, PNG**')
        return False
    return True

#=======================
# Deepface Command
#=======================
@bot.tree.command(name="deepface", description="Changes the face of the picture.")
@app_commands.describe(face="The face picture that you want to copy.", image="The image that you want to change the face.")
async def deepface(interaction: discord.Interaction, face: discord.Attachment, image: discord.Attachment):
    user_id = str(interaction.user.id)
    channel_id = interaction.channel.id  

    # Check user in database, if not add it and give starting credits
    if user_id not in userdata:              
        userdata[user_id] = data["start-credits"]
        with open('userdata.json', 'w') as json_file:
            json.dump(userdata, json_file, indent=4)
        json_file.close()
    
    if channel_id == data["channel-id"] or data["channel-id"] == 0:
        if userdata[user_id] > 0:
            conversion_parameters = await VerifyParameters(interaction)
            valid_attachment = await VerifyAttachment(interaction,face,image)

            if(conversion_parameters != False and valid_attachment == True):
                userdata[user_id] -= 1
                with open('userdata.json', 'w') as json_file:
                    json.dump(userdata, json_file, indent=4)
                await interaction.response.send_message('Your photo added to the queue. **Credits left: ' + str(userdata[user_id]) + '**')
                await image_synth.ImageConversion(interaction,conversion_parameters,face,image)
        else:
            await interaction.response.send_message('Not enough credits.',ephemeral=True)
    else:
        await interaction.response.send_message("You can't use the bot in this channel.",ephemeral=True)
    
@deepface.error
async def deepface_error(interaction: discord.Interaction, error):
    print(error)


#=======================
# Bot Online
#=======================
@bot.event
async def on_ready():
    print("Bot is ready")
    try:
        bot.loop.create_task(image_synth.CheckForUploads())
        bot.tree.copy_global_to(guild=discord.Object(id=data['server-id']))
        synced = await bot.tree.sync(guild=discord.Object(id=data['server-id']))
        await bot.change_presence(activity=discord.Game(name=f"No images in queue!"))
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

bot.run(data["token"])

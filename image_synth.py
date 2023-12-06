import discord
from discord.ext import tasks
import os
import asyncio
import json
from random import randint


image_queue = 0
bot = None

conversion_queue = []

unprocessed_photo_directory = "discord/unprocessed-photo/"
unprocessed_directory = "discord/unprocessed/"
processed_directory = 'discord/processed/'

with open('config.json') as json_file:
    config = json.load(json_file)

#=================================================================
# Check if there any files in the processed directory for upload
#=================================================================
@tasks.loop(seconds=4)
async def CheckForUploads():
    while True:
        await asyncio.sleep(10)
        directory_contents = os.listdir(processed_directory)
        if(len(directory_contents) > 0):
            print('Found files to upload')
            await UploadProcessedAudioFiles(directory_contents)

async def ImageConversion(interaction,conversion_parameters,face,image):
    await DownloadUnprocessedImageFile(interaction, conversion_parameters,face,image)

#======================================
# Update bot status with queue length
#======================================
async def updateStatus(que):
    if que == 0:
        await bot.change_presence(activity=discord.Game(name=f"No images in queue!"))
    else:
        await bot.change_presence(activity=discord.Game(name=f"⏳ {que} images in queue"))

#======================================
# Download the images of user sent
#======================================
async def DownloadUnprocessedImageFile(interaction, conversion_parameters,face,image):
        global image_queue
        filename0 = face.filename.split('.')
        filename0 = filename0[0] + "_" + str(randint(0,999)) + "." + filename0[1]

        filename1 = image.filename.split('.')
        filename1 = filename1[0] + "_" + str(randint(0,999)) + "." + filename1[1]
        try:
            image_queue += 1
            await updateStatus(image_queue)
            print('Attempting download of' + face.filename + " and " + image.filename)
            await face.save(unprocessed_directory + filename0)
            await image.save(unprocessed_photo_directory + filename1)
            GenerateConversionDetails(conversion_parameters,filename0,filename1,)
        except Exception as e:
            print(e)
            return False

#================================================
# Generate a json file with the given parameters
#================================================
def GenerateConversionDetails(conversion_parameters,filename0,filename1):
    with open(unprocessed_directory + filename0 +'.json', 'w') as f:
        conversion_parameters["image"] = filename1
        conversion_parameters["no_face"] = False
        json.dump(conversion_parameters, f)

#========================================
# Upload the final image to the channel
#========================================
async def UploadProcessedAudioFiles(directory_contents):
    global image_queue
    for file in directory_contents:
        converted_parameters = False
        file_extension = file.split('.')[-1]
        if(file_extension != 'json'):
            with open(processed_directory+file+'.json' ,'r') as parameter_file:
                converted_parameters = json.load(parameter_file)
            parameter_file.close()

            if(converted_parameters != False):
                attachment = discord.File(processed_directory + file)
                channel = bot.get_channel(converted_parameters['channel_id'])
                user = await bot.fetch_user(converted_parameters['user_id'])
                noface = converted_parameters['no_face']
                if noface:
                    with open('userdata.json', 'r') as f:
                        userdata = json.load(f)
                    await channel.send(user.mention + "Couldn't find the face in the image you sent. Credit refunded.")
                    userdata[str(converted_parameters['user_id'])] += 1
                    with open('userdata.json', 'w') as f:
                        json.dump(userdata, f, indent=4)
                    f.close()
                else:
                    await channel.send(user.mention + " Here is your face cloned picture." + "", file=attachment)
                os.remove(processed_directory + file)
                os.remove(processed_directory + file + '.json')
                image_queue -= 1
                await updateStatus(image_queue)
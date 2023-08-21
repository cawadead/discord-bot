# This is a sample Python script.
import random
import time
import warnings
import threading
warnings.filterwarnings("ignore")
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
SP_TYPES = ['euler_a', 'heun']
MD_TYPES = ['dreamshaper_331BakedVae', 'deliberate_v2', 'CounterfeitV25_25', 'v2-1_768-nonema-pruned']


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    import discord
    import requests
    import json
    from discord.ext import commands
    import asyncio
    import re
    import base64
    import os

    config = {
        'token': '',
        'prefix': '$',
    }

    bot = commands.Bot(intents=discord.Intents.all(), command_prefix=config['prefix'])

    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user} (ID: {bot.user.id})')
        print('------')


    @bot.event
    async def on_message(ctx):
        if ctx.author != bot.user:
            if ctx.content[:5] == '$img ':
                msg = ctx.content[5:]

                match_sp = re.search(r'--sp \w+', msg)
                match_md = re.search(r'--md \w+', msg)
                match_ar = re.search(r'--ar \d:\d+', msg)
                match_nsfw = re.search(r'--nsfw', msg)

                match_anime = re.search(r'anime', msg)

                sp = match_sp[0].split(' ')[1] if match_sp else 'euler_a'
                md = match_md[0].split(' ')[1] if match_md else 'dreamshaper_331BakedVae'
                ar = match_ar[0].split(' ')[1] if match_ar else '1:1'
                #block_nsfw = False if match_nsfw else True
                block_nsfw = False
                if sp not in SP_TYPES:
                    sp = SP_TYPES[0]
                if md not in MD_TYPES:
                    md = MD_TYPES[0]
                if ar == '1:2':
                    width = 512
                    height = 1024
                elif ar == '2:1':
                    width = 1024
                    height = 512
                else:
                    width = 1024
                    height = 1024

                msg = msg.replace(match_sp[0], '') if match_sp else msg
                msg = msg.replace(match_md[0], ' ') if match_md else msg
                msg = msg.replace(match_ar[0], ' ') if match_ar else msg
                msg = msg.replace(match_nsfw[0], ' ') if match_nsfw else msg
                while "  " in msg:
                    msg = msg.replace("  ", " ")

                if sp == 'heun':
                    steps = 30
                else:
                    steps = 75

                upscaler = 'RealESRGAN_x4plus_anime_6B' if match_anime else 'RealESRGAN_x4plus'
                session_id = str(random.randint(1000000000000, 2000000000000))
                print('sid: ', session_id)
                headers = {
                    'Accept': '*/*',
                    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Connection': 'keep-alive',
                    'Content-Type': 'application/json',
                    'Origin': 'http://localhost:9000',
                    'Referer': 'http://localhost:9000/',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-origin',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
                    'X-KL-Ajax-Request': 'Ajax_Request',
                    'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                }

                json_data = {
                    'prompt': msg,
                    'seed': random.randint(1, 10000000),
                    'used_random_seed': True,
                    'negative_prompt': '',
                    'num_outputs': 1,
                    'num_inference_steps': steps,
                    'guidance_scale': 7.5,
                    'width': width,
                    'height': height,
                    'vram_usage_level': 'balanced',
                    'use_stable_diffusion_model': md, #deliberate_v2 dreamshaper_331BakedVae
                    'use_vae_model': '',
                    'stream_progress_updates': True,
                    'stream_image_progress': False,
                    'show_only_filtered_image': True,
                    'block_nsfw': block_nsfw,
                    'output_format': 'jpeg',
                    'output_quality': 75,
                    'metadata_output_format': 'none',
                    'original_prompt': msg,
                    'active_tags': [],
                    'inactive_tags': [],
                    'sampler_name': sp, #heun euler_a
                    'session_id': session_id,
                }

                req = requests.post('http://localhost:9000/render', headers=headers, json=json_data)
                req.close()
                print(req.status_code)
                print('----')
                if (req.status_code == 200):
                    processing_reply = await ctx.reply("Обработка")
                    task_id = (str(req.json()['task']))
                    stream_img = req.json()['stream']
                    while True:
                        await bot.change_presence(activity=discord.Game(name="тужится"))
                        await asyncio.sleep(10)
                        req2 = requests.get('http://localhost:9000/ping?session_id=' + session_id)
                        req2.close()
                        print(req2.status_code)
                        print(req2.json()['tasks'][task_id])
                        print(task_id)
                        print('   ')
                        if req2.json()['tasks'][task_id] == "buffer":
                            await asyncio.sleep(5)
                            url_req3 = 'http://localhost:9000/image/stream/' + task_id
                            print('urlreq3 ', url_req3)
                            req3 = requests.get(url_req3)
                            req3.close()
                            match = re.search(r'"data:image.*",', req3.text)
                            url = match[0] if match else 'Not found'
                            url = url[24:-2]
                            image_code = base64.b64decode(url.replace("\n", ""))
                            with open('output_images/'+task_id+".png", "wb") as fh:
                                fh.write(image_code)
                            with open('output_images/'+task_id+".png", 'rb') as fh:
                                #await ctx.reply(file = discord.File(fh, "SPOILER_"+task_id + ".png"))
                                a = await ctx.reply(file = discord.File(fh, task_id + ".png"))
                            await processing_reply.delete()
                            #os.remove("C:/Users/KEISER/PycharmProjects/DiscordBot/"+task_id+".png")
                            await bot.change_presence(activity=discord.Game(name="ждет"))
                            break
                        elif req2.json()['tasks'][task_id] == "completed":
                            url_req3 = 'http://localhost:9000/image/stream/' + task_id
                            print('urlreq3 ', url_req3)
                            req3 = requests.get(url_req3)
                            req3.close()
                            match = re.search(r'"data:image.*",', req3.text)
                            url = match[0] if match else 'Not found'
                            url = url[24:-2]
                            image_code = base64.b64decode(url.replace("\n", ""))
                            with open('output_images/'+task_id+".png", "wb") as fh:
                                fh.write(image_code)
                            with open('output_images/'+task_id+".png", 'rb') as fh:
                                #await ctx.reply(file=discord.File(fh, "SPOILER_"+task_id + ".png"))
                                await ctx.reply(file=discord.File(fh, task_id + ".png"))
                            #os.remove("C:/Users/KEISER/PycharmProjects/DiscordBot/"+task_id+".png")
                            await bot.change_presence(activity=discord.Game(name="ждет"))
                            print(md, upscaler, sp)
                            break
            elif ctx.content == '$help':
                await ctx.channel.send('Help\n\n'
                                'Option (aspect ratio):\n'
                                '--ar\n'
                                'Accepted values: '
                                '1:1, 1:2, 2:1\n'
                                'Example:\n'
                                '$img demon --ar 1:2\n\n'
                                
                                'Option (model):\n'
                                '--md\n'
                                'Accepted values: '
                                'deliberate_v2, dreamshaper_331BakedVae, CounterfeitV25_25, v2-1_768-nonema-pruned\n'
                                'About values\n'
                                '   deliberate_v2: good at render, photorealistic, cinematic styles\n'
                                '   dreamshaper_331BakedVae: a bit of everything\n'
                                '   CounterfeitV25_25: anime style\n'  
                                '   v2-1_768-nonema-pruned: a bit of everything\n'
                                'Example:\n'
                                '$img demon --md deliberate_v2\n\n'

                                'Option (sampler):\n'
                                '--sp\n'
                                'Accepted values: '
                                'heun, euler_a\n'
                                'Example:\n'
                                '$img demon --sp heun\n\n'
                                       
                                # 'Option (nsfw enable):\n'
                                # '--nsfw\n'
                                # 'Example:\n'
                                # '$img demon --nsfw'

                                )



    bot.run(config['token'])

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

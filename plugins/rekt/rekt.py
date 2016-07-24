from PIL import Image, ImageFont, ImageDraw
from images2gif import writeGif #rare dependency, have to search alternatives
import os, random, time, tempfile, logging

# todo: -port the script to a library other than images2gif
#            -ImageMagick seems good
#       -port debug print() calls to logging module and save them to a log file
#       -actually make it work in the bot
#            -decide if it should be used with a command+reply or with a trigger string/hashtag
#            -download replied-user's profile image
#            -send temporary-file gif
#       -optimize
#       -save binaries to some other location

def rekt(user_photo, image_size=(260, 260), number_of_frames=12, duration=0.115, dump=False):
    """"
    Parameters:
    -----------
    user_photo : PIL Image
        Image that will be rektified (the Telegram user's profile photo)
    image_size : tuple of two integers
         GIF dimensions, better keep square
    number_of_frames : integer
        number of frames to generate
    duration : float
        duration of each GIF frame
    dump : bool
        if True, dumps the generated frames to the current working directory

    """
    start = time.time()
    def proportional(n, coordinate=False):
        """ original working image_size was (640, 640) (all values are based on this).
        this just converts the number it is passed to a image_size-proportional value."""
        if coordinate == False:
            # if no coordinate is proportioned, use the minimum of the two values for calculating the output
            return round(n / 640 * min(image_size))
        return round(n / 640 * image_size[coordinate])

    rekt_image = Image.open('rekt.jpg').resize(image_size)
    user_photo = user_photo.convert('RGB').resize(image_size)


    fonts = list()

    for font in [a for a in os.listdir(os.path.join('.', 'fonts')) if a.endswith('.ttf') or a.endswith('.otf')]:
        '''if font == 'WingDings.ttf': #deprecated code, still have to make WingDings work
            fonts.append(ImageFont.truetype(font, 128, encoding='symb'))
        else:
            fonts.append(ImageFont.truetype(font, 128))'''
        fonts.append(os.path.join('.', 'fonts', '')+font)
        #print(font)

    frames_list = list()
    for a0 in range(number_of_frames):
        #blend the user photo with rekt.jpg. random opacity
        rekt_alpha = random.randint(10, 90)/100
        result_frame = Image.blend(rekt_image, user_photo, rekt_alpha)

        #blend the result_frame with some color. random opacity and color
        color_alpha = random.randint(0, 50)/100
        color = (random.randint(0,255), random.randint(0,255),\
                  random.randint(0,255))
        colorfill_image = Image.new('RGB', image_size, color)
        result_frame = Image.blend(result_frame, colorfill_image, color_alpha)

        n = random.randint(1, round(number_of_frames / 2)) #more accurate randomness
        if n == 1:
            # 2/number_of_frames or 1/n chance that there will be no strings printed on the frame
            number_of_strings = 0
        else:
            number_of_strings = random.randint(1, 6)

        for a1 in range(number_of_strings):
            #print '#REKT'. random coordinates, color, size, font, angle and opacity
            color = (random.randint(0,255), random.randint(0,255),\
                     random.randint(0,255), random.randint(100, 255)) #last value is opacity
            font_size = random.randint(proportional(100), proportional(156))
            font_index = random.randint(1, len(fonts)) - 1
            font = ImageFont.truetype(fonts[font_index], size=font_size)
            actual_font_size = font.getsize('#REKT') #(height, width) that the string occupies

            for x in actual_font_size: #prevents errors when font_size is large
                if x >= proportional(640):
                    larger = True
                    break
                else:
                    larger = False

            if not larger:
                coord = (random.randint(0, (image_size[0] - actual_font_size[0])),\
                         random.randint(0, (image_size[1] - actual_font_size[1])))
                #image_size - actual_font_size = max coords (bottom right corner)
            else:
                coord = (image_size[0], image_size[1])
            rotation = random.randint(-30, 30) #-30º to 30º


            #we print the text in a new image
            text_image = Image.new('L', image_size) #white text over black background
            d = ImageDraw.Draw(text_image)
            d.text(coord, '#REKT', fill=color, font=font) #draws the text on the image

            #color-filled image, later to be used with text_image as a layer mask:
            colorfill_image = Image.new('RGBA', image_size, color)

            #now to rotate the text and resize it:
            text_image = text_image.rotate(rotation, expand=0, resample=Image.NEAREST).resize(image_size, resample=Image.NEAREST)
            #paste the colored text to the output frame:
            result_frame.paste(colorfill_image, mask=text_image)

        #finally, we select a random square area to INTENSIFY
        x0 = random.randint(0, proportional(140, 0))
        y0 = random.randint(0, proportional(140, 1))
        x1 = x0 + proportional(500, 0)
        y1 = y0 + proportional(500, 1)
        crop_area = (x0, y0, x1, y1)
        result_frame = result_frame.crop(crop_area).resize(image_size, resample=Image.NEAREST)
        #append the final image to a list, to make a gif
        frames_list.append(result_frame)
    f = tempfile.NamedTemporaryFile(delete=False, suffix='.gif')
    writeGif(f.name, frames_list, duration=duration, repeat=True, dither=False, nq=0, subRectangles=False)

    if dump:
        for x in range(len(frames_list)): #dump frames to directory
            frames_list[x].save(os.path.join(('rekt result', 'frame-'))+str(x)+'.jpg')
    elapsed = time.time() - start
    print('[%s] Wrote gif in %s seconds. size=%s,frames=%s.' % (time.time(), elapsed, size, frames))
    file = open(f.name, 'rb')
    print('[%s] file %s: %s kB' % (time.time(), f.name, os.stat(f.name).st_size / 1024))
    return file


#Original pyTelegramBotAPI implementation:
"""
def download_image(url, params=None, headers=None):
    try:
        jstr = requests.get(url, params=params, headers=headers, stream=True)
        ext = os.path.splitext(url)[1]
        f = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
        for chunk in jstr.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    except IOError:
        return None
    f.seek(0)
    if not ext:
        f.name += '.jpg'
    file = Image.open(f.name)
    return file

@bot.message_handler(regexp=re.compile('rekt', re.I))
def pythonmessage(message):
    start = time.time()
    print('[MESSAGE]'+('['+str(time.time())+'] ')+('{'+str(message.from_user.id)+'} ')+message.text)
    reply = message.reply_to_message
    try:
        if reply:
            photo_id = bot.get_user_profile_photos(reply.from_user.id, limit=1).photos[0][1].file_id
        else: #use message user photo
            photo_id = bot.get_user_profile_photos(message.from_user.id, limit=1).photos[0][1].file_id
        photo_file_info = bot.get_file(photo_id)
        #print(      'https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, photo_file_info.file_path))
        photo_url = 'https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, photo_file_info.file_path)
        photo_file = download_image(photo_url)
    except:
        photo_file = Image.open('nophoto.png')
    print('[%s] Downloaded image in %s seconds.' %(time.time(), time.time()-start))
    r = rekt(photo_file)
    bot.send_document(message.chat.id, r, reply_to_message_id=message.message_id)
    print('[SENT FILE]'+('['+str(time.time())+'] ')+('{'+str(message.from_user.id)+'} ')+message.text)
    print('[ELAPSED] %s seconds.\n' %(time.time()-start))"""

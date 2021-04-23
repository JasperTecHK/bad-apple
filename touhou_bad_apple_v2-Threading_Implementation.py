#!/usr/bin/python3
from PIL import Image
import cv2
import sys
import time
import vlc
import os
import logging
import json
import re
import threading
from queue import Queue

ASCII_CHARS = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]

# frame_interval = 0.0329
frame_interval = 1.0 / 31
frame_size = 150

def play_video(result):
    for framescene in range(len(result)):
        start_time = time.time()
        print(str(result[framescene]))
        compute_delay = float(time.time() - start_time)
        delay_duration = frame_interval - compute_delay
        logging.info(str(delay_duration))
        if delay_duration < 0:
            delay_duration = 0
        time.sleep(delay_duration)

# Progress bar code is courtesy of StackOverflow user: Aravind Voggu.
# Link to thread: https://stackoverflow.com/questions/6169217/replace-console-output-in-python
def progress_bar(current, total, barLength=25):
    progress = float(current) * 100 / total
    arrow = '#' * int(progress / 100 * barLength - 1)
    spaces = ' ' * (barLength - len(arrow))
    sys.stdout.write('\rProgress: [%s%s] %d%% Frame %d of %d frames' % (arrow, spaces, progress, current, total)) #Interesting, print can't do this, for some reason.

def extract_resize_convert_frames(video_path, optchosen):  #Extract frame, save to queue, then ascii-fy, and save.
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # gets the total number of frames
    numthreads = min(50, total_frames)
    print("Processing frames... One moment!")
    q = Queue(maxsize=0)
    result = [{} for x in range(total_frames)]
    for i in range(1, total_frames):
        ret, frame = cap.read()
        q.put((i, frame))

    for i in range(numthreads):
        process = threading.Thread(target=asciiprocessing, args=(q, result, optchosen))
        process.setDaemon(True)
        process.start()

    progframe = total_frames - q.qsize()    #This is just for the progress bar.
    progdone = False
    while progframe <= total_frames:
        if progframe > total_frames:
            progframe = total_frames
        if progframe == total_frames:
            progdone = True

        progress_bar(progframe - 1, total_frames - 1)
        progframe = total_frames - q.qsize()

        if progdone:
            break

    q.join()
    cap.release()
    print("\nVideo processing and ascii-fication completed!\n")
    return result

def asciiprocessing(q,result, optchosen):
    while not q.empty():
        work = q.get()
        if optchosen == 1:
            result[work[0]] = ascii_generator(work[1])
        else:
            temp = ascii_generator(work[1])
            result[work[0]] = encode_to_rle(temp)
        q.task_done()
    return True


# A little note of acknowledgement to Alex1Rohwer. The following code of converting image frames into ASCII characters is not original, and is
# based off the code from https://github.com/kiteco/python-youtube-code/blob/master/ascii/ascii_convert.py. As this code repository gains more
# traction, I feel that I need to properly source the code.

# Resize image
def resize_image(image_frame):
    width, height = image_frame.size
    aspect_ratio = (height / float(width * 2.5))  # 2.5 modifier to offset vertical scaling on console
    new_height = int(aspect_ratio * frame_size)
    resized_image = image_frame.resize((frame_size, new_height))
    # print('Aspect ratio: %f' % aspect_ratio)
    # print('New dimensions %d %d' % resized_image.size)
    return resized_image


# Greyscale
def greyscale(image_frame):
    return image_frame.convert("L")

# Convert pixels to ascii
def pixels_to_ascii(image_frame):
    pixels = image_frame.getdata()
    characters = "".join([ASCII_CHARS[pixel // 25] for pixel in pixels])
    return characters

# Open image => Resize => Greyscale => Convert to ASCII => Store in memory/export
def ascii_generator(passthru):
    image_frame = Image.fromarray(passthru)     # Directly convert the image to something PIL can use, instead of an extra i/o step.
    resized_image = resize_image(image_frame)   # resize the image
    greyscale_image = greyscale(resized_image)  # convert to greyscale
    ascii_characters = pixels_to_ascii(greyscale_image)  # get ascii characters
    pixel_count = len(ascii_characters)
    ascii_image = "\n".join(                    #Can't change this, haven't the foggiest what this does for now.
        [ascii_characters[index:(index + frame_size)] for index in range(0, pixel_count, frame_size)])
    return ascii_image

def save_later(encodesource):
    with open ("BadApple.rle", "w+") as rlebackup:
        rlebackup.write(json.dumps(encodesource))

def encode_to_rle(temp):
    frameset = temp.replace("\n", "")
    lastchar = ""
    storage = ""
    charcount = 1
    for pixel in frameset:
        if pixel != lastchar:
            if lastchar:
                storage += str(charcount) + lastchar
            lastchar = pixel
            charcount = 1
        else:
            charcount += 1
    storage += str(charcount) + lastchar
    return storage

def decode_from_rle(result):
    with open(result, "r") as pregenframes:
        framesource = json.loads(pregenframes.read())
        total_frames = len(framesource)
        numthreads = min(50, total_frames)
        print("Processing frames... One moment!")
        q = Queue(maxsize=0)
        result = [{} for x in range(total_frames)]
        for i in range(len(framesource)):
            q.put((i, framesource[i]))
        for i in range(numthreads):
            process = threading.Thread(target=asciidecoding, args=(q, result))
            process.setDaemon(True)
            process.start()

        progframe = total_frames - q.qsize()    #This is just for the progress bar.
        progdone = False
        while progframe <= total_frames:
            if progframe > total_frames:
                progframe = total_frames
            if progframe == total_frames:
                progdone = True

            progress_bar(progframe - 1, total_frames - 1)
            progframe = total_frames - q.qsize()

            if progdone:
                break

        q.join()
        return result

def asciidecoding(q,result):
    while not q.empty():
        framesource = q.get()
        framecontent = framesource[1]
        frameshape = ""
        cycles = ""
        for pixel in framecontent:
            if pixel.isdigit():
                cycles += pixel
            else:
                frameshape += pixel * int(cycles)
                cycles = ""

        frameshape = re.sub("(.{150})", "\\1\n", frameshape, 0, re.DOTALL)
        result[framesource[0]] = frameshape[:-1]
        q.task_done()
    return True


def audiosource():
    while True:
        user_input = input("What is the name of the song you want to ascii-ify?")
        user_input.strip()
        if not os.file.exists(user_input):
            print("Invalid file. Please check again.")
        else:
            break
    return user_input

# Delete extracted frames and .txt files
def delete_assets():
    for index in range(1, 6572):
        # print("Deleting .txt files...")
        file_name = r"TextFiles/" + "bad_apple" + str(index) + ".txt"
        try:
            os.remove(file_name)
        except:
            continue

# Main function
def main():
    while True:
        logging.basicConfig(filename='compute_delay.log', level=logging.INFO, filemode='w+')
        print('==============================================================\n')
        print('Select option: \n')
        print('1) Create and/or play\n')
        print('2) Save for later\n')
        print('3) Delete save\n')
        print('4) Terminal Scaling\n')
        print('5) Exit\n')
        print('==============================================================\n')

        user_input = str(input("Your option: "))
        user_input.strip()  # removes trailing whitespaces

        if user_input == '1':
            #songname = audiosource()
            if os.path.isfile("BadApple.rle"):
                print('Decoding save.')
                results = decode_from_rle("BadApple.rle")
                print('\nDecode complete!')
            else:
                results = extract_resize_convert_frames('BadApple.mp4', 1)
            #os.system('color F0')  #Linux doesn't use this. Plus, this is a system call, which will replace the terminal settings for the user.
            try:
                p = vlc.MediaPlayer("bad-apple-audio.mp3")
                p.play()
                logging.info('Started')
                play_video(results)
                logging.info('Stopped')
            except:
                p.stop()
            #os.system('color 07')  #Not the best idea when users might have customized it.
            continue
        elif user_input == '2':
            #songname = audiosource()
            results = extract_resize_convert_frames('BadApple.mp4', 2)   #Directly bypasses both above, as it does both, with less i/o!
            print('Generating and saving results...\n')
            save_later(results)
            print('Results saved!')
            sys.exit()
        elif user_input == '3':
            print("Removing save...")
            try:
                os.remove("BadApple.rle")
            except:
                print("File does not exist.")
            continue
        elif user_input == '4':
            while True:
                frow = ''
                for i in range(150):
                    frow = frow + '#'
                print(frow + '@')
                for i in range(44):
                    print('#')
                confscale = input('# Lowest line ends here. Is this ok? Y / N : ')
                if confscale == 'Y' or confscale == 'y':
                    break
            continue
        elif user_input == '5':
            sys.exit()
        else:
            print('Unknown input!\n')
            continue


if __name__ == "__main__":
    main()

#Todo: RLE SAVE the resulting ascii frames as a single file.        --Done
#Todo: Implement back in the save feature.                          --Done
#Todo: Generalify so it can be used for any video (theoretically).
#Todo: Looping ascii art to scale console to size before start.     --Done
#Todo: Replace audio library to support force stopping of playback. --Done

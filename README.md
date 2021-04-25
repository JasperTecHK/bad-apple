# bad-apple
 Bad Apple printed out on the console with Python!

# Preface
A word of disclaimer, while the final code is somewhat original, this project is an amalgamation of different code snippets that I found online. As the main YouTube Video begins to gain traction, I feel the need to inform the audience that this code is NOT ENTIRELY ORIGINAL. 

The concept of playing Bad Apple!! on a Command Line Interface (CLI) is not a novel idea and I am definitely not the first. 

There are many iterations and versions around YouTube and I wanted to give it a shot. The intent of posting the video on YouTube was to show a few friends of a simple weekend project that I whipped up in Python. 

CalvinLoke's original video can be found [here](https://www.youtube.com/watch?v=AZfrXrk3ZHc).

Changes to this readme in relation to changes not found on the master branch will be suffixxed with --JasperTech.

## Differences compared to master branch implementation --JasperTech
1) Faster overall frame generation + asciification. (Properly utilizes threading, and combines steps to allow for less spaghetti)
2) Less I/O steps to non-volatile storage mediums (from 6571* 4 to 1 * 2 if saving, else frames are generated per execution.)
3) Compressed saved results (Stores all frames in one file, with RLE compression to achieve 7x less size, 8x block size, compared to saving individual frames, per frame.)
4) Breakout support (Exits a bit more gracefully, instead of spewing errors.)
5) Frame-terminal setup guide (Adds in a fake frame to adjust terminal shape before execution.)

Tl;dr, Fixed basically every issue plaguing the original.

# Running this code
Thanks to [TheHusyin](https://github.com/TheHusyin) for adding a `requirements.txt` file for easier installs.

First, ensure that you set your terminal to the directory of this repository. 

`cd bad-apple`

Install the necessary dependencies and packages by using:

`pip install -r requirements.txt`

And to run the code:

`python touhou_bad_apple_v2-Threading_Implementation.py` --JasperTech

And just follow the on-screen prompts. 

# Current known issues and bugs
Timing is a mild issue, unsure of if issue exists on Windows, or environment, but is consistantly 0.00x, instead of Linux's smoother 0.000x. Still, timing is good enough to the regular viewer. --JasperTech

# Version descriptor
1) touhou_bad_apple_v1.py

First rudimentary version that accomplishes basic frame extraction and animation. Utilizes threads, but suffers from heavy
synchronization issues.

2) touhou_bad_apple_v2.py

Extended version that includes a "GUI", some basic file I/O. Suffers from slight synchronization issues. Core program 
logic was completed in 24 hours with some minor tweaks and comments afterwards. 

3) touhou_bad_apple_v3.py

~~Current development version. Improved frame time delay and better file I/O. Looking to implement threading to expedite frame extraction and ASCII conversion.~~

Will be backported to v2-Threading if the implementation is good. v2-Threading should be treated as a seperate branch entirely, with features found on v2, v3, and more additions.


# Functions
The main functions will be listed here. 

## play_video()
Reads the frames from memory and prints it out onto the console. 

## progress_bar(current, total, barLength=25)
A simple progress bar function that generates the status of both frame extraction and ASCII frame generation. 
This code was taken from a [StackOverflow thread](https://stackoverflow.com/questions/6169217/replace-console-output-in-python).

`current` is the current value/progress of the process. 

`total` is the desired/intended end value of the process.

`barLength=25` sets the length of the progress bar. (Default is 25 characters)

## ASCII Frame generation
Not a particular function, but a group of functions.

```
resize_image()

greyscale()

pixels_to_ascii()
```
These functions are called in the `ascii_generator()` function to convert image files to ASCII format and stores them into .rle files. 

Note that the ASCII conversion code is not original, and was taken from [here](https://github.com/kiteco/python-youtube-code/blob/master/ascii/ascii_convert.py).

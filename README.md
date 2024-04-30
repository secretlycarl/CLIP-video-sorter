# CLIP-video-sorter
sorts videos based on user-defined visual content

This is a simple script that uses FFMPEG and CLIP to sort videos based on visual content. I had a bunch of videos that I didn't want to manually sort and couldn't find a free or efficient tool to do so, so I threw this together. I'm on windows.

It is meant to be used with mp4 files. FFMPEG extracts frames from the videos in a folder (1 per second of video), then CLIP analyzes the visual content of the frames and compares it to strings you input. It then sorts the videos into folders based on the words you are using. This was quickly made (with the help of gpt4 through [Cursor](https://cursor.sh/)) so I can't advise on the best type of filter parameters but I'd suggest starting with things in the same category, such as "desert, forest, city" etc. It can also use different subfilters to filter those categories further (day, night etc.) Definitely test in small batches before you do a whole library of videos. It's not perfect, and mis-categorizes anywhere from 5%-25% of them. Still helped me sort a lot of videos quicker than without it.

# Requirements

Python (3.7 or newer)

CUDA Compatible GPU

CUDA toolkit installed

FFMPEG installed and in PATH

Pytorch associated with your CUDA version (find it [here](https://pytorch.org/get-started/locally/))

# Setup

Get python set up on your system and add it to PATH.

Open the project folder in powershell

1. Create a virtual environment with
```
python -m venv venv
```

2. Activate the environment
```
venv\Scripts\activate
```

3. Install requirements
```
pip install -r requirements.txt
```

4. Install the correct pytorch for CUDA using the command from the pytorch.com link above, mine was
```
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

# Usage

1. Once all of the setup is complete, run this command with the venv activated
```
python analyze-sort-video.py
```

2. It will ask for a directory of videos to process. Copy and paste from the file explorer.

3. It will rename the files to be a stanard name with the count at the end (video_1 and so on) because I had some trouble with the script and videos that had the same file name.

4. It will prompt you
```
Enter the number of primary filters:
```
This is the amount of top level folders you want it to sort the current videos into. Based on "desert, forest, city" from earlier, that would be 3.

4. It will prompt you
```
Enter the name for primary filter 1:
```
This is the first term that it will use to sort. So "desert" from the example.

5. It will prompt you
```
Enter the number of subfilters for desert (Enter 0 to skip):
```
This is the amount of terms you use to sort the videos in "desert". From the example this would be 2. 0 can be entered to stop it from sorting further.

6. It will prompt you
```
Enter the name for subfilter 1 for desert:
```
This is the first term it will use to sort desert videos. "day" from the eample. It will then ask about the next filters until you have filled all of them in.

7. Then it will go on to have you select the next top level sorting term. "forest" from the example, and it will ask the same questions as it did for the first one.

8. Then it will process all of the videos and sort them. Once it finishes processing all the videos, it will ask for a new directory, or you can exit.

In my initial use, I needed to convert any stray mov files to mp4 and ignore landscape oriented videos for processing. This functionality is commented out and can be enabled if needed. 

# Potential changes

Improve the sorting. I have no idea what CLIP is seeing and using to decide how to sort, but it could be improved somewhat.

Add unlimited sorting levels. Currently it has 2 sorting levels that can have potentially unlimited sorting terms, though I haven't tried more than 3 each. I tried to implement unlimited levels but couldn't work it out.

import os
import glob
import torch
import ffmpeg
from PIL import Image
import clip
import shutil
import logging

# Setting up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Load the model
model, preprocess = clip.load("ViT-B/32", device='cuda')

#def rename_videos(directory):
#    """Renames all videos in the directory to 'video_n' where n is a counter."""
#    logging.info(f'Renaming videos in {directory}')
#    counter = 1
#    video_files = sorted(glob.glob(os.path.join(directory, '*.mov')) + glob.glob(os.path.join(directory, '*.mp4')))
#    for video_file in video_files:
#        extension = os.path.splitext(video_file)[1]
#        new_name = os.path.join(directory, f'video_{counter}{extension}')
#        if video_file != new_name and not os.path.exists(new_name):
#            os.rename(video_file, new_name)
#            logging.info(f'Renamed {video_file} to {new_name}')
#        counter += 1

#def convert_mov_to_mp4(mov_file):
#    """Converts a .mov file to .mp4 using FFmpeg."""
#    logging.info(f'Converting {mov_file} to .mp4')
#    mp4_file = os.path.splitext(mov_file)[0] + '.mp4'

#    try:
#        (
#            ffmpeg
#            .input(mov_file)
#            .output(mp4_file, vcodec='copy', acodec='copy')  # Copy all video and audio streams
#            .run(capture_stdout=True, capture_stderr=True)
#        )
#        logging.info(f'Successfully converted {mov_file} to {mp4_file}')
#    except ffmpeg.Error as e:
#        logging.error(f"FFmpeg error while converting {mov_file} to .mp4: {e.stderr.decode()}")
#        logging.error(f"FFmpeg stdout: {e.stdout.decode()}")
#        return False

    # Delete the original .mov file after successful conversion
#    os.remove(mov_file)
#    return True

def extract_frames(video_path, output_folder):
    """Extracts frames from a video file and returns True if successful, False otherwise."""
    logging.info(f'Extracting frames from {video_path} to {output_folder}')
    # Get video metadata
    try:
        metadata = ffmpeg.probe(video_path)
    except ffmpeg.Error as e:
        logging.error(f'FFmpeg probing error on video {video_path}: {e.stderr.decode()}')
        return False

    # Get video dimensions
    #video_stream = next((stream for stream in metadata['streams'] if stream['codec_type'] == 'video'), None)
    #if video_stream is None:
    #    logging.info(f"No video stream found in {video_path}")
    #    return False
    #width = video_stream['width']
    #height = video_stream['height']

    # Skip videos that are wider than they are tall
    #if width > height:
    #    logging.info(f"Skipping {video_path} because it's landscape-oriented")
    #    return False

    # Create output folder after checking video orientation
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    try:
        (
            ffmpeg
            .input(video_path)
            .output(os.path.join(output_folder, 'frame_%04d.jpg'), vf='fps=1', video_bitrate='5000k', sws_flags='bilinear')
            .run(capture_stdout=True, capture_stderr=True)
        )
        logging.info(f'Successfully extracted frames from {video_path} to {output_folder}')
        return True
    except ffmpeg.Error as e:
        logging.error(f"FFmpeg error during frame extraction from {video_path}: {e.stderr.decode()}")
        return False

def analyze_and_sort(output_folder, video_path, filters, filter_folders):
    """Analyzes frames using the CLIP model and sorts videos based on attributes."""
    logging.info(f'Analyzing frames in {output_folder} for video {video_path}')
    frame_files = glob.glob(os.path.join(output_folder, '*.jpg'))

    # Sort by filter
    filter_indices = []
    for frame_path in frame_files:
        image = preprocess(Image.open(frame_path)).unsqueeze(0).to('cuda')
        text = clip.tokenize(filters).to('cuda')
        with torch.no_grad():
            image_features = model.encode_image(image)
            text_features = model.encode_text(text)
        similarities = torch.cosine_similarity(text_features, image_features, dim=-1)
        filter_indices.append(similarities.argmax().item())
    filter_index = max(set(filter_indices), key=filter_indices.count)

    # Move the video to the corresponding filter folder
    destination_folder = os.path.join(os.path.dirname(video_path), filter_folders[filter_index])
    logging.info(f"Moved video {video_path} to {destination_folder} based on filter {filters[filter_index]}")

    os.makedirs(destination_folder, exist_ok=True)
    shutil.move(video_path, os.path.join(destination_folder, os.path.basename(video_path)))

def main():
    """Converts .mov files to .mp4, extracts frames from all video files in the specified directory and analyzes them."""
    filters = None
    while True:
        logging.info('Starting main function')
        # Get the directory from the user
        directory = input("Enter the directory path (or 'exit' to quit): ")

        if directory.lower() == 'exit':
            break

        # Rename videos
        #rename_videos(directory)

        # Convert .mov files to .mp4
        #mov_files = glob.glob(os.path.join(directory, '*.mov'))  # Adjust the pattern if your video files have different extensions
        #for mov_file in mov_files:
        #    if convert_mov_to_mp4(mov_file):
        #        logging.info(f'Converted {mov_file}')

        # Get user input for filters and subfilters
        if filters is None or input("Use the same filters as last time? (y/N): ").lower() != 'y':
            num_primary_filters = int(input("Enter the number of primary filters: "))
            filters = {}
            for i in range(num_primary_filters):
                primary_filter = input(f"Enter the name for primary filter {i+1}: ")
                num_subfilters = int(input(f"Enter the number of subfilters for {primary_filter} (Enter 0 to skip): "))
                subfilters = []
                if num_subfilters != 0:
                    for j in range(num_subfilters):
                        subfilters.append(input(f"Enter the name for subfilter {j+1} for {primary_filter}: "))
                filters[primary_filter] = subfilters

        # Process .mp4 files
        video_files = glob.glob(os.path.join(directory, '*.mp4'))  # Adjust the pattern if your video files have different extensions
        for video_path in video_files:
            filename = os.path.splitext(os.path.basename(video_path))[0]
            output_folder = os.path.join(directory, filename)
            if extract_frames(video_path, output_folder):  # Only analyze frames if extract_frames was successful
                # Analyze frames based on primary filters and sort videos
                analyze_and_sort(output_folder, video_path, list(filters.keys()), list(filters.keys()))
                shutil.rmtree(output_folder)  # Delete the folder with frames

        # Process .mp4 files again for subfilters
        for primary_filter, subfilters in filters.items():
            if subfilters:
                video_files = glob.glob(os.path.join(directory, primary_filter, '*.mp4'))  # Adjust the pattern if your video files have different extensions
                for video_path in video_files:
                    filename = os.path.splitext(os.path.basename(video_path))[0]
                    output_folder = os.path.join(directory, primary_filter, filename)
                    if extract_frames(video_path, output_folder):  # Only analyze frames if extract_frames was successful
                        # Analyze frames based on subfilters and sort videos
                        analyze_and_sort(output_folder, video_path, subfilters, subfilters)
                        shutil.rmtree(output_folder)  # Delete the folder with frames

        print("Finished processing the directory.\n")

    print("Exiting the program.")

if __name__ == '__main__':
    main()


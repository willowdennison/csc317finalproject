from moviepy import VideoFileClip

video = VideoFileClip(r'video.mp4')

video.audio.write_audiofile(r"audio.mp3")
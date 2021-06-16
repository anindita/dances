import moviepy
import moviepy.editor as mp

filename = 'wl'

video = mp.VideoFileClip(f"videos/{filename}.mp4")
audio = video.set_fps(30)

audio.write_audiofile(f'audios/{filename}.mp3')
print(video.fps)
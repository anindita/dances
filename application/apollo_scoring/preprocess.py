import os
import moviepy
import moviepy.editor as mp

def process_video(vid):
    video = mp.VideoFileClip(vid)
    video = video.rotate(90).resize(height=1280)

    half = vid.split("/")[1]

    video.set_audio(video.audio).write_videofile(
        filename=f"wk3_pp/{half[:-4]}.mov",
        fps=None,
        codec="libx264",
        audio_codec="aac",
        bitrate=None,
        audio=True,
        audio_fps=44100,
        preset='medium',
        audio_nbytes=4,
        audio_bitrate=None,
        audio_bufsize=2000,
        rewrite_audio=True,
        verbose=True,
        threads=4,
        ffmpeg_params=None)

def process_all():
    folder_path = os.path.join("Week 3 Submissions")
    es = [ x[:-4] for x in os.listdir(folder_path)]
    vids = os.path.join("wk3_pp")
    missing = [ x[:-4] for x in os.listdir(vids)]
    missing = list(set(es) - set(missing))
    #missing.remove('.DS_S')
    
    formatted = []
    es = [ x for x in os.listdir(folder_path)]
    for m in missing:
        for e in es:
            if m in e:
                formatted.append(e)

    formatted.sort()
    for e in formatted:
        print(f"Processing {e}")
        process_video(f"Week 3 Submissions/{e}")

process_all()

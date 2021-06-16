import moviepy
import moviepy.editor as mp
from moviepy.editor import VideoFileClip, vfx
import scoring as apollo

def overlay_video(original, entry, video, res=1, split=0, split2=0):
    scores = apollo.oks_score(apollo.get_positions_lists(original), apollo.get_positions_lists(entry), res=res, split=split, split2=split2)
    print(scores[-1])
    half = entry.split("/")[1]
    uni_logo = half.split("_")[0]

    video = mp.VideoFileClip(video)
    logo = mp.ImageClip(f"./logos/{uni_logo}.png")
    logo = logo.set_duration(video.duration).resize(height=150).set_position((10,10))

    clips = []
    clips.append(video)
    clips.append(logo)

    for i in range(len(scores)):
        txt_clip = mp.TextClip("Score: %.2f" % scores[i], font='Ayuthaya', fontsize = 50, color = 'black', bg_color='white')
        score = txt_clip.set_pos((10, 1200)).set_duration(1/30).set_start((i+1)/30)
        clips.append(score)

    final = mp.CompositeVideoClip(clips, size=video.size)
    final.set_audio(video.audio).write_videofile(
        filename=f"wk3_vids/{half}.mov",
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

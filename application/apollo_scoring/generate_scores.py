import os # for manipulates files and subdirectories
import json
import scoring as apollo
import overlay as artemis

def mp4(university):
    return [f"wk2_res/{university}", f"wk2_pp/{university}.mp4"]

def mov(university):
    return [f"wk2_res/{university}", f"wk2_pp/{university}.mov"]

results_json = {}

def score_and_write(original, entry, video, res=1, split=0, split2=0):
    scores = apollo.oks_score(apollo.get_positions_lists(original), apollo.get_positions_lists(entry), res=res, split=split, split2=split2)
    half = entry.split("/")[1]
    # print(half)
    # results_json[half] = scores
    f = open("week1.txt", "a")
    line = f"{entry} has scored {scores[-1]}\n"
    f.write(line)
    f.close()

def get_entries():
    folder_path = os.path.join("wk3_pp")
    es = [ x for x in os.listdir(folder_path) ]
    keypoints = {}
    videos = {}
    for e in es:
        uni = e[:-4]
        keypoints[uni] = f"wk3_res/{uni}"
        videos[uni] = f"wk3_pp/{e}"
    return keypoints, videos

def get_entries_for_song(song):
    folder_path = os.path.join("wk3_pp")
    e = [ x for x in os.listdir(folder_path) if song in x]
    return len(e)

entries, videos = get_entries()

def score_for_song(song, song_path):
    global entries, videos
    with open("week1.txt", 'a') as f:
        line = f"Expecting {get_entries_for_song(song)} entries\n"
        f.write(line)
        f.write("Calculating scores...\n")
    folder_path = os.path.join("wk3_pp")
    es = [ x for x in os.listdir(folder_path) if song in x]
    for entry in es:
        uni = entry[:-4]
        artemis.overlay_video(song_path, entries[uni], videos[uni])

def generate_video(uni, song_path):
    artemis.overlay_video(song_path, entries[uni], videos[uni], split=32)

def generate_videos(unis, song_path):
    for uni in unis:
        generate_video(uni, song_path)

def missing_songs():
    folder_path = os.path.join("wk3_pp")
    es = [ x[:-4] for x in os.listdir(folder_path)]
    vids = os.path.join("wk3_pp")
    missing = [ x[:-4] for x in os.listdir(vids)]
    return list(set(es) - set(missing))

def multi_score_and_write(es):
    for entry in es:
        uni = entry[:-4]
        song = uni.split("_")[1]
        song_path = f"wk3_res/{song}"
        artemis.overlay_video(song_path, entries[uni], videos[uni])
    with open("week1.json", 'a') as f:
        json.dump(results_json, f)
    
violeta = "wk3_res/v"
icsm = "wk3_res/icsm"
bluehour = "wk3_res/bh"
ridin = "wk3_res/r"

#score_for_song("_v", violeta)
#score_for_song("_icsm", icsm)
#score_for_song("_bh", bluehour)
#score_for_song("_r", ridin)

generate_video("ic_r_2", ridin)

missing = missing_songs()
ms = "\n".join(missing)
print(ms)


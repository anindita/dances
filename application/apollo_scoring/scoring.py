import os # for manipulates files and subdirectories
import json # handle json files
import math
import matplotlib.pyplot as plt
import numpy as np

def get_positions_lists(directory, offset=0, transition=0):
    json_folder_path = os.path.join(directory)
    json_files = [ x for x in os.listdir(json_folder_path) if x.endswith("json") ]
    result = []

    for i in range(offset*30,len(json_files)):
        json_file = json_files[i]
        json_file_path = os.path.join(json_folder_path, json_file)
        with open (json_file_path, "r") as f:
            data = json.load(f)
            try:
                result.append(data["people"][0]["pose_keypoints_2d"])
            except:
                result.append([])
    return result

def translate(lists):
    for l in lists:
        if not l:
            continue
        x = l[8*3]
        y = l[8*3 + 1]
        for i in range(0,len(l),3):
            if l[i+2] == 0:
                l[i] = 0
                l[i+1] = 0
            else:
                l[i] -= x
                l[i+1] -= y

def translate_frame(frame, x, y):
    for i in range(0,len(frame),3):
        frame[i] -= x
        frame[i+1] -= y

def get_gradient_diff(f1, f2, a, b, frame_score):
    x_1a = f1[a*3]
    y_1a = f1[a*3 + 1]
    x_1b = f1[b*3]
    y_1b = f1[b*3 + 1]

    x_2a = f2[a*3]
    y_2a = f2[a*3 + 1]
    x_2b = f2[b*3]
    y_2b = f2[b*3 + 1]

    try:
        grad1 = (y_1b - y_1a) / (x_1b - x_1a)
        grad2 = (y_2b - y_2a) / (x_2b - x_2a)
        diff = abs(grad1 - grad2)
    except ZeroDivisionError:
        diff = 11

    angle = get_angle_diff(f1,f2,a,b)
    
    if diff < 1 and angle < 5:
        return frame_score * 2
    elif diff < 10 or angle < 10:
        return frame_score * 0.91
    else:
        return frame_score / 10

def get_angle_diff(f1, f2, a, b):
    x_1a = f1[a*3]
    y_1a = f1[a*3 + 1]
    x_1b = f1[b*3]
    y_1b = f1[b*3 + 1]

    x_2a = f2[a*3]
    y_2a = f2[a*3 + 1]

    angle1 = math.atan2(y_1a - y_1b, x_1a - x_1b)
    angle2 = math.atan2(y_2a - y_1b, x_2a - x_1b)

    angle_between = np.mod((angle1 - angle2) * (180 / math.pi), 180)

    return min(angle_between, abs(180-angle_between))/180

def angle_score(og, en):
    score = 0
    f_score = 500 / len(en)

    for i in range(0,len(og)):
        og_frame = og[i]
        try:
            en_frame = en[i]
        except IndexError:
            break

        if not og_frame or not en_frame:
            continue

        frame_score = 1
        frame_score = get_gradient_diff(og_frame, en_frame, 0, 1, frame_score)
        frame_score = get_gradient_diff(og_frame, en_frame, 1, 2, frame_score)
        frame_score = get_gradient_diff(og_frame, en_frame, 1, 5, frame_score)
        frame_score = get_gradient_diff(og_frame, en_frame, 1, 8, frame_score)
        frame_score = get_gradient_diff(og_frame, en_frame, 2, 3, frame_score)
        frame_score = get_gradient_diff(og_frame, en_frame, 3, 4, frame_score)
        frame_score = get_gradient_diff(og_frame, en_frame, 5, 6, frame_score)
        frame_score = get_gradient_diff(og_frame, en_frame, 6, 7, frame_score)
        frame_score = get_gradient_diff(og_frame, en_frame, 8, 9, frame_score)
        frame_score = get_gradient_diff(og_frame, en_frame, 8, 12, frame_score)
        frame_score = get_gradient_diff(og_frame, en_frame, 9, 10, frame_score)
        frame_score = get_gradient_diff(og_frame, en_frame, 10, 11, frame_score)
        frame_score = get_gradient_diff(og_frame, en_frame, 12, 13, frame_score)
        frame_score = get_gradient_diff(og_frame, en_frame, 13, 14, frame_score)

        score += f_score * frame_score / 32

    return score

def position_score(og, en):
    score = 0
    f_score = 500 / len(en)

    translate(og)
    translate(en)
    
    for i in range(0,len(og)):
        og_frame = og[i]
        try:
            en_frame = en[i]
        except IndexError:
            break

        if not og_frame or not en_frame:
            continue

        og_torso = math.sqrt((og_frame[1*3] - og_frame[1*8]) ** 2 + (og_frame[1*3 + 1] - og_frame[1*8 + 1]) ** 2)
        en_torso = math.sqrt((en_frame[1*3] - en_frame[1*8]) ** 2 + (en_frame[1*3 + 1] - en_frame[1*8 + 1]) ** 2)

        scale_factor = og_torso / en_torso

        for p in range(0, len(en_frame), 3):
            en[i][p] *= scale_factor
            en[i][p+1] *= scale_factor

        frame_score = 1

        for p in range(0, 15*3, 3):
            distance = math.sqrt((en_frame[p] - og_frame[p]) ** 2 + (en_frame[p + 1] - og_frame[p + 1]) ** 2)
            if distance < 10:
                frame_score *= 2
            elif distance < 60:
                frame_score += 1
            elif distance > 300:
                frame_score /= 2

        score += f_score * frame_score / 15

    return int(score)

def running_averages(scores, split=0, split2=0):
    running_averages = [100]
    skip_frames = []
    if split > 0:
        midpoint = split * 30
        begin = midpoint - 45
        end = midpoint + 45
        skip_frames = list(range(begin,end))

    if split2 > 0:
        midpoint = split * 30
        begin = midpoint - 45
        end = midpoint + 45
        skip = list(range(begin,end))
        skip_frames = skip_frames + skip

    for frame, score in enumerate(scores):
        prev_avg = running_averages[-1]
        if score < 0 or frame in skip_frames:
            running_averages.append(prev_avg)
        else:
            add = min(100, score)
            running_averages.append((prev_avg * frame + add) / (frame + 1))
    return running_averages

def minmax(val_list):
    min_val = min(val_list)
    max_val = max(val_list)

    return (min_val, max_val)

def oks_score(og, en, res=1, split=0, split2=0):
    score = []

    translate(og)
    translate(en)
    
    for i in range(0,len(og)):
        og_frame = og[i]
        try:
            en_frame = en[i]
        except IndexError:
            break

        if not og_frame or not en_frame:
            continue

        point_1 = 0
        point_2 = 8

        og_torso = math.sqrt((og_frame[1*point_1] - og_frame[1*point_2]) ** 2 + (og_frame[1*point_1 + 1] - og_frame[1*point_2 + 1]) ** 2)
        en_torso = math.sqrt((en_frame[1*point_1] - en_frame[1*point_2]) ** 2 + (en_frame[1*point_1 + 1] - en_frame[1*point_2 + 1]) ** 2)

        try:
            scale_factor = og_torso / en_torso
        except ZeroDivisionError:
            scale_factor = 1

        for p in range(0, len(en_frame), 3):
            en[i][p] *= scale_factor
            en[i][p+1] *= scale_factor
    
    for i in range(0,len(og)):
        og_frame = og[i]
        try:
            en_frame = en[i]
        except IndexError:
            break

        if not og_frame or not en_frame:
            score.append(-1)
            continue
    
        frame_score = 0
        points = 15

        min_x, max_x = minmax(en_frame[0::3])
        min_y, max_y = minmax(en_frame[1::3])
        # Fixed 23/01 19:05
        height = (max_x - min_x) * (max_y - min_y)
        k_vals = [0.001, 0.001, 0.001, 0.0035, 0.0035, 0.009, 0.009, 0.0072, 0.0072, 0.0062, 0.0062, 0.011, 0.11, 0.0087, 0.0087, 0.0089, 0.0089]
        k = -1

        for p in range(0, points * 3, 3):
            k = k+1
            if en_frame[p+2] == 0.0 or og_frame[p+2] == 0.0:
                points -= 1
                continue
            distance = math.sqrt((en_frame[p] - og_frame[p]) ** 2 + (en_frame[p + 1] - og_frame[p + 1]) ** 2)
            frame_score += math.exp(-((distance ** 2)/(2 * height ** 2 * k_vals[k] ** 2)))
        
        score.append(100 * frame_score / points)

    return running_averages(score, split, split2)

numbers = [1, 2, -3, 7, 1]

# Step 0: Gather all positions per frame for entry
bh = get_positions_lists('train/bh')
bh_t = get_positions_lists('train/bh_t')

print(len(bh[0]))
# nbtm = get_positions_lists('train/nbtm')
# nbtm_t = get_positions_lists('train/nbtm_t')
# green = get_positions_lists('train/green')
# green2 = get_positions_lists('train/green2')


print(f"Blue Hour OKS score is {oks_score(bh,bh_t)[-1]}")
#print(f"By the Moon OKS score is {oks_score(nbtm,nbtm_t)[-1]}")

# print(f"So What OKS score is {oks_score(sw,sw_n)[-1]}")

# print(f"Blue Hour score is {angle_score(og,en) + position_score(og,en)}")
# print(f"By the Moon score is {angle_score(out,outt) + position_score(out,outt)}")


# # Print frame on graph
# plt.xlabel("X-axis")
# plt.ylabel("Y-axis")
# plt.title("A test graph")
# fig = plt.figure(1)
# fig.add_subplot()
# for i in range(0,len(og[5]),3):
#     plt.scatter(og[5][i], og[5][i+1], color='red')

# fig.add_subplot()
# for i in range(0,len(en[0]),3):
#     plt.scatter(en[5][i], en[5][i+1], color='blue')

# plt.tight_layout()
# plt.show()

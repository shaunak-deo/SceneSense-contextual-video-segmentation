import os
import subprocess

def extract_frame(video_path, timestamp, output_path):
    cmd = ["ffmpeg", "-y", "-ss", str(timestamp), "-i", video_path, "-vframes", "1", "-q:v", "2", output_path]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def extract_frames(video_path, start, end, output_dir, num_frames=3):
    os.makedirs(output_dir, exist_ok=True)
    paths = []
    for i in range(num_frames):
        ts = start + i * ((end - start) / (num_frames + 1))
        out_path = os.path.join(output_dir, f"frame_{i+1}.jpg")
        extract_frame(video_path, ts, out_path)
        paths.append(out_path)
    return paths
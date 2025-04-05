from scenedetect import open_video, SceneManager
from scenedetect.detectors import AdaptiveDetector
from app.frame_extractor import extract_frames
from app.openai_labeler import label_frames
from app.utils import format_time, save_labels
import os

def detect_scenes(video_path):
    video = open_video(video_path)
    scene_manager = SceneManager()
    scene_manager.add_detector(AdaptiveDetector(min_scene_len=30))
    scene_manager.detect_scenes(video)
    return [(s[0].get_seconds(), s[1].get_seconds()) for s in scene_manager.get_scene_list()]

def merge_to_chunks(scenes, chunk_duration=600, min_duration=480):
    chunks = []
    current_chunk = []
    current_duration = 0

    for i, (start, end) in enumerate(scenes):
        seg_len = end - start

        if current_duration + seg_len > chunk_duration and current_duration >= min_duration:
            # Finalize current chunk
            chunks.append((current_chunk[0][0], current_chunk[-1][1]))
            current_chunk = [(start, end)]
            current_duration = seg_len
        else:
            current_chunk.append((start, end))
            current_duration += seg_len

    # Add leftover chunk
    if current_chunk:
        chunks.append((current_chunk[0][0], current_chunk[-1][1]))

    return chunks


def process_video(video_path, chunk_duration):
    scenes = detect_scenes(video_path)
    chunks = merge_to_chunks(scenes, chunk_duration)
    results = []
    for i, (start, end) in enumerate(chunks):
        print(f"📍 Segment {i+1}: {format_time(start)} → {format_time(end)}")
        output_dir = f"output/segment_{i+1}"
        frame_paths = extract_frames(video_path, start, end, output_dir)
        labels = label_frames(frame_paths)
        print(f"   🏷️ Labels: {labels}\n")
        results.append({"segment": i+1, "start": start, "end": end, "labels": labels})
    save_labels(results, "output/labels.json")
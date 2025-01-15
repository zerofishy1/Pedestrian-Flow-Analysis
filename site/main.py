import cv2
import numpy as np
import os
from collections import defaultdict
from deep_sort_realtime.deepsort_tracker import DeepSort
from ultralytics import YOLO
import json
import time

def process_video(video_path):
    model = YOLO('yolov8n.pt')

    tracker = DeepSort(max_age=50, nn_budget=20, max_iou_distance=0.6)

    cap = cv2.VideoCapture(video_path)

    frame_count = 0
    frame_skip = 1
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    time_window = 10
    window_frames = fps * time_window

    movement_stats = {"вверх": 0, "вниз": 0, "налево": 0, "направо": 0}
    frame_to_person_count = defaultdict(int)
    tracker_history = defaultdict(list)

    def is_in_dead_zone(x, y, dead_zone):
        """Проверка, находится ли объект в мёртвой зоне"""
        return dead_zone['x_min'] < x < dead_zone['x_max'] and dead_zone['y_min'] < y < dead_zone['y_max']

    dead_zone = {
        'x_min': 0,
        'x_max': 960,
        'y_min': 0,
        'y_max': 180
    }

    tracked_ids = set()

    peak_window = None
    max_people = 0

    tracked_directions = set()

    unique_people_in_window = set()
    start_time = time.time()

    first_seen_objects = []
    object_id_mapping = {}

    last_positions = {}

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            if frame_count % frame_skip == 0:
                results = model(frame, imgsz=928, classes=[0], conf=0.6, iou=0.3)  # class 0 = "person"
                detections = []

                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        conf = float(box.conf[0])
                        xyxy = box.xyxy[0].tolist()
                        x1, y1, x2, y2 = map(int, xyxy)
                        cx, cy = x1 + (x2 - x1) // 2, y1 + (y2 - y1) // 2

                        if is_in_dead_zone(cx, cy, dead_zone):
                            continue

                        detections.append([[x1, y1, x2 - x1, y2 - y1], conf, 0])

                outputs = tracker.update_tracks(detections, frame=frame)
                current_person_count = 0

                for output in outputs:
                    if not output.is_confirmed() or output.time_since_update > 1:
                        continue

                    track_id = output.track_id
                    bbox = output.to_ltwh()
                    x, y, w, h = map(int, bbox)
                    cx, cy = x + w // 2, y + h // 2

                    if track_id not in object_id_mapping:
                        object_id_mapping[track_id] = len(first_seen_objects) + 1
                        first_seen_objects.append(track_id)

                    assigned_id = object_id_mapping[track_id]

                    tracked_ids.add(assigned_id)

                    direction = None
                    if assigned_id in tracker_history:
                        prev_cx, prev_cy = tracker_history[assigned_id][-1]
                        dx, dy = cx - prev_cx, cy - prev_cy
                        if abs(dx) > abs(dy):
                            direction = "вниз" if dx > 0 else "вверх"
                        else:
                            direction = "направо" if dy > 0 else "налево"

                    if direction and assigned_id not in tracked_directions:
                        movement_stats[direction] += 1
                        tracked_directions.add(assigned_id)

                    last_positions[assigned_id] = (cx, cy)

                    tracker_history[assigned_id].append((cx, cy))
                    if len(tracker_history[assigned_id]) > 10:
                        tracker_history[assigned_id].pop(0)

                    # Отрисовка треков
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    cv2.putText(frame, f"ID: {assigned_id}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                    current_person_count += 1

                frame_to_person_count[frame_count] = current_person_count

                elapsed_time = time.time() - start_time
                if elapsed_time >= time_window:
                    # Проверяем, если outputs пустой, чтобы избежать ошибки
                    if 'assigned_id' in locals():
                        unique_people_in_window.add(assigned_id)

                    people_in_window = len(unique_people_in_window)
                    if people_in_window > max_people:
                        max_people = people_in_window
                        peak_window = (int((frame_count - window_frames) / fps), int(frame_count / fps))

                    start_time = time.time()
                    unique_people_in_window.clear()

                cv2.putText(frame, f"People in the frame: {current_person_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.imshow("Movement Tracking", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()

        # Формирование итогового JSON
        output_data = {
            "total_unique_people": len(tracked_ids),
            "movement_statistics": movement_stats,
        }

        with open("results/results.json", "w", encoding="utf-8") as json_file:
            json.dump(output_data, json_file, ensure_ascii=False, indent=4)

        print("Results saved to movement_tracking_results.json")
    return output_data

def process_all_videos_in_uploads():
    uploads_folder = "uploads"
    for filename in os.listdir(uploads_folder):
        if filename.endswith(".mp4"):
            video_path = os.path.join(uploads_folder, filename)
            process_video(video_path)

process_all_videos_in_uploads()

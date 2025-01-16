import cv2
import numpy as np
from collections import defaultdict
from deep_sort_realtime.deepsort_tracker import DeepSort
from ultralytics import YOLO
import json
import time
import os

def process_video(video_path, output_video_path="output.mp4"):
    # Загрузка модели YOLO
    model = YOLO('yolov8n.pt')

    # Настройка DeepSort
    tracker = DeepSort(max_age=50, nn_budget=20, max_iou_distance=0.6)

    # Открытие видеофайла
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Видео {video_path} не найдено или не может быть открыто.")
        return

    # Получение параметров видео
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Настройка видеозаписи
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    # Инициализация переменных
    frame_count = 0
    movement_stats = {"вверх": 0, "вниз": 0, "налево": 0, "направо": 0}
    tracked_ids = set()
    object_id_mapping = {}
    tracker_history = defaultdict(list)
    last_positions = {}
    id_directions = {}  # Хранение направления для каждого ID
    dead_zone = {'x_min': 0, 'x_max': width // 2, 'y_min': 0, 'y_max': height // 4}
    peak_window = None
    max_people = 0
    unique_people_in_window = set()
    start_time = time.time()

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # Обработка каждого кадра
            results = model(frame, imgsz=640, classes=[0], conf=0.6, iou=0.3)  # class 0 = "person"
            detections = []

            for result in results:
                boxes = result.boxes
                for box in boxes:
                    conf = float(box.conf[0])
                    xyxy = box.xyxy[0].tolist()
                    x1, y1, x2, y2 = map(int, xyxy)
                    cx, cy = x1 + (x2 - x1) // 2, y1 + (y2 - y1) // 2

                    if dead_zone['x_min'] < cx < dead_zone['x_max'] and dead_zone['y_min'] < cy < dead_zone['y_max']:
                        continue

                    detections.append([[x1, y1, x2 - x1, y2 - y1], conf, 0])

            # Обновление треков
            outputs = tracker.update_tracks(detections, frame=frame)
            for output in outputs:
                if not output.is_confirmed() or output.time_since_update > 1:
                    continue

                track_id = output.track_id
                bbox = output.to_ltwh()
                x, y, w, h = map(int, bbox)
                cx, cy = x + w // 2, y + h // 2

                # Привязка ID объектов
                if track_id not in object_id_mapping:
                    object_id_mapping[track_id] = len(object_id_mapping) + 1

                assigned_id = object_id_mapping[track_id]
                tracked_ids.add(assigned_id)

                # Определение направления движения
                direction = None
                if assigned_id in tracker_history:
                    prev_cx, prev_cy = tracker_history[assigned_id][-1]
                    dx, dy = cx - prev_cx, cy - prev_cy
                    if abs(dx) > abs(dy):
                        direction = "вниз" if dx > 0 else "вверх"
                    else:
                        direction = "направо" if dy > 0 else "налево"

                    # Проверка, чтобы не учитывать направление, если оно уже было вычислено
                    if direction and assigned_id not in id_directions:
                        id_directions[assigned_id] = direction
                        movement_stats[direction] += 1

                # Сохранение позиции
                tracker_history[assigned_id].append((cx, cy))
                if len(tracker_history[assigned_id]) > 10:
                    tracker_history[assigned_id].pop(0)

                # Рисование рамок и ID
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.putText(frame, f"ID: {assigned_id}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                # Отображение направления для каждого ID
                if assigned_id in id_directions:
                    direction_text = id_directions[assigned_id]
                    cv2.putText(frame, f"Dir: {direction_text}", (x, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Добавление текста на кадр
            current_person_count = len(tracked_ids)
            cv2.putText(frame, f"People tracked: {current_person_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            # Пиковое время в 10-секундном интервале
            elapsed_time = time.time() - start_time
            if elapsed_time >= 10:  # 10 секундный интервал
                people_in_window = len(tracked_ids)
                if people_in_window > max_people:
                    max_people = people_in_window
                    peak_window = (int((frame_count - 10 * fps) / fps), int(frame_count / fps))
                start_time = time.time()

            if peak_window:
                cv2.putText(frame, f"Peak people in 10s: {max_people}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            # Запись кадра
            out.write(frame)

            # Отображение в реальном времени
            cv2.imshow("Processed Video", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        # Освобождение ресурсов
        cap.release()
        out.release()
        cv2.destroyAllWindows()

        # Сохранение результатов
        results_path = "results/results.json"
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump({
                "total_unique_people": len(tracked_ids),
                "movement_statistics": movement_stats,
                "peak_time_window": peak_window,
                "peak_people_count": max_people,
                "id_directions": id_directions  # Сохранение направлений для каждого ID
            }, f, ensure_ascii=False, indent=4)

        print(f"Обработка завершена. Результаты сохранены в {results_path} и {output_video_path}.")



def process_all_videos_in_uploads():
    uploads_folder = "uploads"
    for filename in os.listdir(uploads_folder):
        if filename.endswith(".mp4"):
            video_path = os.path.join(uploads_folder, filename)
            process_video(video_path)

process_all_videos_in_uploads()

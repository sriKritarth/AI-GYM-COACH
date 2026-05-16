import os
import cv2
import numpy as np
import mediapipe as mp
import av
from streamlit_webrtc import VideoProcessorBase
import threading
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from detectors.squats import SquatDetector
from detectors.pushup import PushUpDetector
from detectors.bicep_curl import BicepsCurlDetector
from detectors.lunges import LungesDetector
from detectors.shoulder_press import ShoulderPressDetector
from services.config.workout_config import POSE_CONNECTIONS



class VideoProcessor(VideoProcessorBase):
    def __init__(self):
        self._lock = threading.Lock()
        self._latest_metrics = None
        self.exercise_type = "Squats"

        model_path = os.path.join(os.getcwd() , "ml_models" , "pose_landmarker_full.task")
        base_option = python.BaseOptions(model_asset_path = model_path)

        options = vision.PoseLandmarkerOptions(
            base_options = base_option,
            running_mode = vision.RunningMode.VIDEO , 
            min_pose_detection_confidence = 0.7,
            min_pose_presence_confidence = 0.7,
            min_tracking_confidence = 0.7,
            output_segmentation_masks = False
        )

        self._landmarker = vision.PoseLandmarker.create_from_options(options)

        self._frame_timestamp_ms = 0

        self._detectors = {
            "Squats" : SquatDetector(),
            "Bicep Curls(Dumbbell)" : BicepsCurlDetector(),
            "Lunges" : LungesDetector(),
            "Push-ups" : PushUpDetector(),
            "Shoulder Press" : ShoulderPressDetector()
        }


    def set_latest_metrics(self , metrics):
        with self._lock:
            self._latest_metrics = metrics.copy()

    def get_latest_metrics(self):
        with self._lock:
            return None if self._latest_metrics is None else self._latest_metrics.copy()


    def set_exercise(self , exercise_type):
        with self._lock:
            self.exercise_type = exercise_type

    def get_exercise(self):
        with self._lock:
            return self.exercise_type
        

    def _draw_skeleton(self , img , landmarks):
        h , w = img.shape[:2]

        for start_idx , end_idx in POSE_CONNECTIONS:
            p1 = landmarks[start_idx]
            p2 = landmarks[end_idx]

            if p1.visibility > 0.7 and p2.visibility > 0.7:
                cv2.line(
                    img=img,
                    pt1=(int(p1.x * w) , int(p1.y * h)),
                    pt2=(int(p2.x * w) , int(p2.y * h)),
                    color=(0 ,255 , 0),
                    thickness=8
                )
        
        for lm in landmarks:
            if lm.visibility > 0.7:
                cv2.circle(
                    img,
                    (int(lm.x * w) , int(lm.y * h)),
                    8,
                    (255 , 0 , 0),
                    -1
                )

        return img
    
    def _draw_no_pose_warnings(self , img):
        cv2.putText(
            img,
            "NO POSE DETECTED",
            (30 , 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0 , 255 , 0),
            2 ,
            cv2.LINE_AA
        )

        cv2.putText(
            img,
            "PLEASE FACE THE CAMERA",
            (30 , 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0 , 255 , 0),
            2 ,
            cv2.LINE_AA
        )
    

    def _draw_overlays(self , img , metrics , ex_type):
        if ex_type == "Squats":
            self._draw_squats_overlays(img , metrics)
        elif ex_type == "Push-ups":
            self._draw_pushup_overlays(img, metrics)
        elif ex_type == "Bicep Curls(Dumbbell)":
            self._draw_curl_overlays(img, metrics)
        elif ex_type == "Shoulder Press":
            self._draw_press_overlays(img, metrics)
        elif ex_type == "Lunges":
            self._draw_lunge_overlays(img, metrics)


    def _draw_squats_overlays(self , img , metrics):
        h = img.shape[0]

        cv2.putText(
            img,
            f"DEPTH : {metrics['depth_status']}",
            (20 , h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0 , 255 , 0),
            2
        )

    
    def _draw_pushup_overlays(self, img, metrics):
        h, _ = img.shape[:2]

        cv2.putText(
            img,
            f"BODY: {metrics['body_alignment']} | HIP: {metrics['hip_status']}",
            (20, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

    def _draw_curl_overlays(self, img, metrics):
        h, _ = img.shape[:2]

        cv2.putText(
            img,
            f"SWING: {metrics['swing_status']}",
            (20, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

    def _draw_press_overlays(self, img, metrics):
        h, _ = img.shape[:2]

        cv2.putText(
            img,
            f"EXT: {metrics['extension_status']} | BACK: {metrics['back_arch_status']}",
            (20, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

    def _draw_lunge_overlays(self, img, metrics):
        h, _ = img.shape[:2]

        cv2.putText(
            img,
            f"BALANCE: {metrics['balance_status']}",
            (20, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

    def recv(self , frame):
        img = np.asarray(
            cv2.flip(frame.to_ndarray(format = "bgr24") , 1),
            dtype=np.uint8
        )


        #Converts data in ml model format
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=cv2.cvtColor(img , cv2.COLOR_RGB2BGR)
        )


        self._frame_timestamp_ms += 30

        result = self._landmarker.detect_for_video(mp_image , self._frame_timestamp_ms)

        if result.pose_landmarks:
            landmarks = result.pose_landmarks[0]

            self._draw_skeleton(img , landmarks)

            ex_type = self.get_exercise()

            detectors = self._detectors.get(ex_type)

            if detectors:
                metrics = detectors.process(landmarks)

                self._draw_overlays(img , metrics , ex_type)
                self.set_latest_metrics(metrics)


        else:
            self._draw_no_pose_warnings(img)

        return av.VideoFrame.from_ndarray(img , format="bgr24")
    
# python3
#
# Copyright 2019 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Example using TF Lite to detect objects with the Raspberry Pi camera."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from operator import attrgetter

import argparse
import io
import re
import time

import numpy as np
import picamera

from PIL import Image
from tflite_runtime.interpreter import Interpreter

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

FRAMERATE = 1


def load_labels(path):
  """Loads the labels file. Supports files with or without index numbers."""
  with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    labels = []
    for row_number, content in enumerate(lines):
      pair = re.split(r'[:\s]+', content.strip(), maxsplit=1)
      #if len(pair) == 2 and pair[0].strip().isdigit():
      labels.append(np.array([pair[0].strip(),pair[1]]))
      #else:
      #  labels.append(pair[0].strip())
  return np.array(labels)


def set_input_tensor(interpreter, image):
  """Sets the input tensor."""
  tensor_index = interpreter.get_input_details()[0]['index']
  input_tensor = interpreter.tensor(tensor_index)()[0]
  input_tensor[:, :] = image


def get_output_tensor(interpreter, index):
  """Returns the output tensor at the given index."""
  output_details = interpreter.get_output_details()[index]
  tensor = np.squeeze(interpreter.get_tensor(output_details['index']))
  return tensor


def detect_objects(interpreter, image):
  """Returns a list of detection results, each a dictionary of object info."""
  set_input_tensor(interpreter, image)
  interpreter.invoke()

  # Get all output details
  #boxes = get_output_tensor(interpreter, 0)
  classes = get_output_tensor(interpreter, 1)
  scores = get_output_tensor(interpreter, 2)
  #count = int(get_output_tensor(interpreter, 3))

  #results = []
  #for i in range(count):
  #  if scores[i] >= threshold:
  #    result = {
  #        #'bounding_box': boxes[i],
  #        'class_id': classes[i],
   #       'score': scores[i]
   #   }
   #   results.append(result)
      
      
  #print("detection results:\n" + str(results))
  #return results
  return np.array([int(_class) for _class in classes]), np.array(scores)

# Returns the classification with the highest score
#def highest_score_class(results, labels):
#  obj = max(results, key=attrgetter('score'))
#  classification = labels[obj['class_id']]
 # return classification

# Captures an image and returns the classification
# update to take a method to update variables
def capture_class(update_detections):
  default_labels = "files/coco_labels.txt"
  default_model = "files/detect.tflite"
  default_threshold = .3

  labels = load_labels(default_labels)
  label_nums = labels[:0].astype(int)
  label_names = labels[:1]  
  
  interpreter = Interpreter(default_model)
  interpreter.allocate_tensors()
  _, input_height, input_width, _ = interpreter.get_input_details()[0]['shape']

  with picamera.PiCamera(
      resolution=(CAMERA_WIDTH, CAMERA_HEIGHT), framerate=FRAMERATE) as camera:
    camera.start_preview()
    try:
      time.sleep(0.2)
      stream = io.BytesIO()
      camera.capture(stream, format='jpeg', use_video_port=True)
      stream.seek(0)
      image = Image.open(stream).convert('RGB').resize(
          (input_width, input_height), Image.ANTIALIAS)

      classes, scores = detect_objects(interpreter, image)
      
      detected_indeces = np.where(scores > default_threshold, True, False)
      detected_classes = classes[detected_indeces].astype(int)
      
      print("detected classes: " + str(detected_classes))
      
      detected_labels = []
      
      for x in detected_classes:
        index = np.where(label_nums == x, True, False)
        detected_label = label_names[index]
        
        print("detected label: " + str(detected_label))
        
        if detected_label.size > 0:
            detected_labels.append(detected_label[0])
      
      print("detected labels: " + str(detected_labels))
      
      person = "person" in detected_labels
      stop_sign = "stop_sign" in detected_labels
      
      print("Person: " + str(person))
      print("Stop sign: " + str(stop_sign))
      
      update_detections(person, stop_sign)
      
      return

    finally:
      stream.seek(0)
      stream.truncate()
      camera.stop_preview()
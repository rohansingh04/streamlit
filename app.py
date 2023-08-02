# import os
# import json
# from flask import Flask, render_template, request

# app = Flask(__name__)

# # Function to read annotation data from a JSON file
# def read_annotations_data(video_file):
#     annotation_file = os.path.join(app.static_folder, 'annotations', video_file.replace('.mp4', '.json'))
#     with open(annotation_file, 'r') as file:
#         return json.load(file)

# @app.route('/')
# def index():
#     # Get a list of video files in the "videos" directory with the .mpg, .mpeg, and .mp4 extensions
#     videos_dir = os.path.join(app.static_folder, 'videos')
#     video_files = [f for f in os.listdir(videos_dir) if f.lower().endswith(('.mpg', '.mpeg', '.mp4'))]

#     return render_template('index.html', video_files=video_files)

# @app.route('/streamlit')
# def streamlit():
#     # Get the selected video from the query parameter in the URL
#     selected_video = request.args.get('video_file')

#     # Read annotation data for the selected video
#     annotations_data = read_annotations_data(selected_video)

#     return render_template('streamlit_video.html', video_file=f'videos/{selected_video}', annotations_data=annotations_data)

# if __name__ == '__main__':
#     app.run(debug=True)

import os
import json
import re
import cv2 as cv
from flask import Flask, render_template, request, render_template_string

app = Flask(__name__)

# Function to read annotation data from a JSON file
def read_annotations_data(video_file):
    annotation_file = os.path.join(app.static_folder, 'annotations', video_file.replace('.mp4', '.json'))
    with open(annotation_file, 'r') as file:
        return json.load(file)

# Function to perform OCR and plot bounding boxes on frames
def plot_ocr_frame(frame, txt_locs, bounds):
    """
    Get the scalar distance value and plot it on the region of interest
    """
    dist_ocr = -1
    # Draw the provided ocr text region bounds
    dx, dy, dw, dh = bounds
    dtl = (int(dx - dw / 2), int(dy - dh / 2))
    dbr = (int(dx + dw / 2), int(dy + dh / 2))
    cv.rectangle(frame, dtl, dbr, color=(255, 0, 0), thickness=1)

    # Draw the detected text regions
    for (bbox, text, prob) in txt_locs:
        (tl, tr, br, bl) = bbox
        tl = (int(tl[0] + dtl[0]), int(tl[1] + dtl[1]))
        br = (int(br[0] + dtl[0]), int(br[1] + dtl[1]))
        cv.rectangle(frame, tl, br, color=(0, 255, 0), thickness=1)
        cv.putText(frame, text, (tl[0], tl[1] - 5), cv.FONT_HERSHEY_SIMPLEX, fontScale=0.4, color=(0, 255, 0), thickness=1)
        # Get the final distance value
        if len(text) > 2:
            if "/" in text:
                text = text.split("/")[0]
            # extract the continuous digits
            digits = re.findall(r"[-+]?\d*\.\d+|\d+", text)
            if len(digits) > 0:
                dist_ocr = float(digits[0])

    if dist_ocr >= 0:
        # Draw OCR on the image
        cv.putText(frame, "{}".format(dist_ocr), (dtl[0], dtl[1] - 10), cv.FONT_HERSHEY_SIMPLEX, fontScale=0.6,
                   color=(255, 0, 0), thickness=2)
    return dist_ocr

@app.route('/')
def index():
    # Get a list of video files in the "videos" directory with the .mpg, .mpeg, and .mp4 extensions
    videos_dir = os.path.join(app.static_folder, 'videos')
    video_files = [f for f in os.listdir(videos_dir) if f.lower().endswith(('.mpg', '.mpeg', '.mp4'))]

    return render_template('index.html', video_files=video_files)

@app.route('/streamlit')
def streamlit():
    # Get the selected video from the query parameter in the URL
    selected_video = request.args.get('video_file')

    # Read annotation data for the selected video
    annotations_data = read_annotations_data(selected_video)

    # Load the HTML template and pass the annotations data to it
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'streamlit_video.html')
    with open(template_path, 'r') as template_file:
        template = template_file.read()

    # Create the video file path
    video_file_path = os.path.join('videos', selected_video)

    # Render the template with the video file path and annotations data
    rendered_template = render_template_string(template, video_file=video_file_path, annotations_data=annotations_data)

    return rendered_template

if __name__ == '__main__':
    app.run(debug=True)

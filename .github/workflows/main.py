from kivy.core.window import Window
Window.size = (1280, 720)
try:
    from android.storage import primary_external_storage_path
    import os

    image_library_path = os.path.join(primary_external_storage_path(), 'ImageLibrary')
    os.makedirs(image_library_path, exist_ok=True)
except ImportError:
    pass


from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from kivy.graphics import Rectangle
from kivy.uix.popup import Popup
from kivy.graphics import Ellipse

import cv2
import face_recognition
import numpy as np
import datetime
import os
import csv
import playsound
import time

class RoundedButton(ButtonBehavior, Label):
    def __init__(self, **kwargs):
        super(RoundedButton, self).__init__(**kwargs)
        with self.canvas.before:
            Color(0x00/255.0, 0x80/255.0, 0x35/255.0, 1)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[10])
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class CircaApp(App):
    def __init__(self, **kwargs):
        super(CircaApp, self).__init__(**kwargs)
        self.save_location = 'storage/emulated/0/Documents'

    def create_csv_file(self):
        file_path = os.path.join(self.save_location, 'detections.csv')
        if not os.path.exists(file_path):
            with open(file_path, mode='x') as file:
                writer = csv.writer(file)
                writer.writerow(['Name', 'Date Time'])
    def build(self):
        # Create the main layout
        main_layout = BoxLayout(orientation='vertical')
        main_layout.background_color = (0x80/255.0, 0x08/255.0, 0x00/255.0, 1)

        # Create the main layout
        help_layout = FloatLayout()
        
        # Add a small circle button on the top right corner
        help_button = Button(text='?', size_hint=(None, None), size=(50, 50), pos_hint={'right': 1, 'top': 1})
        help_button.background_color = (0, 0, 0, 0)
        help_button.background_normal = ''
        help_button.background_down = ''
        help_button.border = (0, 0, 0, 0)
        with help_button.canvas.before:
            Color(1, 1, 1, 1)
            Ellipse(size=help_button.size, pos=help_button.pos)
        help_button.bind(on_press=self.show_help)
        main_layout.add_widget(help_button)

        # Add a canvas instruction to set the background color
        with main_layout.canvas.before:
            Color(0x80/255.0, 0x08/255.0, 0x00/255.0, 1)  # Set the color to 800800
            self.rect = Rectangle(size=main_layout.size, pos=main_layout.pos)
        main_layout.bind(size=self._update_rect, pos=self._update_rect)

        # Add the title label to the main layout
        # Set the size_hint_y property to None and specify a fixed height for the title label
        title_label = Label(text='CIRCA', font_size=44, size_hint_y=None, height=54)
        main_layout.add_widget(title_label)

        # Create a layout for the video stream and buttons
        content_layout = BoxLayout(orientation='horizontal')
        main_layout.add_widget(content_layout)

        # Add the video stream to the left side of the content layout
        self.image = Image()
        content_layout.add_widget(self.image)

        # Create a black texture and set it as the initial texture of the Image widget
        black = [0 for _ in range(3 * 100 * 100)]
        black_texture = Texture.create(size=(100, 100), colorfmt='rgb')
        black_texture.blit_buffer(bytes(black), colorfmt='rgb', bufferfmt='ubyte')
        self.image.texture = black_texture
        
        # Create a layout for the buttons
        button_layout = BoxLayout(orientation='vertical', size_hint=(None, 1), width=400)
        content_layout.add_widget(button_layout)

        # Add an empty label to fill the space above the buttons
        button_layout.add_widget(Label())

        # Calculate button size based on screen resolution
        screen_width = 1280
        screen_height = 720

        
        # Add the start button
        start_button = RoundedButton(text='Start', size_hint=(None, None), font_size=24)
        start_button.bind(on_press=self.start_video)
        button_layout.add_widget(start_button)

        # Add another empty label to fill the space below the buttons
        spacer_label = Label(size_hint_y=None, height=50)
        button_layout.add_widget(spacer_label)

        # Add the stop button
        stop_button = RoundedButton(text='Stop', size_hint=(None, None), font_size=24)
        stop_button.bind(on_press=self.stop_video)
        button_layout.add_widget(stop_button)

        # Add another empty label to fill the space below the buttons
        spacer_label = Label(size_hint_y=None, height=50)
        button_layout.add_widget(spacer_label)

        # Add the add images button
        add_images_button = RoundedButton(text='Add Images', size_hint=(None, None), font_size=24)
        add_images_button.bind(on_press=self.add_images)
        button_layout.add_widget(add_images_button)

        # Add another empty label to fill the space below the buttons
        button_layout.add_widget(Label())

        button_width = start_button.texture_size[0] + 160
        button_height = start_button.texture_size[1] + 80

        # Set the size of start_button
        start_button.size = (button_width, button_height)
        stop_button.size = (button_width, button_height)
        add_images_button.size = (button_width, button_height)
        

        # Initialize OpenCV video capture
        #self.capture = cv2.VideoCapture(0)

        return main_layout
    
    def show_help(self, instance):
        # Create a label with the help text
        help_text = 'Copyright Act\n\n“Copyright in the Philippines is governed by the Intellectual Property Code.\nIt covers original intellectual creations in the literary and artistic domain, as well as derivative works.\nProtection is granted automatically from the moment of creation and lasts for the life of the author/creator plus 50 years\nafter their death. Infringement occurs when there is a violation of the exclusive rights granted to the copyright owner.”'
        help_label = Label(text=help_text)

        # Create a popup with the help label as content
        help_popup = Popup(title='Help', content=help_label, size_hint=(0.8, 0.8))
        help_popup.open()

    def start_video(self, instance):
        # Load images of the attendants
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_records = set()
        dir_path = 'storage/emulated/0/ImageLibrary' # replace with the actual directory path
        for file_name in os.listdir(dir_path):
            img_path = os.path.join(dir_path, file_name)
            img = face_recognition.load_image_file(img_path)
            face_encoding = face_recognition.face_encodings(img)[0]
            self.known_face_encodings.append(face_encoding)
            self.known_face_names.append(os.path.splitext(file_name)[0])

        self.save_location = 'storage/emulated/0/Documents'
        self.create_csv_file()

        # Set video capture resolution
        cap_width = 240
        cap_height = 240

        # Use lower-quality face recognition and detection models
        self.face_recognition_model = 'hog'
        self.face_detection_model = 'hog'

        # Capture video frames
        #self.video_capture = cv2.VideoCapture("http://192.168.4.1:81/stream")
        self.video_capture = cv2.VideoCapture(0)
        self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, cap_width)
        self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, cap_height)

        Clock.schedule_interval(self.update, 1.0/30.0)

    def stop_video(self, instance):
        print("stop")
        Clock.unschedule(self.update)
        # Create a black texture and display it in the Image widget
        black = [0 for _ in range(3 * 100 * 100)]
        black_texture = Texture.create(size=(100, 100), colorfmt='rgb')
        black_texture.blit_buffer(bytes(black), colorfmt='rgb', bufferfmt='ubyte')
        self.image.texture = black_texture

    def update(self, dt):
        self.play_time = time.time()
        print("UPDATE")

        # Add a dictionary to store the last recorded time for each person
        self.last_recorded_time = {}
        ret, frame = self.video_capture.read()
        if ret:
            # Convert it to texture and display in the Image widget
            buf1 = cv2.flip(frame, 0)
            buf = buf1.tostring()
            texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.image.texture = texture1
            print('texture updated')

        if ret:
            # Convert it to texture and display in the Image widget
            buf1 = cv2.flip(frame, 0)
            buf = buf1.tostring()
            texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.image.texture = texture1

            # Resize the frame to reduce processing time
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            # Detect faces
            face_locations = face_recognition.face_locations(small_frame, model=self.face_detection_model)
            face_encodings = face_recognition.face_encodings(small_frame, face_locations, model=self.face_recognition_model)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                # Check if the face is a match for the attendants
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                name = "Unknown"
                if True in matches:
                    match_index = matches.index(True)
                    name = self.known_face_names[match_index]

                if name not in self.known_face_records and name != "Unknown":
                    now = datetime.datetime.now()
                    # Check if 20 hours have passed since the last time this person was recorded
                    if name not in self.last_recorded_time or (now - self.last_recorded_time[name]).total_seconds() > 20 * 60 * 60:
                        date_time = now.strftime("%Y-%m-%d %H:%M:%S")
                        with open(os.path.join(self.save_location,'detections.csv'), mode='a', newline='') as file:
                            writer = csv.writer(file)
                            writer.writerow([name, date_time])
                        self.known_face_records.add(name)
                        # Update the last recorded time for this person
                        self.last_recorded_time[name] = now
                        # Play a different sound if the face is new
                        playsound.playsound('voice1.wav')

                    # Play a sound if the face is recorded
                    if name in self.known_face_records and time.time() - self.play_time > 25:
                        playsound.playsound('voice2.wav')
                        self.play_time = time.time()


    def choose_save_location(self, instance):
        # Create a new directory and set it as save location 
        directory = 'storage/emulated/0/Documents/'
        os.makedirs(directory, exist_ok=True)
        self.save_location = directory

    def add_images(self, instance):
        # Create a file chooser to select images
        file_chooser = FileChooserListView(path='~', filters=['*.png', '*.jpg', '*.jpeg'])
        popup = Popup(title='Select Images', content=file_chooser, size_hint=(0.9, 0.9))
        file_chooser.bind(on_submit=self.add_selected_images)
        popup.open()

    def add_selected_images(self, instance, selection, touch):
        # Copy the selected images to the ImageLibrary folder
        import shutil
        for image_path in selection:
            shutil.copy(image_path, 'ImageLibrary/')
        instance.parent.parent.dismiss()

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

if __name__ == '__main__':
    CircaApp().run()


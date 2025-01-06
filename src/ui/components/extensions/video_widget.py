import sys
from PySide6.QtWidgets import QApplication, QFrame, QVBoxLayout, QPushButton, QSlider, QHBoxLayout
from PySide6.QtGui import QIcon
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import QUrl, Qt, QTimer, QSize


class VideoPlayer:
    def __init__(self, video_path, parent_frame):
        # Video Widget
        self.video_widget = QVideoWidget(parent_frame)

        # QMediaPlayer
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)

        # Set Video Widget to QFrame via layout
        self.frame_layout = QVBoxLayout(parent_frame)
        self.frame_layout.addWidget(self.video_widget)
        self.frame_layout.setContentsMargins(0, 0, 0, 0)
        self.frame_layout.setSpacing(0)

        # Timeline (Slider)
        self.timeline_slider = QSlider(Qt.Horizontal)
        self.timeline_slider.setRange(0, 100)
        self.timeline_slider.valueChanged.connect(self.set_position)
        self.frame_layout.addWidget(self.timeline_slider)

        # Playback Controls
        self.controls_layout = QHBoxLayout()

        # Frame-by-frame backward button
        self.frame_backward_button = QPushButton("⏪")
        self.frame_backward_button.setVisible(False)
        self.frame_backward_button.pressed.connect(self.start_rewind_hold)
        self.frame_backward_button.released.connect(self.stop_rewind_hold)
        self.controls_layout.addWidget(self.frame_backward_button)

        # Play/Pause Button
        # Play/Pause Button
        self.play_icon = QIcon("resources/icons/general/play.svg")
        self.pause_icon = QIcon("resources/icons/general/pause.svg")
        self.play_pause_button = QPushButton()
        self.play_pause_button.setStyleSheet("""
            background-color: white;
            border: none;
            width: 50px;  
            height: 10px;
        """)
        self.play_pause_button.setFixedWidth(50)
        self.play_pause_button.setFixedHeight(20)
        self.play_pause_button.setIcon(self.play_icon)
        self.play_pause_button.setIconSize(QSize(32, 32))
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        self.controls_layout.addWidget(self.play_pause_button)

        # Frame-by-frame forward button
        self.frame_forward_button = QPushButton("⏩")
        self.frame_forward_button.setVisible(False)
        self.frame_forward_button.pressed.connect(self.start_forward_hold)
        self.frame_forward_button.released.connect(self.stop_forward_hold)
        self.controls_layout.addWidget(self.frame_forward_button)

        self.frame_layout.addLayout(self.controls_layout)

        # Connect media signals
        self.media_player.durationChanged.connect(self.update_duration)
        self.media_player.positionChanged.connect(self.update_position)

        self.media_player.setSource(QUrl.fromLocalFile(video_path))

        # Timers for continuous forward/backward
        self.forward_timer = QTimer()
        self.forward_timer.timeout.connect(self.increment_forward)

        self.backward_timer = QTimer()
        self.backward_timer.timeout.connect(self.increment_backward)

        # Speed increments
        self.base_increment = 5000  # 5 seconds per tick initially
        self.increment = self.base_increment
        self.hold_time_ms = 0
        self.speed_increase_interval = 1000  # Increase speed every 1 second of hold
        self.speed_increase_amount = 5000  # Increase increments by 5 seconds every interval

        # Track whether keys are pressed
        self.right_key_held = False
        self.left_key_held = False

    def update_duration(self, duration):
        """Set the slider's maximum value to the video's duration."""
        self.timeline_slider.setRange(0, duration)

    def update_position(self, position):
        """Update the slider's value as the video plays."""
        self.timeline_slider.blockSignals(True)
        self.timeline_slider.setValue(position)
        self.timeline_slider.blockSignals(False)

    def set_position(self, position):
        """Set the video's playback position."""
        self.media_player.setPosition(position)

    def toggle_play_pause(self):
        """Toggle between play and pause."""
        if self.media_player.playbackState() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            self.play_pause_button.setIcon(self.play_icon)
        else:
            self.media_player.play()
            self.play_pause_button.setIcon(self.pause_icon)

    def start_forward_hold(self):
        """Start fast forwarding when button pressed."""
        self.start_hold(forward=True)

    def stop_forward_hold(self):
        """Stop fast forwarding when button released."""
        self.stop_hold(forward=True)

    def start_rewind_hold(self):
        """Start rewinding when button pressed."""
        self.start_hold(forward=False)

    def stop_rewind_hold(self):
        """Stop rewinding when button released."""
        self.stop_hold(forward=False)

    def start_hold(self, forward=True):
        """Common method to start hold timers."""
        self.increment = self.base_increment
        self.hold_time_ms = 0

        if forward:
            self.forward_timer.start(100)
        else:
            self.backward_timer.start(100)

    def stop_hold(self, forward=True):
        """Common method to stop hold timers."""
        if forward:
            self.forward_timer.stop()
        else:
            self.backward_timer.stop()

    def increment_forward(self):
        self.handle_increment(forward=True)

    def increment_backward(self):
        self.handle_increment(forward=False)

    def handle_increment(self, forward):
        """Increment position while holding button or key."""
        current_position = self.media_player.position()

        # Increase hold time and speed if necessary
        self.hold_time_ms += 100
        if self.hold_time_ms % self.speed_increase_interval == 0:
            self.increment += self.speed_increase_amount

        new_position = current_position + self.increment if forward else max(0, current_position - self.increment)
        self.media_player.setPosition(new_position)

    def handle_key_press(self, key):
        """Handle keyboard shortcuts (pressed event)."""
        if key == Qt.Key_Space:
            self.toggle_play_pause()
        elif key == Qt.Key_Right:
            if not self.right_key_held:
                self.right_key_held = True
                self.start_hold(forward=True)
        elif key == Qt.Key_Left:
            if not self.left_key_held:
                self.left_key_held = True
                self.start_hold(forward=False)

    def handle_key_release(self, key):
        """Handle key release event."""
        if key == Qt.Key_Right and self.right_key_held:
            self.right_key_held = False
            self.stop_hold(forward=True)
        elif key == Qt.Key_Left and self.left_key_held:
            self.left_key_held = False
            self.stop_hold(forward=False)


class MainWindow(QFrame):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Enhanced Video Player")
        self.resize(800, 600)

        # Specify the path to the video file
        video_path = "C:/Users/sknay/Videos/progress_video2.mp4"  # Replace with the actual path

        # Create the VideoPlayer instance with QFrame as input
        self.video_player = VideoPlayer(video_path, self)  # Pass video_path and self as parent_frame

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        self.video_player.handle_key_press(event.key())

    def keyReleaseEvent(self, event):
        super().keyReleaseEvent(event)
        self.video_player.handle_key_release(event.key())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QLabel, QVBoxLayout, QWidget, QMessageBox, QProgressBar
from PyQt5.QtCore import QTimer, QPropertyAnimation
from twilio.rest import Client
import geocoder

class PersonalSafetyApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Personal Safety App")
        self.setGeometry(100, 100, 400, 300)

        # Initialize with some dummy phone numbers in E.164 format
        self.predefined_contacts = ["+", "+91"]

        # Twilio credentials
        self.twilio_sid = ''
        self.twilio_auth_token = ''
        self.twilio_phone_number = ''


        self.initUI()

    def initUI(self):
        # Create widgets
        self.sos_button = QPushButton("Emergency SOS")
        self.location_button = QPushButton("Get Location")
        self.alerts_button = QPushButton("Safety Alerts")
        self.add_contact_button = QPushButton("Add Emergency Contact")
        self.contact_input = QLineEdit()
        self.contact_label = QLabel("Emergency Contact:")
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)

        # Connect buttons to functions
        self.sos_button.clicked.connect(self.send_emergency_sos)
        self.location_button.clicked.connect(self.get_location)
        self.alerts_button.clicked.connect(self.show_safety_alerts)
        self.add_contact_button.clicked.connect(self.add_emergency_contact)

        # Set up layout
        layout = QVBoxLayout()
        layout.addWidget(self.sos_button)
        layout.addWidget(self.location_button)
        layout.addWidget(self.alerts_button)
        layout.addWidget(self.contact_label)
        layout.addWidget(self.contact_input)
        layout.addWidget(self.add_contact_button)
        layout.addWidget(self.progress_bar)

        # Create container widget and set layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def send_emergency_sos(self):
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(100)
        
        # Start progress bar animation
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(100)  # Update every 100 ms

        # Get the location and send SOS message
        self.get_location_and_send_sos()

    def update_progress(self):
        value = self.progress_bar.value()
        if value < 100:
            self.progress_bar.setValue(value + 10)
        else:
            self.timer.stop()
            self.fade_out_progress_bar()

    def fade_out_progress_bar(self):
        animation = QPropertyAnimation(self.progress_bar, b"windowOpacity")
        animation.setDuration(1000)  # Duration in milliseconds
        animation.setStartValue(1.0)  # Fully visible
        animation.setEndValue(0.0)  # Fully transparent
        animation.start()
        animation.finished.connect(lambda: self.progress_bar.setVisible(False))
        QMessageBox.information(self, "Emergency SOS", "Distress signal sent to your emergency contacts!")

    def get_location_and_send_sos(self):
        g = geocoder.ip('me')
        location = g.latlng
        if location:
            location_str = f"Latitude: {location[0]}, Longitude: {location[1]}"
            self.sos_contacts(location_str)
        else:
            QMessageBox.critical(self, "Location Error", "Unable to retrieve location")

    def sos_contacts(self, location):
        client = Client(self.twilio_sid, self.twilio_auth_token)
        for contact in self.predefined_contacts:
            try:
                message = client.messages.create(
                    body=f"Emergency SOS: Please check on me immediately! My location is {location}",
                    from_=self.twilio_phone_number,
                    to=contact
                )
                print(f"Sent message to {contact}, SID: {message.sid}")
            except Exception as e:
                print(f"Failed to send message to {contact}: {e}")

    def get_location(self):
        g = geocoder.ip('me')
        location = g.latlng
        if location:
            location_str = f"Latitude: {location[0]}, Longitude: {location[1]}"
            QMessageBox.information(self, "Current Location", location_str)
        else:
            QMessageBox.critical(self, "Location Error", "Unable to retrieve location")

    def show_safety_alerts(self):
        QMessageBox.information(self, "Safety Alert", "No current safety alerts in your area")

    def add_emergency_contact(self):
        contact = self.contact_input.text()
        if contact:
            # Validate phone number format
            if contact.startswith('+') and len(contact) > 10:
                self.predefined_contacts.append(contact)
                QMessageBox.information(self, "Contact Added", f"Emergency contact '{contact}' added successfully!")
                self.contact_input.clear()
            else:
                QMessageBox.warning(self, "Input Error", "Please enter a valid phone number in E.164 format")
        else:
            QMessageBox.warning(self, "Input Error", "Please enter a contact name")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = PersonalSafetyApp()
    mainWin.show()
    sys.exit(app.exec_())
f

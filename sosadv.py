import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLineEdit, QLabel, 
                             QVBoxLayout, QHBoxLayout, QWidget, QMessageBox, QProgressBar, 
                             QTextEdit, QComboBox, QFormLayout, QCheckBox)
from PyQt5.QtCore import QTimer, QPropertyAnimation, Qt
from PyQt5.QtGui import QFont
from twilio.rest import Client
import geocoder
import webbrowser
import requests  # For weather alerts

class PersonalSafetyApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Personal Safety App")
        self.setGeometry(100, 100, 800, 500)

        # Initialize with some dummy phone numbers in E.164 format
        self.predefined_contacts = ["+", "+91"]

        # Twilio credentials
        self.twilio_sid = ''
        self.twilio_auth_token = ''
        self.twilio_phone_number = ''

        # User profile data
        self.user_profile = {
            'name': '',
            'phone': ''
        }

        # Initialize settings
        self.dark_mode = False
        self.check_in_interval = 10  # Default to 10 minutes

        self.initUI()

    def initUI(self):
        # Set font and style
        font = QFont("Arial", 12)
        self.setFont(font)
        self.setStyleSheet("background-color: white; color: black;")

        # Create widgets
        self.sos_button = QPushButton("Emergency SOS")
        self.location_button = QPushButton("Get Location")
        self.alerts_button = QPushButton("Safety Alerts")
        self.add_contact_button = QPushButton("Add Contact")
        self.edit_contact_button = QPushButton("Edit Contact")
        self.remove_contact_button = QPushButton("Remove Contact")
        self.user_profile_button = QPushButton("User Profile")
        self.safety_tips_button = QPushButton("Safety Tips")
        self.theme_toggle_button = QPushButton("Toggle Dark Mode")
        self.incident_report_button = QPushButton("Report Incident")
        self.check_in_button = QPushButton("Set Safety Check-in")
        self.weather_alert_button = QPushButton("Weather Alerts")
        self.nearby_services_button = QPushButton("Nearby Safety Services")
        self.location_history_button = QPushButton("Location History")
        self.help_center_button = QPushButton("Help Center")

        self.contact_input = QLineEdit()
        self.contact_label = QLabel("Emergency Contact:")
        self.contact_list = QComboBox()
        self.contact_list.addItems(self.predefined_contacts)
        
        self.user_name_input = QLineEdit()
        self.user_phone_input = QLineEdit()
        self.profile_name_label = QLabel("Name:")
        self.profile_phone_label = QLabel("Phone:")
        
        self.safety_tips_text = QTextEdit()
        self.safety_tips_text.setReadOnly(True)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)

        self.check_in_checkbox = QCheckBox("Enable periodic safety check-ins")
        self.check_in_checkbox.setChecked(False)
        
        self.incident_form = QTextEdit()
        self.incident_form.setPlaceholderText("Describe the incident here...")
        self.incident_form.setVisible(False)

        # Connect buttons to functions
        self.sos_button.clicked.connect(self.send_emergency_sos)
        self.location_button.clicked.connect(self.get_location)
        self.alerts_button.clicked.connect(self.show_safety_alerts)
        self.add_contact_button.clicked.connect(self.add_emergency_contact)
        self.edit_contact_button.clicked.connect(self.edit_emergency_contact)
        self.remove_contact_button.clicked.connect(self.remove_emergency_contact)
        self.user_profile_button.clicked.connect(self.show_user_profile)
        self.safety_tips_button.clicked.connect(self.show_safety_tips)
        self.theme_toggle_button.clicked.connect(self.toggle_theme)
        self.incident_report_button.clicked.connect(self.toggle_incident_report)
        self.check_in_button.clicked.connect(self.set_safety_check_in)
        self.weather_alert_button.clicked.connect(self.show_weather_alerts)
        self.nearby_services_button.clicked.connect(self.show_nearby_services)
        self.location_history_button.clicked.connect(self.show_location_history)
        self.help_center_button.clicked.connect(self.show_help_center)

        # Layouts
        main_layout = QVBoxLayout()

        # Header Layout
        header_layout = QHBoxLayout()
        header_layout.addWidget(self.sos_button)
        header_layout.addWidget(self.location_button)
        header_layout.addWidget(self.alerts_button)
        header_layout.addWidget(self.weather_alert_button)
        header_layout.addWidget(self.theme_toggle_button)

        # Contact Management Layout
        contact_layout = QVBoxLayout()
        contact_layout.addWidget(self.contact_label)
        contact_layout.addWidget(self.contact_input)
        contact_layout.addWidget(self.add_contact_button)
        contact_layout.addWidget(self.edit_contact_button)
        contact_layout.addWidget(self.remove_contact_button)
        contact_layout.addWidget(self.contact_list)

        # User Profile Layout
        profile_layout = QVBoxLayout()
        profile_layout.addWidget(self.profile_name_label)
        profile_layout.addWidget(self.user_name_input)
        profile_layout.addWidget(self.profile_phone_label)
        profile_layout.addWidget(self.user_phone_input)
        profile_layout.addWidget(self.user_profile_button)

        # Safety Tips Layout
        safety_tips_layout = QVBoxLayout()
        safety_tips_layout.addWidget(self.safety_tips_button)
        safety_tips_layout.addWidget(self.safety_tips_text)

        # Incident Report Layout
        incident_report_layout = QVBoxLayout()
        incident_report_layout.addWidget(self.incident_report_button)
        incident_report_layout.addWidget(self.incident_form)
        incident_report_layout.addWidget(self.check_in_checkbox)
        incident_report_layout.addWidget(self.check_in_button)

        # Additional Features Layout
        additional_features_layout = QVBoxLayout()
        additional_features_layout.addWidget(self.nearby_services_button)
        additional_features_layout.addWidget(self.location_history_button)
        additional_features_layout.addWidget(self.help_center_button)

        # Add all layouts to main layout
        main_layout.addLayout(header_layout)
        main_layout.addLayout(contact_layout)
        main_layout.addLayout(profile_layout)
        main_layout.addLayout(safety_tips_layout)
        main_layout.addLayout(incident_report_layout)
        main_layout.addLayout(additional_features_layout)
        main_layout.addWidget(self.progress_bar)

        # Create container widget and set layout
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Load safety tips
        self.load_safety_tips()

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
            if contact.startswith('+') and len(contact) > 10:
                self.predefined_contacts.append(contact)
                self.contact_list.addItem(contact)
                QMessageBox.information(self, "Contact Added", f"Emergency contact '{contact}' added successfully!")
                self.contact_input.clear()
            else:
                QMessageBox.warning(self, "Input Error", "Please enter a valid phone number in E.164 format")
        else:
            QMessageBox.warning(self, "Input Error", "Please enter a contact name")

    def edit_emergency_contact(self):
        selected_contact = self.contact_list.currentText()
        if selected_contact:
            new_contact = self.contact_input.text()
            if new_contact and new_contact.startswith('+') and len(new_contact) > 10:
                index = self.contact_list.currentIndex()
                self.predefined_contacts[index] = new_contact
                self.contact_list.setItemText(index, new_contact)
                QMessageBox.information(self, "Contact Edited", f"Emergency contact updated to '{new_contact}'!")
                self.contact_input.clear()
            else:
                QMessageBox.warning(self, "Input Error", "Please enter a valid phone number in E.164 format")
        else:
            QMessageBox.warning(self, "Selection Error", "Please select a contact to edit")

    def remove_emergency_contact(self):
        selected_contact = self.contact_list.currentText()
        if selected_contact:
            self.predefined_contacts.remove(selected_contact)
            self.contact_list.removeItem(self.contact_list.currentIndex())
            QMessageBox.information(self, "Contact Removed", f"Emergency contact '{selected_contact}' removed successfully!")
        else:
            QMessageBox.warning(self, "Selection Error", "Please select a contact to remove")

    def show_user_profile(self):
        name = self.user_name_input.text()
        phone = self.user_phone_input.text()
        if name and phone:
            self.user_profile['name'] = name
            self.user_profile['phone'] = phone
            QMessageBox.information(self, "User Profile", f"Name: {name}\nPhone: {phone}")
        else:
            QMessageBox.warning(self, "Input Error", "Please enter both name and phone number")

    def load_safety_tips(self):
        # Load safety tips from a file or any other source
        self.safety_tips_text.setPlainText("1. Always be aware of your surroundings.\n2. Avoid walking alone at night.\n3. Keep your phone fully charged.\n4. Trust your instincts. If something feels off, take action.")

    def show_safety_tips(self):
        self.safety_tips_text.setVisible(True)

    def toggle_theme(self):
        if self.dark_mode:
            self.setStyleSheet("background-color: white; color: black;")
            self.theme_toggle_button.setText("Toggle Dark Mode")
        else:
            self.setStyleSheet("background-color: black; color: white;")
            self.theme_toggle_button.setText("Toggle Light Mode")
        self.dark_mode = not self.dark_mode

    def toggle_incident_report(self):
        self.incident_form.setVisible(not self.incident_form.isVisible())

    def set_safety_check_in(self):
        if self.check_in_checkbox.isChecked():
            QMessageBox.information(self, "Safety Check-in", f"Safety check-ins are set to {self.check_in_interval} minutes.")
        else:
            QMessageBox.information(self, "Safety Check-in", "Periodic safety check-ins are disabled.")

    def show_weather_alerts(self):
        # Fetch weather alerts from a weather API
        # This is a placeholder. Replace with real API call.
        weather_info = "Severe thunderstorm warning in your area."
        QMessageBox.information(self, "Weather Alerts", weather_info)

    def show_nearby_services(self):
        # Open a web browser to show nearby safety services
        webbrowser.open("https://www.google.com/maps/search/nearest+police+station")

    def show_location_history(self):
        # Placeholder for location history
        QMessageBox.information(self, "Location History", "Showing location history is not yet implemented.")

    def show_help_center(self):
        # Open a web browser to show the help center
        webbrowser.open("https://www.example.com/help")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = PersonalSafetyApp()
    mainWin.show()
    sys.exit(app.exec_())


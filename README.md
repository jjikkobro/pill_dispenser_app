# Automatic Pill Dispenser Display Interface
![image](https://github.com/user-attachments/assets/cc128925-ccea-49a7-b3e5-e09eeb25f013)
This project is an interactive Automatic Pill Dispenser with a display interface, designed to assist with pill management and scheduling. The dispenser provides convenient functionalities such as voice-recognized scheduling, manual pill dispensing, and automated dispensing based on pre-set times. It leverages Azure Speech-to-Text (STT), GPT-4 mini API, Arduino Serial Communication, and Dear PyGui for the display interface.

## Features
1. **Voice Recognition Scheduling**

- Uses Azure STT to convert voice input to text.
- Text data is processed with GPT-4 mini API to generate structured JSON data.
- JSON data is stored in MySQL for scheduling.
- If the voice input lacks information (e.g., time, medication name), the system requests only the missing information for re-recording, enhancing efficiency and user experience.

2. **Manual Pill Dispensing**

- Allows users to dispense specific pills manually.
- Communicates with Arduino through Serial for motor control, managing up to 3 motors that handle separate pill containers.
- The motor system selects and dispenses pills from the designated container as per user choice.

3. **Automated Pill Dispensing**

- Scheduled pill dispensing feature integrates with a Web Application and Display Interface.
- Fetches scheduled information from MySQL, dispensing the correct pill at the pre-set time.
- Notifies the user via display and/or sound when the medication is ready for dispensing.

## Dependencies
- **Azure Speech-to-Text** for voice recognition.
- **GPT-4 mini API** for natural language processing.
- **Arduino** with Serial communication for motor control.
- **Dear PyGui** for the graphical display interface.
- **MySQL** for data storage.

## Usage
1. **Voice-activated Scheduling:**
Speak your schedule into the microphone. The system will analyze and save your schedule. If additional information is needed, it will prompt you to re-record only the missing details.

2. **Manual Dispensing:**
Select the pill container on the interface, and the system will dispense the chosen medication.

3. **Automated Dispensing:**
The system will automatically dispense scheduled medications at the correct times, notifying you through the display interface.

# ThunAI - Empowering Women Through AI-Powered Safety Solutions

## Project Overview

ThunAI is an innovative AI-powered safety application designed to proactively detect and respond to threats faced by women in their daily lives. Our solution leverages cutting-edge technologies like computer vision and real-time GPS tracking to create a comprehensive safety network.

## Key Features

### 🚨 AI-Powered Threat Detection

- Uses computer vision to analyze facial expressions and surrounding environment
- Detects distress signals automatically without manual intervention

### 📍 Real-Time GPS Tracking

- Continuously monitors user's location
- Shares live updates with trusted contacts and law enforcement
- Provides accurate location data during emergencies

### 📱 Multi-Device Integration

- Works seamlessly with smartphones and wearable devices
- Ensures accessibility in various situations

### ⚡ Instant Emergency Response

- One-touch emergency button for immediate alerts
- Automated notifications to emergency contacts and authorities
- AI chatbot provides real-time safety guidance

### 🗺️ Safety Heatmaps

- Visual representation of risk levels in different areas
- Uses historical incident data to identify high-risk zones

## Technical Implementation

### System Architecture

- Cloud-based infrastructure for fast data synchronization
- Real-time collaboration with law enforcement

### Tech Stack

- **Emergency Alerts**: Twilio & Firebase Admin
- **Location Tracking**: Google Maps API & Folium
- **Safety Points Locator**: Google Maps API
- **Community Support**: Streamlit & Firebase
- **Authentication**: Firebase Authentication & Streamlit-JS-Eval
- **Time-Based Response**: Datetime Module

## Getting Started

### Prerequisites

- Python 3.7+
- Google Maps API key
- Twilio account credentials

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/mithgx/ThunAI.git
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment variables:
   - Set your Google Maps API key
   - Add Twilio credentials (account SID, auth token, phone number)

### Running the Application

```bash
streamlit run app.py
```

## Future Enhancements

- Offline accessibility for areas with poor network coverage
- AI-driven predictive analytics for personalized risk assessments
- IoT-based wearable safety devices integration
- Biometric authentication for secure access

## Environment Variables

Create a `.env` file in the `ThunAI` directory with the following content:

```
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
POLICE_CONTACT_NUMBER=your_police_contact_number
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
```

You can use [python-dotenv](https://pypi.org/project/python-dotenv/) to load these automatically. All sensitive keys and tokens should be stored in this file and never committed to the repository.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

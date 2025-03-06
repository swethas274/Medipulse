from flask import Flask, request, jsonify
from twilio.rest import Client
import prediction

app = Flask(__name__)

# Twilio credentials (replace with your actual details)
TWILIO_SID = "ACd6a268fa0cc9a5aa22cfe7d7b837d625"
TWILIO_AUTH_TOKEN = "155a5a819c2593ac0e4169c031622ba4"
TWILIO_PHONE_NUMBER = "+17816751648"
RECIPIENT_PHONE_NUMBER = "+919789032405"

# Function to send SMS alert
def send_sms_alert():
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body="⚠ High stress detected! Immediate attention required.",
        from_=TWILIO_PHONE_NUMBER,
        to=RECIPIENT_PHONE_NUMBER
    )
    print(f"SMS sent: {message.sid}")

# Function to check cortisol level
def check_cortisol(data):
    """
    Takes a list of 6 sensor values and returns:
    - 2 for high stress (≥20)
    - 1 for moderate stress (12-19)
    - 0 for no significant stress (<12)
    """
    avg_value=prediction.predict_cortisol(data)
    
    if avg_value >= 20:
        return 2
    elif avg_value >= 12:
        return 1
    else:
        return 0

@app.route("/sensor_data", methods=["GET"])
def receive_get_sensor_data():
    try:
        # Extract 6 sensor values from URL parameters
        sensor_values = [
            float(request.args.get(f"s{i}")) for i in range(1, 7)
        ]

        stress_level = check_cortisol(sensor_values)

        if stress_level == 2:
            send_sms_alert()

        return jsonify({"status": "success", "stress_level": stress_level})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Route for POST (IoT sensor input)
@app.route("/sensor_data", methods=["POST"])
def receive_post_sensor_data():
    try:
        data = request.get_json()
        sensor_values = data.get("sensor_values", [])

        if len(sensor_values) != 6:
            return jsonify({"error": "Invalid sensor data"}), 400
        
        stress_level = check_cortisol(sensor_values)

        if stress_level == 2:
            send_sms_alert()

        return jsonify({"status": "success", "stress_level": stress_level})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
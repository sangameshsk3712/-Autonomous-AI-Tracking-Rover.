import cv2
import numpy as np
import socket
import time

# ==================================================
# 🌐 DYNAMIC NETWORK INTEGRATION
# ==================================================
PC_IP = "192.168.29.112"              # Your PC IP address
PORT = 5005                           # Free network port

# Combine the IP string cleanly to avoid truncation bugs
phone_ip_address = "192.168.29.172"
CAMERA_URL = "http://" + phone_ip_address + ":8080/video"

# Initialize our networking tools
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(f"[SYSTEM] Connecting directly to wireless camera at: {CAMERA_URL}")
cap = cv2.VideoCapture(CAMERA_URL)

if not cap.isOpened():
    print("\n==================================================================")
    print("[FATAL ERROR] Could not establish link to the phone stream.")
    print("1. Ensure your IP Webcam app server is active on your smartphone.")
    print("2. Confirm your PC and phone are on the exact same Wi-Fi router.")
    print("==================================================================")
    exit()

print("\n==================================================")
print("     MIT-TIER AUTONOMOUS MASTER CONTROL ONLINE    ")
print("==================================================")
print(" Show a BRIGHT GREEN object to guide the system automatically.")
print(" Press 'q' on your keyboard to close down safely.")
print("==================================================")

last_sent_command = "STOP"

while True:
    ret, frame = cap.read()
    if not ret:
        print("[ERROR] Lost connection to the camera channel.")
        break

    frame = cv2.flip(frame, 1)
    height, width, _ = frame.shape
    screen_center_x = int(width / 2)

    # Process image frames into HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # PRECISE CALIBRATION BOUNDS FOR BRIGHT GREEN
    lower_green = np.array([35, 100, 100])
    upper_green = np.array([85, 255, 255])

    mask = cv2.inRange(hsv, lower_green, upper_green)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    current_command = "STOP"

    if len(contours) > 0:
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)

        if area > 500:
            ((x, y), radius) = cv2.minEnclosingCircle(largest_contour)
            obj_x, obj_y = int(x), int(y)

            # Draw green tracking circle and red center dot on the screen
            cv2.circle(frame, (obj_x, obj_y), int(radius), (0, 255, 0), 2)
            cv2.circle(frame, (obj_x, obj_y), 5, (0, 0, 255), -1)

            # AI Autonomous Navigation
            if obj_x < (screen_center_x - 80):
                current_command = "LEFT"
            elif obj_x > (screen_center_x + 80):
                current_command = "RIGHT"
            else:
                if radius < 70:
                    current_command = "FORWARD"
                else:
                    current_command = "STOP"

    # Send data over Wi-Fi only if the decision has changed
    if current_command != last_sent_command:
        try:
            server_socket.sendto(current_command.encode(), (PC_IP, PORT))
            print(f"[WIFI AIR-BURST] -> Sent Navigation Logic: {current_command}")
            last_sent_command = current_command
        except Exception as e:
            pass

    # Draw guidelines on the processed output window
    cv2.line(frame, (screen_center_x, 0), (screen_center_x, height), (255, 255, 255), 1)
    cv2.putText(frame, f"AI OUTPUT: {current_command}", (20, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    cv2.imshow("1. Master Autonomous Driver View", frame)
    cv2.imshow("2. AI Filter Channel Mask", mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("\n[SYSTEM] Closing wireless communication pipelines...")
        break

cap.release()
server_socket.close()
cv2.destroyAllWindows()

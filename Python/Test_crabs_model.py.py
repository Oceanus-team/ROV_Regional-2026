import cv2
from ultralytics import YOLO

# 1. Load the model
model = YOLO(r'C:\Users\Rana\runs\detect\train3\weights\best.pt')

# Load the image to test
image_path = r'C:\Users\Rana\Downloads\caaa.png' 
frame = cv2.imread(image_path)

# Check if image loaded successfully
if frame is None:
    print(f"Error: Could not open or find the image '{image_path}'")
    exit()

# Run detection
results = model(frame)

green = 0

# Process results
for r in results:
    boxes = r.boxes
    
    for box in boxes:
        # Get class ID and Confidence
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])

        # Only count if it's a green crab and confidence > 50%
        if cls_id == 0 and conf > 0.5:
            green += 1
            
            # Draw bounding box
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"Green Crab {conf:.2f}", (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# 5. Display the count and the image
print(f"Total Green Crabs Detected: {green}")

cv2.putText(frame, f"Count: {green}", (20, 50), 
            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

cv2.imshow('MATE ROV Image Test', frame)

cv2.waitKey(0)
cv2.destroyAllWindows()
import os
import sys
import time
import cv2
import numpy as np
from ultralytics import YOLO

def main():
    # Load the YOLO model from file
    # Change "my_model.pt" to your actual model file path (e.g., "runs/detect/train/weights/best.pt")
    model_path = "my_model.pt"  
    
    # Check if the model file exists before trying to load it
    if not os.path.exists(model_path):
        print(f'ERROR: Model path {model_path} is invalid or model was not found.')
        sys.exit(0)  # Exit the program if model not found
        
    # Load the YOLO model and tell the user what's happening
    print(f"Loading model from {model_path}...")
    model = YOLO(model_path, task='detect')
    
    # Get the class names (chocolate types) that the model can detect
    labels = model.names
    print(f"Model loaded successfully. Classes: {labels}")
    
    # Start the webcam connection
    print("Initializing webcam...")
    cap = cv2.VideoCapture(0)  # 0 means the default webcam (first camera)
    
    # Make sure the webcam is working
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        sys.exit(0)  # Exit if webcam doesn't work
        
    # Tell user how to use the program
    print("Webcam initialized. Press 'q' to quit, 's' to save a screenshot.")
    
    # Set different colors for different candy types' bounding boxes
    # Each candy type will have its own color when displayed
    bbox_colors = [(164,120,87), (68,148,228), (93,97,209), (178,182,133), (88,159,106), 
                  (96,202,231), (159,124,168), (169,162,241), (98,118,150), (172,176,184)]
    
    # For measuring how fast our program runs (frames per second)
    fps_buffer = []  # Store recent frame times
    fps_avg_len = 30  # Calculate average over 30 frames
    
    # Main loop - keep running until user quits
    while True:
        # Start timing this frame (to calculate FPS)
        t_start = time.perf_counter()
        
        # Get a single image from the webcam
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture image")
            break  # Exit loop if we can't get an image
            
        # Use our YOLO model to find candy in the image
        results = model(frame, verbose=False)
        
        # Get the detection results (bounding boxes around candy)
        detections = results[0].boxes
        
        # Counter for how many candies we find
        object_count = 0
        
        # Process each candy the model found
        for i in range(len(detections)):
            # Get the box coordinates (where the candy is in the image)
            xyxy_tensor = detections[i].xyxy.cpu()
            xyxy = xyxy_tensor.numpy().squeeze()
            xmin, ymin, xmax, ymax = xyxy.astype(int)
            
            # Get what type of candy it is
            classidx = int(detections[i].cls.item())
            classname = labels[classidx]
            
            # Get how confident the model is (0-1) that this is candy
            conf = detections[i].conf.item()
            
            # Only show detections that are confident enough (above 50%)
            if conf > 0.5:
                # Pick a color for this candy type
                color = bbox_colors[classidx % 10]
                
                # Draw a rectangle around the candy
                cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)
                
                # Create a label with candy name and confidence percentage
                label = f'{classname}: {int(conf*100)}%'
                
                # Get the size of the text to create a background for it
                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                
                # Make sure the label doesn't go off the top of the screen
                label_ymin = max(ymin, labelSize[1] + 10)
                
                # Draw a filled rectangle behind the text (so it's easier to read)
                cv2.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), 
                              (xmin+labelSize[0], label_ymin+baseLine-10), color, cv2.FILLED)
                
                # Draw the text on top of the background rectangle
                cv2.putText(frame, label, (xmin, label_ymin-7), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
                
                # Increase our candy counter
                object_count = object_count + 1
        
        # Calculate how long this frame took to process
        t_stop = time.perf_counter()
        frame_rate_calc = 1.0 / (t_stop - t_start)  # FPS = 1 / time_per_frame
        
        # Keep track of recent frame rates
        if len(fps_buffer) >= fps_avg_len:
            fps_buffer.pop(0)  # Remove oldest entry if buffer is full
        fps_buffer.append(frame_rate_calc)  # Add new frame rate
        
        # Calculate the average FPS over recent frames
        avg_frame_rate = np.mean(fps_buffer)
        
        # Display the FPS in the top-left corner
        cv2.putText(frame, f'FPS: {avg_frame_rate:.2f}', (10, 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Display how many candies were detected
        cv2.putText(frame, f'Candy detected: {object_count}', (10, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Show the image with all our drawings on screen
        cv2.imshow('YOLO Candy Detection', frame)
        
        # Check if user pressed any keys
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):  # If user pressed 'q', quit the program
            break
        elif key == ord('s'):  # If user pressed 's', save the current image
            cv2.imwrite('candy_detection.jpg', frame)
            print("Screenshot saved as candy_detection.jpg")
    
    # When done, print final statistics
    print(f'Average FPS: {avg_frame_rate:.2f}')
    
    # Clean up: release webcam and close all windows
    cap.release()
    cv2.destroyAllWindows()

# This is where the program starts running
if __name__ == "__main__":
    main()
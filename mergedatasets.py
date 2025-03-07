import os
import shutil
from collections import defaultdict

def combine_yolo_exports(export_dirs, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "images"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "labels"), exist_ok=True)
    
    all_classes = set()
    class_mapping = {}
    
    for i, export_dir in enumerate(export_dirs):
        classes_file = os.path.join(export_dir, "classes.txt")
        if os.path.exists(classes_file):
            with open(classes_file, 'r') as f:
                classes = [line.strip() for line in f.readlines()]
                for cls in classes:
                    all_classes.add(cls)
    
    sorted_classes = sorted(list(all_classes))
    
    with open(os.path.join(output_dir, "classes.txt"), 'w') as f:
        for cls in sorted_classes:
            f.write(f"{cls}\n")
    
    for i, cls in enumerate(sorted_classes):
        class_mapping[cls] = i
    
    for export_dir in export_dirs:
        export_class_map = {}
        classes_file = os.path.join(export_dir, "classes.txt")
        
        if os.path.exists(classes_file):
            with open(classes_file, 'r') as f:
                classes = [line.strip() for line in f.readlines()]
                for i, cls in enumerate(classes):
                    export_class_map[i] = class_mapping[cls]
        
        images_dir = os.path.join(export_dir, "images")
        labels_dir = os.path.join(export_dir, "labels")
        
        if os.path.exists(images_dir) and os.path.exists(labels_dir):
            for image_file in os.listdir(images_dir):
                image_path = os.path.join(images_dir, image_file)
                if os.path.isfile(image_path):
                    base_name = os.path.splitext(image_file)[0]
                    label_file = f"{base_name}.txt"
                    label_path = os.path.join(labels_dir, label_file)
                    
                    dest_image_path = os.path.join(output_dir, "images", image_file)
                    dest_label_path = os.path.join(output_dir, "labels", label_file)
                    
                    if not os.path.exists(dest_image_path):
                        shutil.copy2(image_path, dest_image_path)
                    
                    if os.path.exists(label_path):
                        with open(label_path, 'r') as f:
                            lines = f.readlines()
                        
                        if not os.path.exists(dest_label_path):
                            with open(dest_label_path, 'w') as f:
                                for line in lines:
                                    parts = line.strip().split(' ')
                                    if len(parts) >= 5:
                                        class_id = int(parts[0])
                                        new_class_id = export_class_map.get(class_id, class_id)
                                        parts[0] = str(new_class_id)
                                        f.write(' '.join(parts) + '\n')
                        else:
                            with open(dest_label_path, 'a') as f:
                                for line in lines:
                                    parts = line.strip().split(' ')
                                    if len(parts) >= 5:
                                        class_id = int(parts[0])
                                        new_class_id = export_class_map.get(class_id, class_id)
                                        parts[0] = str(new_class_id)
                                        f.write(' '.join(parts) + '\n')
    
    print(f"Combined YOLO exports into {output_dir}")
    print(f"Final classes: {sorted_classes}")

if __name__ == "__main__":
    export_dirs = []
    while True:
        export_dir = input("Enter a Label Studio YOLO export directory (or press Enter to finish): ")
        if not export_dir:
            break
            
        # Clean up path by removing surrounding quotes
        export_dir = export_dir.strip('"\'')
        
        if os.path.isdir(export_dir):
            export_dirs.append(export_dir)
        else:
            print(f"Directory not found: {export_dir}")
    
    if export_dirs:
        output_dir = input("Enter the output directory: ")
        # Clean up output path by removing surrounding quotes
        output_dir = output_dir.strip('"\'')
        combine_yolo_exports(export_dirs, output_dir)
    else:
        print("No valid export directories provided.")
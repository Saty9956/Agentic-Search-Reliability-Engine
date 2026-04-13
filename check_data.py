import os

# Tumhara exact dataset path
DATA_DIR = r"C:\Users\Satyartha Shukla\Desktop\BPSS_Agentic_AI_Interview_Dataset\bpss_agentic_dataset"

def explore_directory(directory_path):
    print(f"--- Scanning Directory: {directory_path} ---\n")
    
    total_files = 0
    file_types = {}

    # os.walk() automatically saare subfolders ke andar traverse karta hai
    for root, dirs, files in os.walk(directory_path):
        
        # Root path se relative path nikalna taaki output clean dikhe
        folder_name = os.path.relpath(root, directory_path)
        if folder_name == '.':
            print("[Root Folder]")
        else:
            print(f"\n[Folder] -> {folder_name}")
        
        if not files and not dirs:
            print("   (Empty)")
            
        for file in files:
            print(f"   📄 {file}")
            total_files += 1
            
            # File extensions (formats) count karna
            ext = os.path.splitext(file)[1].lower()
            if ext == '':
                ext = 'No Extension'
            file_types[ext] = file_types.get(ext, 0) + 1

    # Final Summary Report
    print("\n" + "="*30)
    print("📊 DATASET SUMMARY")
    print("="*30)
    print(f"Total Files Found : {total_files}")
    for ext, count in file_types.items():
        print(f" -> {ext.upper():<10} : {count} files")
    print("="*30)

if __name__ == "__main__":
    if os.path.exists(DATA_DIR):
        explore_directory(DATA_DIR)
    else:
        print(f"❌ CRITICAL ERROR: The path '{DATA_DIR}' does not exist.")
        print("Please check if the folder is there or if the spelling is correct.")
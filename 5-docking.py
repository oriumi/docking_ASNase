import os
import subprocess
import time
import datetime

def update_status_header(file_path, status):
    with open(file_path, 'r+') as file:
        lines = file.readlines()
        file.seek(0)
        
        file.write(lines[0])
        file.write("\n")
        
        if status == 'running':
            file.write("⏳ Please, do not turn off the PC !!! 😊\n\n")
        elif status == 'completed':
            file.write("✅ All tasks have been completed. The PC can be turned off. 😊\n\n")
            
        file.writelines(lines[3:])
        file.truncate()

def run_all_variants():
    # Edit the line below for your files
    base_dir = '/home/your_pc_name/Documents/monomers'
    global_status_file = os.path.join(base_dir, 'docking_status.txt')
    
    # Edit the line below to include the path where your software is installed.
    docking_command = ['/home/your_pc_name/CCDC/ccdc-software/gold/GOLD/bin/gold_auto', 'gold.conf']

    start_time_str = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    
    with open(global_status_file, 'w') as file:
        file.write(f"📅🕔 {start_time_str} 📅🕔\n\n")
        file.write("⏳ Please, do not turn off the PC !!! 😊\n\n")

    for dir_name in os.listdir(base_dir):
        if dir_name.startswith('Variant') and dir_name.endswith('_monomer'):
            variant_dir = os.path.join(base_dir, dir_name)
            
            if os.path.isdir(variant_dir):
                print(f"\nProcessing folder: {variant_dir}")
                
                with open(global_status_file, 'a') as file:
                    file.write(f"📂 Starting processing for folder: {dir_name}\n")
                
                try:
                    result = subprocess.run(
                        docking_command,
                        cwd=variant_dir,
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    
                    with open(global_status_file, 'a') as file:
                        file.write("    ✅ Docking completed successfully.\n\n")

                except FileNotFoundError:
                    with open(global_status_file, 'a') as file:
                        file.write("❌ ERROR: Command 'gold_auto' not found.\n")
                        file.write("Check if it is in your $PATH or use the absolute path.\n")
                        file.write("-" * 20 + "\n\n")
                except subprocess.CalledProcessError as e:
                    with open(global_status_file, 'a') as file:
                        file.write("❌ ERROR: The docking command returned an error.\n")
                        file.write(f"Error output:\n{e.stderr}\n")
                        file.write("-" * 20 + "\n\n")
                except Exception as e:
                    with open(global_status_file, 'a') as file:
                        file.write(f"❌ UNEXPECTED ERROR: {e}\n")
                        file.write("-" * 20 + "\n\n")
    
    update_status_header(global_status_file, 'completed')
        
    print("\nDocking process completed for all variants. Check the file 'docking_status.txt'.")
    
run_all_variants()

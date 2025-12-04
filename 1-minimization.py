import os
import subprocess

base_dirs = [
    './L-ASNase',
]

def check_log(log_path):
    try:
        with open(log_path, "r") as f:
            lines = f.readlines()

        for line in reversed(lines):
            if "Steepest Descents converged to Fmax < 100" in line:
                return True
            if "did not reach the requested Fmax < 100" in line:
                return False
        return None
    except FileNotFoundError:
        print(f"[ERROR] File {log_path} not found.")
        return None
    except Exception as e:
        print(f"[ERROR] Failed to read {log_path}: {str(e)}")
        return None

for base_dir in base_dirs:
    print(f"\n📂 Processing directory: {base_dir}")

    if not os.path.isdir(base_dir):
        print(f"[ERROR] Directory '{base_dir}' does not exist or is not valid.")
        continue

    required_files = ["EM.mdp", "box_solv_ion.gro", "topol.top"]
    missing_files = [f for f in required_files if not os.path.exists(os.path.join(base_dir, f))]
    if missing_files:
        print(f"[ERROR] Missing files in {base_dir}: {', '.join(missing_files)}. Skipping.")
        continue

    log_path = os.path.join(base_dir, "EM.log")

    if not os.path.exists(log_path):
        print(f"[WARNING] Directory {base_dir} does not contain EM.log")
        continue

    status = check_log(log_path)

    if status is True:
        print(f"[OK] Convergence reached (Fmax < 100) in {log_path}.")
    elif status is False:
        print(f"[ERROR] Did not converge in {log_path}. Trying to rerun minimization...")
        
        for i in range(1, 5):
            tpr_file = f"EM_{i}.tpr"
            log_file = f"EM_{i}.log"
            print(f"[INFO] Attempt {i}: Running minimization for {tpr_file}...")
            
            try:
                subprocess.run(
                    f"gmx grompp -f EM.mdp -c box_solv_ion.gro -maxwarn 2 -p topol.top -o {tpr_file}",
                    cwd=base_dir,
                    shell=True,
                    check=True
                )
                subprocess.run(
                    f"gmx mdrun -v -deffnm EM_{i}",
                    cwd=base_dir,
                    shell=True,
                    check=True
                )
                new_log_path = os.path.join(base_dir, log_file)
                if os.path.exists(new_log_path):
                    new_status = check_log(new_log_path)
                    if new_status is True:
                        print(f"[OK] Convergence reached (Fmax < 100) in {new_log_path} on attempt {i}.")
                        break
                    else:
                        print(f"[ERROR] Attempt {i} did not converge in {new_log_path}.")
                else:
                    print(f"[ERROR] File {log_file} was not generated on attempt {i}.")
            except subprocess.CalledProcessError as e:
                print(f"[ERROR] Minimization execution failed on attempt {i}: {str(e)}")
                break
    else:
        print(f"[WARNING] Could not interpret EM.log in {log_path}.")

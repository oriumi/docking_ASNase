import os
import shutil
import subprocess

def run_gold_batch_setup():
    current_directory = os.getcwd()
    monomers_dir = os.path.join(current_directory, 'monomers')

    source_conf = 'gold.conf'
    # Edit the line below to include the path where your software is installed.
    gold_utils_path = "/home/your_pc_name/CCDC/ccdc-software/gold/GOLD/gold_utils"

    for variant_name in os.listdir(monomers_dir):
        if variant_name.startswith('Variant') and variant_name.endswith('_monomer'):
            variant_id = variant_name.split("Variant")[1].split("_monomer")[0]
            variant_folder = os.path.join(monomers_dir, variant_name)

            centroid_file_name = 'gold_activesite_aas.txt'
            destination_conf = os.path.join(variant_folder, source_conf)

            try:
                shutil.copyfile(os.path.join(current_directory, source_conf), destination_conf)
                print(f"gold.conf copied to: {variant_folder}")
            except FileNotFoundError:
                print(f"Error: '{source_conf}' not found in: {current_directory}")
                continue

            input_pdb = f"EM_Variant{variant_id}_monomer.pdb"
            output_pdb = f"EM_Variant{variant_id}_monomer_H.pdb"
            input_pdb_path = os.path.join(variant_folder, input_pdb)
            output_pdb_path = os.path.join(variant_folder, output_pdb)

            if not os.path.exists(input_pdb_path):
                print(f"Error: Input file '{input_pdb}' not found in: {variant_folder}")
                continue

            if os.path.exists(output_pdb_path):
                print(f"Warning: Output file '{output_pdb_path}' already exists. Removing...")
                os.remove(output_pdb_path)

            gold_utils_cmd = [
                gold_utils_path,
                "-protonate",
                "-i", input_pdb_path,
                "-o", output_pdb_path
            ]

            try:
                result = subprocess.run(gold_utils_cmd, capture_output=True, text=True, check=True)
                print(f"Protonation completed for {variant_name}: {output_pdb_path}")
                print(f"gold_utils output: {result.stdout}")
                if result.stderr:
                    print(f"gold_utils warnings/errors: {result.stderr}")
            except subprocess.CalledProcessError as e:
                print(f"Error running gold_utils for {variant_name}: {e}")
                print(f"Error output: {e.stderr}")
                continue
            except FileNotFoundError:
                print(f"Error: '{gold_utils_path}' not found.")
                continue

            centroid_file_path = os.path.join(variant_folder, centroid_file_name)
            if not os.path.exists(centroid_file_path):
                print(f"Error: '{centroid_file_name}' not found in: {variant_folder}")
                continue

            try:
                with open(destination_conf, 'r') as f:
                    conf_lines = f.readlines()

                new_conf_lines = []
                protein_datafile_updated = False
                cavity_file_updated = False

                for line in conf_lines:
                    if line.strip().startswith('cavity_file ='):
                        new_conf_lines.append(f"cavity_file = {centroid_file_name}\n")
                        cavity_file_updated = True
                    elif line.strip().startswith('protein_datafile ='):
                        new_conf_lines.append(f"protein_datafile = {output_pdb_path}\n")
                        protein_datafile_updated = True
                    else:
                        new_conf_lines.append(line)

                if not protein_datafile_updated:
                    print(f"Warning: 'protein_datafile =' not found in gold.conf for {variant_name}")
                if not cavity_file_updated:
                    print(f"Warning: 'cavity_file =' not found in gold.conf for {variant_name}")

                with open(destination_conf, 'w') as f:
                    f.writelines(new_conf_lines)

                print(f"gold.conf updated successfully in: {variant_folder}")
                print("-" * 20)

            except Exception as e:
                print(f"Error processing folder '{variant_name}': {e}")

    print("Batch setup completed for all variants.")

run_gold_batch_setup()

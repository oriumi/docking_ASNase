import os
import re

base_dir = "."

regex_force = re.compile(r"Maximum force\s*=\s*([\d\.Ee\+\-]+)")

global_status_path = os.path.join(base_dir, "replicated_status.txt")
with open(global_status_path, "w") as g:
    g.write("General summary of replicas:\n\n")

for dir_name in sorted(os.listdir(base_dir)):
    variant_dir = os.path.join(base_dir, dir_name)
    if not (os.path.isdir(variant_dir) and dir_name.startswith("Variant") and dir_name.endswith("_monomer")):
        continue

    print(f"\n📂 Processing: {dir_name}")

    forces = {}
    log_files = [f for f in os.listdir(variant_dir) if f.startswith("EM") and f.endswith(".log") and f != "EM.mdp"]

    for log_file in log_files:
        log_path = os.path.join(variant_dir, log_file)
        with open(log_path, "r", errors="ignore") as f:
            content = f.read()
        m = regex_force.search(content)
        if m:
            base_no_ext = os.path.splitext(log_file)[0]
            forces[base_no_ext] = float(m.group(1))

    if not forces:
        print("⚠️  No EM*.log containing 'Maximum force' found. Skipping folder.")
        continue

    sorted_forces = sorted(forces.items(), key=lambda x: x[1])
    best_base, best_f = sorted_forces[0]

    summary_path = os.path.join(variant_dir, "forces_summary.txt")
    with open(summary_path, "w") as out:
        out.write("Summary of maximum forces (kJ/mol/nm):\n\n")
        for base, val in sorted_forces:
            out.write(f"{base}.log: {val:.4f}\n")
        out.write(f"\nBest replica: {best_base}.log  (Maximum force = {best_f:.4f} kJ/mol/nm)\n")

    print(f"📝 Summary saved in: {summary_path}")
    print(f"✅ Best replica: {best_base}.log (Fmax={best_f:.2f})")

    with open(global_status_path, "a") as g:
        g.write(f"📂 {dir_name}\n")
        g.write(f"   📝 Summary saved in: {summary_path}\n")
        g.write(f"   ✅ Best replica: {best_base}.log (Fmax={best_f:.2f})\n\n")

    em_pattern_files = [f for f in os.listdir(variant_dir) if re.match(r"^EM(?:_\d+)?\..+$", f)]
    for fname in em_pattern_files:
        if fname == "EM.mdp":
            continue
        base_no_ext = os.path.splitext(fname)[0]
        if base_no_ext != best_base:
            try:
                os.remove(os.path.join(variant_dir, fname))
                print(f"🗑️  Removed: {fname}")
            except FileNotFoundError:
                pass

    if best_base != "EM":
        chosen_files = [f for f in os.listdir(variant_dir) if os.path.splitext(f)[0] == best_base]
        for fname in chosen_files:
            if fname == "EM.mdp":
                continue
            old_path = os.path.join(variant_dir, fname)
            ext = os.path.splitext(fname)[1]
            new_path = os.path.join(variant_dir, "EM" + ext)
            if os.path.exists(new_path):
                os.remove(new_path)
            os.rename(old_path, new_path)
            print(f"✏️  Renamed: {fname}  →  EM{ext}")

print("\n🎉 Done! All Variant folders have been processed.")
print(f"📑 Global summary saved in: {global_status_path}")

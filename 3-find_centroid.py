import os
from pymol import cmd

monomers_dir = "./monomers"

cmd.reinitialize()
cmd.load("6v2a_monomer.pdb")

folders = [
    d for d in os.listdir(monomers_dir)
    if os.path.isdir(os.path.join(monomers_dir, d))
    and d.startswith("Variant")
    and d.endswith("_monomer")
]

for folder in folders:
    variant = folder.split("Variant")[1].split("_monomer")[0]
    full_folder = os.path.join(monomers_dir, folder)
    model_name = f"EM_Variant{variant}_monomer"
    pdb_path = os.path.join(full_folder, f"EM_Variant{variant}_monomer.pdb")

    if not os.path.exists(pdb_path):
        print(f"PDB file not found in {full_folder}: {pdb_path}")
        continue

    cmd.load(pdb_path, model_name)

    try:
        rmsd = cmd.align("6v2a_monomer", model_name)[0]
        print(f"Alignment RMSD for {variant}: {rmsd:.3f}")
    except:
        print(f"Alignment error for {variant}. Skipping...")
        cmd.delete(model_name)
        continue

    cmd.remove("resn HOH")
    cmd.remove("resn WAT")

    cmd.select("lig", "hetatm and chain A and resn ASN and resi 401")
    lig_atoms = cmd.count_atoms("lig")
    print(f"Atom count in 'lig' for {variant}: {lig_atoms}")

    if lig_atoms == 0:
        print(f"Error: Ligand ASN 401 (chain A) not found for {variant}.")
        cmd.delete(model_name)
        continue

    cmd.show("sticks", "lig")

    cmd.select("pocket_6v2a", "byres (polymer within 5.0 of lig)")
    print(f"pocket_6v2a selection for {variant}: {cmd.count_atoms('pocket_6v2a')} atoms")

    cmd.select("pocket_model", f"{model_name} within 5.0 of pocket_6v2a")
    print(f"pocket_model selection for {variant}: {cmd.count_atoms('pocket_model')} atoms")

    cmd.select("near_model", "byres (polymer and pocket_model)")
    print(f"near_model selection for {variant}: {cmd.count_atoms('near_model')} atoms")

    atoms = cmd.get_model("near_model and name CA").atom

    if not atoms:
        print(f"No CA atoms found in 'near_model' selection for {variant}.")
        cmd.delete(model_name)
        cmd.delete("lig")
        cmd.delete("pocket_6v2a")
        cmd.delete("pocket_model")
        cmd.delete("near_model")
        continue

    x = sum(a.coord[0] for a in atoms) / len(atoms)
    y = sum(a.coord[1] for a in atoms) / len(atoms)
    z = sum(a.coord[2] for a in atoms) / len(atoms)
    print(f"Centroid (X, Y, Z) for {variant}: ({x}, {y}, {z})")

    cmd.pseudoatom("centroid_pocket", pos=[x, y, z])
    cmd.show("spheres", "centroid_pocket")
    cmd.color("red", "centroid_pocket")
    cmd.set("sphere_scale", 1.0, "centroid_pocket")

    cmd.select("pocket_residues", f"(byres ({model_name} within 8 of centroid_pocket) and polymer.protein)")

    cmd.show("cartoon", model_name)
    cmd.color("slate", f"{model_name} and not lig")

    cmd.show("cartoon", "6v2a_monomer")
    cmd.color("wheat", "6v2a_monomer and not lig")

    cmd.zoom("centroid_pocket", buffer=15)

    residues = []
    for a in cmd.get_model("pocket_residues and name CA").atom:
        residues.append((a.resi, a.resn, a.coord[0], a.coord[1], a.coord[2]))
    n_residues = len(residues)

    coordinates_path = os.path.join(full_folder, "coordinates.txt")

    with open(coordinates_path, "w") as f:
        print(f"Writing coordinates.txt to {coordinates_path}")
        f.write("Centroid coordinates X, Y and Z:\n")
        f.write(f"{x:10.3f} {y:10.3f} {z:10.3f}\n\n")
        f.write(f"{n_residues} amino acids within an 8 Å radius of the centroid:\n\n")
        f.write(f"{'Resi':>5} {'Resn':>5} {'X':>10} {'Y':>10} {'Z':>10}\n")
        f.write("-" * 45 + "\n")
        for resi, resn, cx, cy, cz in residues:
            f.write(f"{resi:>5} {resn:>5} {cx:10.3f} {cy:10.3f} {cz:10.3f}\n")
        f.write("\n" + "=" * 50 + "\n\n")

    residues_unique = []
    for resi, resn, _, _, _ in residues:
        tag = f"{resn}{resi}"
        if tag not in residues_unique:
            residues_unique.append(tag)

    gold_path = os.path.join(full_folder, "gold_activesite_aas.txt")
    with open(gold_path, "w") as f:
        print(f"Writing gold_activesite_aas.txt to {gold_path}")
        f.write("> <Gold.Protein.ActiveResidues>\n")
        f.write(" ".join(residues_unique) + "\n")

    cmd.bg_color("white")
    cmd.set("ray_trace_mode", 1)
    cmd.set("antialias", 2)
    cmd.set("ray_shadows", 0)
    cmd.set("ray_trace_gain", 0.1)
    cmd.set("ray_trace_disco_factor", 1)
    cmd.set("ray_trace_fog", 0.5)

    cmd.color("yellow", "lig")
    cmd.rebuild()
    cmd.refresh()

    image_path = os.path.join(full_folder, "centroid_pocket.png")
    cmd.png(image_path, width=2000, height=1800, dpi=300, ray=0)
    print(f"Image 'centroid_pocket.png' saved successfully for {variant} in {full_folder}!\n")
    print("=" * 20)

    cmd.delete(model_name)
    cmd.delete("lig")
    cmd.delete("pocket_6v2a")
    cmd.delete("pocket_model")
    cmd.delete("near_model")
    cmd.delete("centroid_pocket")
    cmd.delete("pocket_residues")

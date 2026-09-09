import subprocess, os, sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def run(cmd, cwd="."):
    print(f"\n>>> {cmd}")
    subprocess.run(cmd, shell=True, cwd=cwd, check=True)

csv_path = "data/generated/historical_data.csv"
if not os.path.exists(csv_path):
    run("python run_simulator.py", cwd="simulator")
else:
    print(f"{csv_path} already exists — skipping simulation. Delete it to force regeneration.")

run("python create_schema.py", cwd="db")
run("python load_data.py", cwd="db")

for model, script in [
    ("ml/models/occupancy_model.pkl", "train_occupancy_model.py"),
    ("ml/models/energy_model.pkl", "train_energy_model.py"),
    ("ml/models/anomaly_model.pkl", "train_anomaly_model.py"),
]:
    if not os.path.exists(model):
        run(f"python training/{script}", cwd="ml")
    else:
        print(f"{model} already exists — skipping training. Delete it to force retraining.")

print("\nPipeline complete.")
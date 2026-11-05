cat << 'EOF' > mine.py
import subprocess
import modal

quantus_image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("wget", "tar", "libssl-dev", "ocl-icd-opencl-dev", "ca-certificates")
    .run_commands(
        "wget https://github.com/andru-sho/wildrig-multi/releases/download/0.40.1/wildrig-multi-linux-0.40.1.tar.xz",
        "tar -xvf wildrig-multi-linux-0.40.1.tar.xz",
        "mv wildrig-multi wildrig"
    )
)

app = modal.App("quantus-kryptex-mining")

@app.function(
    image=quantus_image,
    gpu="H100",
    timeout=86400
)
def run_miner():
    WALLET_ADDRESS = "qzodqEtdBhugS8bVkDjsxcUToZ44ibTsFaeA1985QjTx4XfGe"
    WORKER_NAME = "modal_h100_kryptex"
    POOL = "qtc-sg.kryptex.network:7049"
    
    cmd = [
        "./wildrig",
        "--algo", "quantus",
        "--url", f"stratum+tcp://{POOL}",
        "--user", f"{WALLET_ADDRESS}.{WORKER_NAME}",
        "--pass", "x"
    ]
    
    print("=" * 60)
    print("Memulai Mining Quantus (QTC) di Kryptex SG via Modal.com")
    print(f"GPU    : NVIDIA H100")
    print(f"Pool   : {POOL}")
    print(f"Wallet : {WALLET_ADDRESS}")
    print("=" * 60)

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    
    for line in process.stdout:
        print(line, end="")

@app.local_entrypoint()
def main():
    print("Mengirimkan tugas mining ke server cloud Modal.com...")
    run_miner.remote()
EOF

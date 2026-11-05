cat << 'EOF' > mine.py
import subprocess
import modal

quantus_image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("wget", "tar", "libssl-dev", "ocl-icd-opencl-dev", "ca-certificates")
    .run_commands(
        "wget https://github.com/doktor83/SRBMiner-Multi/releases/download/3.8.3/SRBMiner-Multi-3-8-3-Linux.tar.gz",
        "tar -xvf SRBMiner-Multi-3-8-3-Linux.tar.gz",
        "mv SRBMiner-Multi-3-8-3 srbminer"
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
        "./srbminer/SRBMiner-MULTI",
        "--algorithm", "quantus",
        "--pool", POOL,
        "--wallet", f"{WALLET_ADDRESS}.{WORKER_NAME}",
        "--password", "x",
        "--disable-cpu"
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

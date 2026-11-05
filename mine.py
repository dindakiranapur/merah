import os
import subprocess
import modal

# 1. Menyiapkan Image kontainer Linux dengan dependensi CUDA dan SRBMiner
quantus_image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("wget", "tar", "libssl-dev", "ocl-icd-opencl-dev")
    .run_commands(
        "wget https://github.com/doktor83/SRBMiner-Multi/releases/download/1.2.9/SRBMiner-Multi-1-2-9-Linux.tar.gz",
        "tar -xvf SRBMiner-Multi-1-2-9-Linux.tar.gz",
        "mv SRBMiner-Multi-1-2-9 srbminer"
    )
)

app = modal.App("quantus-mining-app")

# 2. Mengalokasikan GPU H100 (GPU tertinggi di Modal)
@app.function(
    image=quantus_image,
    gpu="H100",  
    timeout=86400  # Durasi maksimum jalan (24 jam)
)
def run_miner():
    # Alamat Dompet Quantus Anda yang sudah dimasukkan
    WALLET_ADDRESS = "qzodqEtdBhugS8bVkDjsxcUToZ44ibTsFaeA1985QjTx4XfGe"
    WORKER_NAME = "modal_h100_worker"
    
    # Server Mining Pool (2Miners Asia)
    POOL = "asia-qtc.2miners.com:3636"
    
    # Perintah eksekusi penambangan
    cmd = [
        "./srbminer/SRBMiner-MULTI",
        "--algorithm", "quantus",
        "--pool", POOL,
        "--wallet", f"{WALLET_ADDRESS}.{WORKER_NAME}",
        "--password", "x",
        "--disable-cpu"
    ]
    
    print("=" * 50)
    print("Memulai Mining Quantus di Modal.com (GPU H100)...")
    print(f"Pool   : {POOL}")
    print(f"Wallet : {WALLET_ADDRESS}")
    print("=" * 50)

    # Menjalankan proses miner & menampilkan log real-time ke terminal
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    
    for line in process.stdout:
        print(line, end="")

@app.local_entrypoint()
def main():
    print("Mengirimkan tugas mining ke server cloud Modal.com...")
    run_miner.remote()

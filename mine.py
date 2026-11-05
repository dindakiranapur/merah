import subprocess
import modal

# Menyiapkan Image kontainer Linux dengan dependensi CUDA dan WildRig-Multi
quantus_image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("wget", "tar", "libssl-dev", "ocl-icd-opencl-dev", "ca-certificates")
    .run_commands(
        # Mengunduh wildrig-multi yang mendukung algoritma quantus
        "wget https://github.com/andru-sho/wildrig-multi/releases/download/0.40.1/wildrig-multi-linux-0.40.1.tar.xz",
        "tar -xvf wildrig-multi-linux-0.40.1.tar.xz",
        "mv wildrig-multi wildrig"
    )
)

app = modal.App("quantus-kryptex-mining")

# Menggunakan GPU tertinggi di Modal.com (NVIDIA H100)
@app.function(
    image=quantus_image,
    gpu="H100",  # Bisa diganti ke "H200" atau "A100" jika diperlukan kuota
    timeout=86400  # Timeout maksimum 24 jam per session
)
def run_miner():
    # Alamat dompet Quantus Anda
    WALLET_ADDRESS = "qzodqEtdBhugS8bVkDjsxcUToZ44ibTsFaeA1985QjTx4XfGe"
    WORKER_NAME = "modal_h100_kryptex"
    
    # Stratum Server Kryptex Singapura (SG)
    POOL = "qtc-sg.kryptex.network:7049"
    
    # Perintah eksekusi penambangan
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

    # Menjalankan proses miner dan menampilkan log real-time
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    
    for line in process.stdout:
        print(line, end="")

@app.local_entrypoint()
def main():
    print("Mengirimkan tugas mining ke server cloud Modal.com...")
    run_miner.remote()

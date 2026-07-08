import urllib.request
import tarfile
import os

def download_and_extract(url, target_dir, filename):
    os.makedirs(target_dir, exist_ok=True)
    filepath = os.path.join(target_dir, filename)
    print(f"Downloading {filename} from {url}...")
    
    # Download
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response, open(filepath, 'wb') as out_file:
        out_file.write(response.read())
    
    print(f"Extracting {filename}...")
    if filename.endswith(".tar.gz") or filename.endswith(".gz") or filename.endswith(".tar"):
        with tarfile.open(filepath, 'r:*') as tar:
            tar.extractall(path=target_dir)
            
    print(f"Done with {filename}.\n")

if __name__ == "__main__":
    home_dir = os.path.expanduser("~")
    
    # 1. Pandeia Data
    pandeia_dir = os.path.join(home_dir, "pandeia_data")
    pandeia_url = "https://stsci.box.com/shared/static/0yd1ks949ee38qbuj76ply0gj3m1cppu.gz"
    download_and_extract(pandeia_url, pandeia_dir, "pandeia_data.tar.gz")
    
    # 2. PySynphot Phoenix Models
    pysynphot_dir = os.path.join(home_dir, "pysynphot_data")
    phoenix_url = "https://archive.stsci.edu/hlsps/reference-atlases/hlsp_reference-atlases_hst_multi_pheonix-models_multi_v3_synphot5.tar"
    download_and_extract(phoenix_url, pysynphot_dir, "phoenix_models.tar")
    
    # 3. PySynphot Normalization Files
    norm_url = "https://archive.stsci.edu/hlsps/reference-atlases/hlsp_reference-atlases_hst_multi_everything_multi_v11_sed.tar"
    download_and_extract(norm_url, pysynphot_dir, "norm_files.tar")
    
    print("All downloads and extractions completed.")

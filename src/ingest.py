from pathlib import Path
import requests
import yaml
import zipfile

# Global variables
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

def download_file(url: str, destination: Path) -> None:
    # Download a file from a URL and save it to the specified destination path.
    response = requests.get(url, stream=True)
    response.raise_for_status()

    destination.parent.mkdir(parents=True, exist_ok=True)

    with destination.open("wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)

    with zipfile.ZipFile(destination, "r") as zip_file:
        zip_file.extractall(destination.parent)
    destination.unlink()

def initialize_directories() -> bool:
    RAW_DIR = DATA_DIR / "01_raw"

    directories = [
        "01_raw",
        "02_intermediate",
        "03_processed"
    ]

    # Check if files exist in the data/01_raw directory
    for directory in directories:
        (DATA_DIR / directory).mkdir(parents=True, exist_ok=True)
    if any(RAW_DIR.iterdir()):
        print(f"Files already exist in {RAW_DIR}. Skipping download.")
        return False
    return True

def main() -> None:
    # Initialize directories and check if files already exist
    if not initialize_directories():
        return

    # Download all quarterly ZIP files.
    config = yaml.safe_load((PROJECT_ROOT / "config.yml").read_text())
    YEAR = str(config["download"]["year"])
    BASE_URL = config["download"]["base_url"] + YEAR
    EXT = config["download"]["extension"]
    NUM_FILES = config["download"]["files"]

    # Download each quarterly file
    RAW_DIR = DATA_DIR / "01_raw"
    for n in range(1, NUM_FILES + 1):
        i = str(n)  # Convert to string for URL construction

        # Create data/01_raw/Q{i} directory if it doesn't exist
        quarter_dir = RAW_DIR / f"Q{i}"
        quarter_dir.mkdir(parents=True, exist_ok=True)

        # Construct URL and destination path
        url = f"{BASE_URL}q{i}{EXT}"
        zip_path = quarter_dir / f"Q{i}.zip"

        print(f"Downloading Q{i}...")
        print(f"\tURL: {url}")

        try:
            download_file(url, zip_path)
            print(f"\tSaved: {zip_path}\n")

        except requests.RequestException as error:
            print(f"\tERROR: Could not download Q{i} from {url}.")
            print(f"\t{error}\n")

if __name__ == "__main__":
    main()

import shutil
from pathlib import Path


directories_to_empty = [
    "../$Private/Customers/$Current/DMA/Repo/Dashboards-MODIFIED",
    "../$Private/Customers/$Current/DMA/Repo/Notebooks-MODIFIED"
    ]

for directory_to_empty in directories_to_empty:
    dir_path = Path(directory_to_empty)

    if dir_path.exists() and dir_path.is_dir():
        shutil.rmtree(dir_path)

    dir_path.mkdir(parents=True, exist_ok=True)

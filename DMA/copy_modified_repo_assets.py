import shutil

# source_dir = "../$Private/Customers/$Current/DMA/Repo/Dashboards-MODIFIED"
# destination_dir = "../$Private/Customers/$Current/DMA/Repo/Dashboards"

source_dir = "../$Private/Customers/$Current/DMA/Repo/Notebooks-MODIFIED"
destination_dir = "../$Private/Customers/$Current/DMA/Repo/Notebooks"

shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)

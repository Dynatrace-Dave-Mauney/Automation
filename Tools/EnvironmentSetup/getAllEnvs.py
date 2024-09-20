import os

env_keys = os.environ.keys()
for env_key in env_keys:
	print(f"setx {env_key} {os.environ.get(env_key, 'Not Set!')}")

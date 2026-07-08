import POSEIDON
import os

print("POSEIDON installed successfully!")
print("Version:", getattr(POSEIDON, "__version__", "Unknown"))
print("POSEIDON_input_data:", os.environ.get("POSEIDON_input_data"))
print("PYSYN_CDBS:", os.environ.get("PYSYN_CDBS"))

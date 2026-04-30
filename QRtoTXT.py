import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from qrtotxt.__main__ import main  # noqa: E402

if __name__ == "__main__":
	main()

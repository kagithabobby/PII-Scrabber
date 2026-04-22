import os
import sys

sys.path.insert(0, os.getcwd())
# sys.path.insert(0, os.path.join(os.getcwd(), ".deps"))

import uvicorn


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)

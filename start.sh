# uvicorn main:app --host 0.0.0.0 --port 10000

#!/usr/bin/env bash

#!/usr/bin/env bash

pip install -r requirements.txt

python -m spacy download en_core_web_md || true

uvicorn main:app --host 0.0.0.0 --port 10000
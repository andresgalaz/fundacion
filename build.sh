#!/bin/bash
# cp app/archivo.py app/db.py app/globalUtil.py app/lambda_function.py app/libroRemu.py app/requirements.txt app/rut.py build/
# cd build

cd app
fecha=$(date +"%Y%m%d_%H%M%S")
zip ../fundacion_$fecha.zip cmp/*.py *.py --exclude __init__.py 

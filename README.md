# Menu Manager
## Dependencies
1. Tesseract for OCR parsing
2. PDFPlumber for general parsing

## Testing
*Do after your first git pull*

Within menuDatabase directory:
1. python3 -m venv .venv
2. source .venv/bin/activate
3. pip install -r requirements.txt

Now your virtual environment should have all the same libraries installed

## Ensuring VSCode regonizes Venv
For mac: (Cmd + Shift + P)
Or: (Ctrl + Shift + P)

Then pick "Python: Select Interpreter" and choose .venv

## Do every time 
1. source .venv/bin/activate

*Until we can figure out how to automate this, we have to manually activate the venv every time a terminal is opened*

## Installing new library into venv
1. Open/activate venv
2. pip install <new_dependency>
3. pip freeze > requirements.txt

This updates requirements.txt to include new dependency, so after you push this to git 

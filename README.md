# Setting up Venv
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

## Installing new library into venv
1. Open/activate venv
2. pip install <new_dependency>
3. pip freeze > requirements.txt

This updates requirements.txt to include new dependency, so after you push this to git 

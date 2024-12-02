# Menu Manager
## Dependencies
1. PDFPlumber for page to png image process
2. OpenAI API for parsing
3. ...

## How to use:
1. Clone the repo.
2. Within the root directory (menuDatabase), create and access .venv by:
>a. python3 -m venv .venv

>b. source .venv/bin/activate

>c. pip install -r requirements.txt

3. **Run Migrations**
>a. Open the first restuarant_menu directory (so manage.py is in path)

>b. python manage.py makemigrations

>c. python manage.py migrate

>d. If there's an error that means you edited either models.py or operations.py; don't touch those

4. Finally: python manage.py runserver
>This runs the app on the specified localhost to use for testing.


## Outputs from the frontend I need
**Upload.html:**
``` json
restaurant_data = {
  "name": <name>,
  "address": <address>, nullable
  "phone_number": <phone_number>, nullable
  "email": <email>, nullable
  "website": <website>, nullable
}
```
This is in addition to the Menu Name output already there; see ERD for the data types of each

**View.html:**
*once i get to it I'll be more specific*
- Only output will be filters; up to you guys what filters you want to be able to add
  
>- Try and limit the filters to only apply to data within: Restuarants table, Menus table, Menu_Versions table, **Menu_Processing Logs table**, and maybe Menu_Sections table

>- This page is only meant to be a general overview of the user's menus; should not display individual menu items

**Edit.html**
*once i get to it I'll be more specific*
- Output will always need to concist of the Menu_Id (which you will be passed in the view.html file, and since you can only get to edit.html file from view.html it'll be easy to pass the value) and the menu version_number
>- This is mostly for the intitial view; display everything abt this menu according to menu_id and version_number

- Then if they do any editing and hit save/confirm/whatever then you pass the **entire** new JSON object back to me.











# Old
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

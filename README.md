# Menu Manager
## Dependencies
*Listed on requirements.txt*

**Most Essential:**
1. PDFPlumber for page to png image process
2. OpenAI API for parsing

## How to use:
1. Clone the repo.
2. Within the root directory (menuDatabase), create and access .venv by:
>a. python3 -m venv .venv

>b. source .venv/bin/activate

>c. pip install -r requirements.txt

3. **Run Migrations**
>a. Open the first restuarant_menu directory (so manage.py is in path)

>b. Ensure any old migration files are deleted if its your first use.

>c. python manage.py makemigrations

>d. python manage.py migrate

>e. If there's an error that means you edited either models.py or operations.py; don't touch those

4. Finally: python manage.py runserver
>This runs the app on the specified localhost to use for testing.

## Considerations
1. API key and Django key's are not included in this repository so it will **not** run without you adding your own.

# Pinterest - Pinterest-style clone (Django)

## Setup
1. python -m venv venv
2. venv\Scripts\activate   (Windows)  OR  source venv/bin/activate (Mac/Linux)
3. pip install -r requirements.txt
4. python manage.py migrate
5. python manage.py seed_demo_pins    (optional: fills the site with demo pins/photos so it looks full)
6. python manage.py createsuperuser   (optional: create your own login)
7. python manage.py runserver
8. Open http://127.0.0.1:8000/

## Demo content
`seed_demo_pins` creates a demo user (demo / demo12345) plus ~18 pins across
6 boards (Home decor, Travel, Recipes, Fashion, Art, Fitness). If your machine
has internet access it downloads real, freely-licensed photos from Picsum;
otherwise it falls back to generated placeholder art automatically.

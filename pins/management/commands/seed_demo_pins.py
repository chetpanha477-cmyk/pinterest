import io
import random
import urllib.request

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw

from pins.models import Board, Pin

# (title, description, category / board name, base color, accent color)
# The board name matches a Pin category so seeded pins show up correctly
# when filtering by category on the home feed.
DEMO_PINS = [
    ("Cozy reading nook", "Soft blankets and warm lighting for lazy afternoons.", "Home decor", (232, 213, 196), (120, 90, 70)),
    ("Minimalist workspace", "Clean desk setup ideas for focused work.", "Home decor", (223, 227, 230), (70, 90, 110)),
    ("Boho living room", "Warm textures and plants for a relaxed vibe.", "Home decor", (214, 205, 178), (110, 120, 70)),
    ("Rustic kitchen shelf", "Open shelving styling with ceramics.", "Home decor", (225, 210, 190), (100, 70, 50)),
    ("Scandinavian bedroom", "Light wood and neutral linens for calm mornings.", "Home decor", (230, 226, 216), (150, 140, 120)),
    ("Small apartment layout", "Smart furniture ideas for tight spaces.", "Home decor", (218, 222, 210), (90, 100, 80)),

    ("Sunset over the mountains", "Golden hour views from a weekend hike.", "Travel", (247, 198, 141), (200, 90, 60)),
    ("City skyline at night", "Long exposure shots of downtown lights.", "Travel", (60, 70, 100), (230, 210, 150)),
    ("Desert road trip", "Wide open roads and red rock canyons.", "Travel", (230, 180, 140), (150, 70, 40)),
    ("Alpine lake reflection", "Still water and morning mist.", "Travel", (180, 210, 220), (40, 80, 100)),
    ("Tropical beach hut", "Overwater bungalows for a dream getaway.", "Travel", (170, 210, 210), (230, 200, 130)),
    ("Backpacking Europe", "A two-week rail itinerary for first timers.", "Travel", (200, 190, 175), (90, 70, 50)),

    ("Homemade pasta night", "Fresh pasta from scratch, step by step.", "Recipes", (240, 225, 200), (150, 60, 40)),
    ("Matcha latte art", "Simple recipe for a creamy matcha at home.", "Recipes", (200, 220, 180), (60, 110, 60)),
    ("Iced coffee setup", "Cold brew basics for summer mornings.", "Recipes", (210, 195, 175), (90, 60, 40)),
    ("Homemade sourdough", "Crusty loaf baked in a dutch oven.", "Recipes", (225, 200, 170), (120, 80, 40)),
    ("Weeknight stir fry", "A 20-minute dinner with pantry staples.", "Recipes", (215, 205, 160), (170, 90, 40)),
    ("Chocolate lava cake", "Rich dessert with a molten center.", "Recipes", (90, 60, 50), (200, 150, 110)),

    ("Street style autumn", "Layering ideas for cooler weather.", "Fashion", (200, 190, 210), (80, 60, 100)),
    ("Pastel nail art", "Simple designs to try at home.", "Fashion", (235, 215, 225), (150, 90, 120)),
    ("Capsule wardrobe", "Ten pieces that mix and match all season.", "Fashion", (210, 205, 195), (70, 65, 55)),
    ("Denim on denim", "Modern ways to wear a classic combo.", "Fashion", (150, 175, 200), (60, 90, 120)),

    ("Watercolor florals", "Soft brush technique for beginners.", "Art", (245, 220, 225), (170, 90, 120)),
    ("Line art portrait", "Single-line drawing inspiration.", "Art", (235, 235, 230), (40, 40, 40)),
    ("Abstract acrylic pour", "Colorful fluid art for your wall.", "Art", (200, 170, 210), (230, 120, 90)),
    ("Sketchbook study", "Daily doodles to build the habit.", "Art", (220, 218, 205), (60, 60, 60)),

    ("Morning yoga flow", "A gentle 10-minute stretch routine.", "Fitness", (210, 230, 225), (50, 120, 100)),
    ("Home gym setup", "Small space equipment that works hard.", "Fitness", (200, 200, 210), (60, 60, 90)),
    ("30-minute HIIT", "No-equipment cardio for busy days.", "Fitness", (230, 200, 190), (200, 80, 60)),

    ("Everyday glow makeup", "A five-minute natural makeup routine.", "Beauty", (240, 210, 210), (190, 100, 110)),
    ("Skincare shelf edit", "Layering order for morning and night.", "Beauty", (225, 220, 210), (150, 130, 100)),
    ("Soft curls tutorial", "Heat-free curls that last overnight.", "Beauty", (215, 190, 170), (110, 70, 50)),

    ("Macrame wall hanging", "Beginner-friendly knots and patterns.", "DIY & Crafts", (225, 215, 195), (110, 90, 60)),
    ("Upcycled glass jars", "Turn kitchen jars into home decor.", "DIY & Crafts", (200, 215, 210), (70, 100, 90)),
    ("Hand-poured candles", "Soy wax candles with dried flowers.", "DIY & Crafts", (235, 220, 200), (180, 140, 90)),

    ("Golden hour portraits", "Natural light tips for outdoor shoots.", "Photography", (230, 190, 140), (150, 90, 50)),
    ("Moody film photography", "Grainy tones inspired by 35mm film.", "Photography", (70, 65, 70), (150, 140, 130)),
    ("Product photography setup", "A simple lightbox for clean shots.", "Photography", (225, 225, 225), (90, 90, 90)),

    ("Balcony garden", "Small space plant arrangement ideas.", "Gardening", (205, 220, 190), (60, 100, 60)),
    ("Raised vegetable beds", "Layout tips for a productive backyard plot.", "Gardening", (150, 170, 120), (90, 60, 40)),
    ("Indoor plant corner", "Low-light houseplants that thrive indoors.", "Gardening", (180, 200, 170), (60, 90, 60)),

    ("Minimal desk setup", "Cable management for a clean workspace.", "Technology", (210, 215, 220), (60, 70, 90)),
    ("Smart home starter kit", "The basics for automating your first room.", "Technology", (200, 205, 215), (50, 60, 100)),
    ("Mechanical keyboard build", "Choosing switches and keycaps.", "Technology", (60, 60, 65), (200, 60, 60)),

    ("Rustic barn wedding", "String lights and wildflower centerpieces.", "Wedding", (235, 220, 200), (150, 110, 80)),
    ("Minimalist wedding invites", "Clean typography for modern couples.", "Wedding", (240, 235, 225), (100, 95, 85)),
    ("Garden ceremony arch", "Floral arch ideas for an outdoor 'I do'.", "Wedding", (220, 225, 200), (150, 170, 100)),

    ("Golden retriever puppy", "Everything about their first year.", "Animals", (220, 180, 120), (150, 100, 50)),
    ("Tabby cat naps", "The coziest napping spots for cats.", "Animals", (200, 190, 175), (110, 90, 70)),
    ("Backyard bird feeders", "Attracting songbirds year-round.", "Animals", (190, 205, 180), (90, 110, 70)),

    ("Monday motivation quote", "A short reminder to start the week right.", "Quotes", (235, 230, 220), (60, 60, 60)),
    ("Minimalist typography quote", "Clean type treatment on a plain background.", "Quotes", (245, 245, 240), (30, 30, 30)),

    ("Modern logo trends", "Simple geometric marks for 2026 brands.", "Design", (220, 220, 225), (60, 60, 90)),
    ("UI color palettes", "Accessible palettes for clean interfaces.", "Design", (210, 220, 225), (50, 90, 110)),
]

HEIGHTS = [340, 420, 500, 380, 460, 320, 440, 400]


def make_placeholder_image(base_color, accent_color, height, seed):
    rng = random.Random(seed)
    width = 400
    img = Image.new("RGB", (width, height), base_color)
    draw = ImageDraw.Draw(img)

    for i in range(height):
        t = i / height
        r = int(base_color[0] * (1 - t) + accent_color[0] * 0.35 * t + base_color[0] * 0.65 * t)
        g = int(base_color[1] * (1 - t) + accent_color[1] * 0.35 * t + base_color[1] * 0.65 * t)
        b = int(base_color[2] * (1 - t) + accent_color[2] * 0.35 * t + base_color[2] * 0.65 * t)
        draw.line([(0, i), (width, i)], fill=(r, g, b))

    shape_count = rng.randint(2, 4)
    for _ in range(shape_count):
        r = rng.randint(40, 120)
        cx = rng.randint(0, width)
        cy = rng.randint(0, height)
        alpha_color = tuple(min(255, c + rng.randint(-20, 20)) for c in accent_color)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=alpha_color)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def fetch_real_photo(seed, width, height):
    """Try to download a real, freely-licensed placeholder photo from Picsum
    (picsum.photos - Unsplash-sourced, free for any use, no attribution required).
    Returns image bytes, or None if the machine has no internet access."""
    url = f"https://picsum.photos/seed/{seed}/{width}/{height}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            return resp.read()
    except Exception:
        return None


class Command(BaseCommand):
    help = "Seeds the database with demo pins and boards (generated placeholder images, no copyrighted content) so the home feed looks full."

    def add_arguments(self, parser):
        parser.add_argument("--username", default="demo", help="Username to own the demo pins (default: demo)")
        parser.add_argument("--password", default="demo12345", help="Password for the demo user if newly created")

    def handle(self, *args, **options):
        username = options["username"]
        password = options["password"]

        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created demo user '{username}' / password '{password}'"))
        else:
            self.stdout.write(f"Using existing user '{username}'")

        board_cache = {}

        created_count = 0
        for i, (title, desc, board_name, base_color, accent_color) in enumerate(DEMO_PINS):
            if Pin.objects.filter(title=title, owner=user).exists():
                continue

            if board_name not in board_cache:
                board, _ = Board.objects.get_or_create(name=board_name, owner=user)
                board_cache[board_name] = board
            board = board_cache[board_name]

            height = HEIGHTS[i % len(HEIGHTS)]
            image_bytes = fetch_real_photo(seed=title.replace(" ", "-").lower(), width=400, height=height)
            source = "photo"
            if image_bytes is None:
                image_bytes = make_placeholder_image(base_color, accent_color, height, seed=i)
                source = "generated art"

            pin = Pin(title=title, description=desc, owner=user, board=board, category=board_name)
            pin.image.save(f"demo_{i+1}.jpg", ContentFile(image_bytes), save=True)
            created_count += 1
            if created_count == 1:
                self.stdout.write(f"(using {source} for demo images...)")

        self.stdout.write(self.style.SUCCESS(f"Done. Created {created_count} new demo pins across {len(board_cache)} boards."))

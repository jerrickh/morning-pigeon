import os
import time
from datetime import datetime, timedelta
import requests

# --- CONFIGURATION ---
LAT = 40.6892   # Clinton Hill, Brooklyn
LON = -73.9647
TIMEZONE = "America/New_York"

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "YOUR_ELEVENLABS_API_KEY")
VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb")
OUTPUT_FILE = "today-weather.mp3"


def pick_daily(options: list[str], day_offset: int = 0) -> str:
    """Deterministically rotates through a list of phrases based on the day of the year."""
    day_of_year = datetime.now().timetuple().tm_yday + day_offset
    return options[day_of_year % len(options)]


def get_last_nights_moon() -> str:
    """Calculates yesterday's lunar phase and rotates Glaswegian-tinged phrasing daily."""
    yesterday = datetime.now() - timedelta(days=1)
    known_new_moon = datetime(2000, 1, 6, 18, 14)
    lunar_cycle = 29.53058867
    days_since = (yesterday - known_new_moon).total_seconds() / 86400.0
    phase = (days_since % lunar_cycle) / lunar_cycle

    if phase < 0.03 or phase > 0.97:
        return pick_daily([
            "Last night the sky was dark and cozy under a brand-new moon.",
            "While you weans slept last night, a dark new moon tucked quietly into the stars.",
            "Last night was a dark new-moon night, with the stars shining extra bright over the rooftops.",
        ])
    elif phase < 0.22:
        return pick_daily([
            "Last night we slept under a thin wee silver crescent moon.",
            "A slender crescent moon hung like a silver fingernail over the brownstones last night.",
            "Last night we slept beneath a quiet, curving crescent moon.",
        ])
    elif phase < 0.28:
        return pick_daily([
            "Last night we slept under a bright half moon glowing over the neighborhood.",
            "A crisp half moon shone down on the block while you wee ones slept last night.",
            "Last night we slept beneath a steady half moon high in the dark sky.",
        ])
    elif phase < 0.47:
        return pick_daily([
            "Last night we slept under a bright, glowing waxing moon high in the sky.",
            "A big, bright waxing moon watched over the block while we slept last night.",
            "Last night we slept beneath a growing moon shining silver over the trees.",
        ])
    elif phase < 0.53:
        return pick_daily([
            "Last night we slept under a big, round full moon shining down on the neighborhood.",
            "A huge, luminous full moon lit up the whole sky while we slept last night.",
            "Last night we slept beneath a bonnie, bright full moon.",
        ])
    elif phase < 0.72:
        return pick_daily([
            "Last night we slept under a bright waning moon slowly growing slimmer.",
            "A soft, glowing waning moon drifted across the night sky while we slept.",
            "Last night we slept beneath a bright moon that is slowly growing thinner each night.",
        ])
    elif phase < 0.78:
        return pick_daily([
            "Last night we slept under a quiet half moon in the late-night sky.",
            "A calm half moon watched over the quiet streets while we slept last night.",
            "Last night we slept beneath a silvery half moon.",
        ])
    else:
        return pick_daily([
            "Last night we slept under a delicate wee crescent moon before sunrise.",
            "A thin, sleepy crescent moon curved low in the sky before dawn today.",
            "Last night we slept beneath a quiet old crescent moon.",
        ])


def get_celestial_or_nature_note(weather_code: int, wind_speed: float, temp_morning: float, today: datetime) -> str:
    """Checks celestial dates first, then rotates seasonal nature observations with Glaswegian warmth."""
    m, d = today.month, today.day

    if (m, d) in [(3, 20), (3, 21)]:
        return "Today is the Spring Equinox, when daytime and nighttime are the exact same length."
    if (m, d) in [(6, 20), (6, 21)]:
        return "Today is the Summer Solstice—the sun's splittin' the trees on the longest, sunniest day of the whole year."
    if (m, d) in [(9, 22), (9, 23)]:
        return "Today is the Autumn Equinox, when day and night share the sky equally."
    if (m, d) in [(12, 21), (12, 22)]:
        return "Today is the Winter Solstice, the shortest day of the year, when the light begins its slow return."

    # Heavy rain
    if weather_code in [63, 65, 81, 82]:
        return pick_daily([
            "Aye, the rain is God's way o' cleanin' the coos—and it brings the earthworms wiggling right up onto the damp sidewalks.",
            "Listen for blue jays calling loudly from the wet oak branches while puddles gather along the curb.",
        ], day_offset=1)

    # Light drizzle / smirr
    if weather_code in [51, 53, 55, 61, 80]:
        return pick_daily([
            "Watch the damp sidewalks closely today for wee earthworms wiggling up into the cool air.",
            "On dreich, misty days like today, dark tree bark turns almost black and moss on the stoops wakes up bright green.",
        ], day_offset=1)

    # Blowin' a hoolie (windy)
    if wind_speed >= 15:
        if m in [10, 11]:
            return pick_daily([
                "Watch how the gusts send golden ginkgo leaves spinning like little fans across the street.",
                "Listen to the wind rattling the dry oak leaves still clinging stubbornly to the high branches.",
                "Neighborhood squirrels are braving the breeze today to tuck their last acorns under the tree roots.",
            ], day_offset=2)
        return pick_daily([
            "Listen to the wind rushing through the high branches, where my pigeon pals and the sparrows are tucking out of the breeze.",
            "Watch how the wind sends dry leaves dancing down the block ahead of Little Red.",
        ], day_offset=2)

    # Pure Baltic / deep cold
    if temp_morning < 36:
        return pick_daily([
            "Down beneath the fallen leaves and soil today, wee beetles, ladybugs, and garden spiders are tucked deep underground sleeping through the cold.",
            "Look closely at shaded grass or car roofs this morning to see tiny crystals of white frost sparkling.",
            "The neighborhood birds fluff their feathers up round and puffy on Baltic mornings like this to trap warm air.",
        ], day_offset=3)

    # Autumn migration / crisp weather (October - November)
    if m in [10, 11]:
        return pick_daily([
            "Keep your ears open along the trees today for noisy flocks of glossy black grackles gathering for their autumn journey south.",
            "Look up into the sky—you might spot a long V of migrating Canada geese honking as they fly south.",
            "Listen to the dry oak and sycamore leaves crunching underfoot around the yard and playground today.",
            "Watch the neighborhood squirrels with their bushy tails—they are burying acorns everywhere before the ground freezes.",
        ], day_offset=4)

    # Default sunny/mild pool
    return pick_daily([
        "Look up into the trees on your way today—the neighborhood chickadees and mourning doves are busy flitting between the branches.",
        "Keep an eye on sunny brick walls and stoops today, where neighborhood cats love to curl up in warm patches of light.",
        "Listen closely above the street sounds for wee sparrows chirping together in the hedges.",
    ], day_offset=5)


def build_morning_script() -> str:
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}&longitude={LON}"
        f"&hourly=temperature_2m,apparent_temperature,precipitation_probability,weather_code,wind_speed_10m,cloud_cover"
        f"&temperature_unit=fahrenheit&wind_speed_unit=mph"
        f"&timezone={TIMEZONE}&past_days=1&forecast_days=1"
    )

    resp = None
    for attempt in range(3):
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            break
        except requests.exceptions.RequestException:
            if attempt == 2:
                raise
            print(f"Weather API slow (attempt {attempt + 1}/3), retrying in 5 seconds...")
            time.sleep(5)

    hourly = resp.json()["hourly"]

    # With past_days=1: index 8 = yesterday 8 AM, index 32 = today 8 AM, index 39 = today 3 PM
    feels_yest_am = hourly["apparent_temperature"][8]
    cloud_yest_am = hourly["cloud_cover"][8]

    temp_am = hourly["temperature_2m"][32]
    feels_am = hourly["apparent_temperature"][32]
    wind_am = hourly["wind_speed_10m"][32]
    cloud_am = hourly["cloud_cover"][32]
    code_am = hourly["weather_code"][32]

    temp_pm = hourly["temperature_2m"][39]
    rain_prob_max = max(hourly["precipitation_probability"][32:41])

    # 1. Sky & precipitation description with Glaswegian weather words
    was_cloudy_yest = cloud_yest_am >= 65
    is_heavy_rain = code_am in [63, 65, 81, 82]
    is_light_rain = code_am in [51, 53, 55, 61, 80]
    is_wet = is_heavy_rain or is_light_rain or rain_prob_max >= 45

    if is_heavy_rain:
        sky_desc = pick_daily([
            "where it is properly chucking it doon from the sky",
            "with rain stoatin' right off the pavement",
        ])
    elif is_light_rain:
        sky_desc = pick_daily([
            "with a fine, misty smirr hanging in the air",
            "on a right dreich, drizzly morning",
        ])
    elif code_am in [71, 73, 75, 77, 85, 86]:
        sky_desc = "with wee snow flurries swirling in the air"
    elif cloud_am >= 75:
        sky_desc = pick_daily([
            "on a bit of a dreich, gray morning",
            "beneath a cozy blanket of gray clouds",
            "under a high ceiling of autumn clouds",
        ])
    elif cloud_am >= 35:
        sky_desc = pick_daily([
            "under partly sunny skies—nae bad the day!",
            "with patches of blue sky peeking through the clouds",
            "under a mix of morning sun and drifting clouds",
        ])
    else:
        if temp_am >= 85 or temp_pm >= 85:
            sky_desc = "where the sun's splittin' the trees—aye, it's official taps aff weather!"
        elif temp_am >= 62:
            sky_desc = pick_daily([
                "and aye, it's a proper stunner out there today!",
                "under wide-open, sunny skies—nae bad the day at all!",
            ])
        elif was_cloudy_yest:
            sky_desc = "under bright, clear sunshine after yesterday's dreich clouds"
        else:
            sky_desc = pick_daily([
                "under wide-open, sunny skies—nae bad the day!",
                "under another bright, crystal-clear sky",
                "with golden morning sunshine pouring down the avenue",
            ])

    # 2. Always-on yesterday comparison
    feels_diff = feels_am - feels_yest_am
    if feels_diff <= -7:
        delta_note = ", and it feels a whole lot colder than yesterday"
    elif feels_diff <= -3:
        delta_note = ", and it feels a wee bit cooler than yesterday"
    elif feels_diff >= 7:
        delta_note = ", and it feels noticeably warmer than yesterday"
    elif feels_diff >= 3:
        delta_note = ", and it feels a wee bit warmer than yesterday"
    else:
        delta_note = ", feeling right around the same as yesterday"

    # 3. Temperature feel + wind + clothing rules
    is_very_cold = feels_am < 34
    is_windy = wind_am >= 15

    play_spaces = pick_daily([
        "playing in the side yard, the backyard, or at the playground",
        "outdoor play in the side yard, the backyard, or the playground",
        "running around the side yard, the backyard, or the playground today",
    ], day_offset=2)

    if is_very_cold:
        feel_phrase = "pure Baltic air—a bitter, snell chill" if is_windy else "pure Baltic, frosty air"
        gear_line = (
            f"Bundle up in your warm wool layers, heavy winter coat, hat, and gloves "
            f"so you aren't chitterin' while {play_spaces}."
        )
    elif feels_am < 48:
        feel_phrase = "a right nippy wind oot there" if is_windy else "a crisp, nippy chill"
        gear_line = (
            f"Wear warm layers, a cozy sweater, and a jacket with your hat and gloves for {play_spaces}."
        )
    elif feels_am < 62:
        feel_phrase = "a blustery breeze blowin' a hoolie" if is_windy else "a cool, fresh breeze"
        gear_line = (
            f"Wear comfortable layers and a sweater or light jacket for {play_spaces}."
        )
    elif feels_am >= 85:
        feel_phrase = "blazing warm summer heat"
        gear_line = (
            f"Light, breathable clothes and plenty of water are the order of the day for {play_spaces}."
        )
    else:
        feel_phrase = "mild, bonnie air"
        gear_line = (
            f"Light layers are plenty today for {play_spaces}."
        )

    if is_windy and not is_very_cold and feels_am >= 48:
        gear_line += " Keep your hood or hat handy too, because it's blowin' a hoolie down the avenue."

    if is_wet:
        gear_line += (
            " Wet weather is in the mix today, so pull on your raincoat and boots, "
            "and gie your bag your rain pants so you don't end up pure drookit!"
        )

    if is_wet or is_very_cold:
        gear_line += " Remember—there's no such thing as bad weather, just the wrong clothes!"

    # 4. Pickup transition on Little Red
    temp_swing = temp_pm - temp_am
    if temp_swing >= 11 and not is_very_cold:
        pickup_line = pick_daily([
            "By pickup time, the afternoon sun will warm things right up, so don't forget to tuck your extra layers into the bag for the ride home on Little Red.",
            "Things will warm up nicely by pickup, so expect to pack your extra layers away for the afternoon ride on Little Red.",
        ])
    elif is_wet:
        pickup_line = "The damp weather will linger through pickup time, so keep your raincoat handy for the ride home on Little Red."
    else:
        pickup_line = pick_daily([
            "Temperatures will stay pretty steady through pickup time, so keep your layers handy for the ride home on Little Red.",
            "The air will feel much the same at pickup, so you'll want those same layers for the ride back on Little Red.",
        ])

    # 5. Glaswegian opening greeting & warm sign-off rotation
    greeting = pick_daily([
        "Good morning, weans! It's Mr. Weatherpigeons tapping on your windowpane.",
        "Rise and shine, wee ones! Mr. Weatherpigeons here, reporting from the windowsill.",
        "Good morning, everyone! Aye, it's your pal Mr. Weatherpigeons checking in from the ledge.",
    ])

    signoff = pick_daily([
        "Have a grand ride on Little Red, and Mr. Weatherpigeons will check the sky again tomorrow. Cheerio!",
        "Enjoy your wee adventures outside today, and have a brilliant ride to school! Cheerio!",
        "Have a lovely day playing outside—Mr. Weatherpigeons will see you tomorrow morning!",
    ], day_offset=3)

    moon_line = get_last_nights_moon()
    nature_line = get_celestial_or_nature_note(code_am, wind_am, feels_am, datetime.now())

    return (
        f"{greeting} {moon_line} "
        f"Riding to school on Little Red this morning, you'll find {feel_phrase} {sky_desc}{delta_note}. "
        f"{gear_line} "
        f"{pickup_line} "
        f"{nature_line} "
        f"{signoff}"
    )


def generate_audio(text: str) -> None:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}?output_format=mp3_44100_128"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.72,
            "similarity_boost": 0.75,
        },
    }

    response = requests.post(url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()

    with open(OUTPUT_FILE, "wb") as f:
        f.write(response.content)
    print(f"Saved {OUTPUT_FILE} ({len(text)} characters).")


if __name__ == "__main__":
    spoken_script = build_morning_script()
    print("--- GENERATED SCRIPT ---")
    print(spoken_script)
    print("------------------------")
    generate_audio(spoken_script)

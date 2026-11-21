"""Site config. Add a topic here and it shows up everywhere (feed, nav, dashboards)."""

TOPICS = {
    "python": {
        "short": "Python",          # compact label for nav chips
        "color": "#3ef0ff",       # accent used for this topic across the site
        "label": "Python",
        "icon": "🐍",
        "blurb": "Libraries, learning repos and data-analysis tooling.",
        "github_queries": [
            "language:python created:>{since} stars:>30",
            "topic:data-analysis pushed:>{since} stars:>300",
        ],
        "hn_query": "python",
        "news_feeds": [("Planet Python", "https://planetpython.org/rss20.xml"), ("Real Python", "https://realpython.com/atom.xml")],
    },
    "3d-printing": {
        "short": "3D Print",          # compact label for nav chips
        "color": "#ff8a3d",       # accent used for this topic across the site
        "label": "3D Printing",
        "icon": "🧊",
        "blurb": "Slicers, firmware, models and printer tinkering.",
        "github_queries": [
            "topic:3d-printing pushed:>{since} stars:>100",
            "topic:klipper pushed:>{since} stars:>50",
        ],
        "hn_query": "3d printing",
        "news_feeds": [("Prusa Blog", "https://blog.prusa3d.com/feed/")],
    },
    "woodworking": {
        "short": "Wood",          # compact label for nav chips
        "color": "#e0b36a",       # accent used for this topic across the site
        "label": "Woodworking",
        "icon": "🪵",
        "blurb": "CAD/CAM, CNC, joinery tools and shop projects.",
        "github_queries": [
            "topic:woodworking pushed:>{since} stars:>10",
            "topic:cnc pushed:>{since} stars:>100",
        ],
        "hn_query": "woodworking",
        "news_feeds": [("Lost Art Press", "https://blog.lostartpress.com/feed/"), ("Wood and Shop", "https://woodandshop.com/feed/")],
    },
    "robotics": {
        "short": "Robotics",          # compact label for nav chips
        "color": "#7cff9b",       # accent used for this topic across the site
        "label": "Arduino · ESP32 · Robotics",
        "icon": "🤖",
        "blurb": "Microcontrollers, sensors, motors and hobby robots.",
        "github_queries": [
            "topic:esp32 created:>{since} stars:>100",
            "topic:arduino pushed:>{since} stars:>500",
            "topic:robotics created:>{since} stars:>200",
        ],
        "hn_query": "esp32",
        "news_feeds": [("Hackaday", "https://hackaday.com/feed/"), ("Arduino Blog", "https://blog.arduino.cc/feed/")],
    },
    "data": {
        "short": "Data",          # compact label for nav chips
        "color": "#a78bfa",       # accent used for this topic across the site
        "label": "Data Analytics",
        "icon": "📈",
        "blurb": "pandas, SQL, visualization and the analytics toolchain.",
        "github_queries": [
            "topic:duckdb pushed:>{since} stars:>1000",
            "topic:data-visualization pushed:>{since} stars:>1000",
            "topic:pandas pushed:>{since} stars:>1000",
        ],
        "hn_query": "data analysis",
        "news_feeds": [("KDnuggets", "https://www.kdnuggets.com/feed")],
    },
    "board-games": {
        "short": "Games",          # compact label for nav chips
        "color": "#ff5fd2",       # accent used for this topic across the site
        "label": "Board Games",
        "icon": "🎲",
        "blurb": "New releases, reviews and tools for the table.",
        "github_queries": [
            "topic:board-game pushed:>{since} stars:>20",
            "topic:boardgame pushed:>{since} stars:>20",
        ],
        "hn_query": "board game",
        "news_feeds": [("Board Game Quest", "https://boardgamequest.com/feed/")],
    },
}

LOOKBACK_DAYS = 30       # "recent" window for GitHub searches
ITEMS_PER_TOPIC = 8
SITE_TITLE = "Maker Hub"
SITE_TAGLINE = "My hub for Python, 3D printing, woodworking, robotics, data and board games — news, cheat sheets and resources."

# Pin board: anything you pin becomes a GitHub issue with this label (close it to unpin).
GITHUB_REPO = "Ovalt1nejenk1ns/maker-hub"
PIN_LABEL = "pin"

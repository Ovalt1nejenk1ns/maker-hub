"""Site config. Add a topic here and it shows up everywhere (feed, nav, dashboards)."""

TOPICS = {
    "python": {
        "label": "Python",
        "icon": "🐍",
        "blurb": "Libraries, learning repos and data-analysis tooling.",
        "github_queries": [
            "language:python created:>{since} stars:>30",
            "topic:data-analysis pushed:>{since} stars:>300",
        ],
        "hn_query": "python",
    },
    "3d-printing": {
        "label": "3D Printing",
        "icon": "🧊",
        "blurb": "Slicers, firmware, models and printer tinkering.",
        "github_queries": [
            "topic:3d-printing pushed:>{since} stars:>100",
            "topic:klipper pushed:>{since} stars:>50",
        ],
        "hn_query": "3d printing",
    },
    "woodworking": {
        "label": "Woodworking",
        "icon": "🪵",
        "blurb": "CAD/CAM, CNC, joinery tools and shop projects.",
        "github_queries": [
            "topic:woodworking pushed:>{since} stars:>10",
            "topic:cnc pushed:>{since} stars:>100",
        ],
        "hn_query": "woodworking",
    },
}

LOOKBACK_DAYS = 30       # "recent" window for GitHub searches
ITEMS_PER_TOPIC = 8
SITE_TITLE = "Maker Hub"
SITE_TAGLINE = "Python · 3D printing · woodworking — what's rising, refreshed weekly."

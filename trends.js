// Trends tab content for maker-hub. Rendered by trends-render.js.
// This is the ONLY file the scheduled refresh task rewrites.
// Keep it valid JS: window.TRENDS = { ... };  (JSON-style object, double quotes)
window.TRENDS = {
  "updated": "2026-10-15",
  "updatedLabel": "October 15, 2026",

  "tiles": [
    { "icon": "🐍", "label": "awesome-python",    "text": "327k stars — definitive \"which tool\" reference", "color": "cyan" },
    { "icon": "🤗", "label": "Transformers",      "text": "167k stars — state-of-the-art ML models",          "color": "purple" },
    { "icon": "🦆", "label": "DuckDB",            "text": "OLAP SQL engine — local analytics standard",       "color": "green" },
    { "icon": "🚀", "label": "LLMs from Scratch", "text": "Build ChatGPT-like LLMs step-by-step",             "color": "amber" }
  ],

  "sections": [
    {
      "title": "🔥 GitHub Trending — October 15, 2026",
      "color": "green",
      "tag": "hot repos python & ml",
      "type": "cards",
      "items": [
        { "kind": "github", "icon": "🐍", "title": "vinta/awesome-python", "sub": "Python · Reference",
          "desc": "The definitive list that answers \"I want to do X in Python, which tool should I use?\" 327k stars and growing. The canonical reference for every Python use case from web to data to ML.",
          "stats": [{ "text": "⭐ 327k+" }, { "text": "Essential", "hot": true }],
          "links": [{ "text": "View →", "url": "https://github.com/vinta/awesome-python" }] },
        { "kind": "github", "icon": "📚", "title": "practical-tutorials/project-based-learning", "sub": "Multi-language · Learning",
          "desc": "Curated list of project-based tutorials across all languages. 286k stars. The best way to learn by building real things. Organized by language and difficulty.",
          "stats": [{ "text": "⭐ 286k+" }],
          "links": [{ "text": "View →", "url": "https://github.com/practical-tutorials/project-based-learning" }] },
        { "kind": "github", "icon": "🧮", "title": "TheAlgorithms/Python", "sub": "Python · Algorithms",
          "desc": "All algorithms implemented in Python — sorting, searching, dynamic programming, graph algorithms, and more. 225k stars. Reference or study guide for interview prep and algorithm mastery.",
          "stats": [{ "text": "⭐ 225k+" }],
          "links": [{ "text": "View →", "url": "https://github.com/TheAlgorithms/Python" }] },
        { "kind": "github", "icon": "🤖", "title": "tensorflow/tensorflow", "sub": "C++ / Python · ML Framework",
          "desc": "An Open Source Machine Learning Framework for Everyone. 200k+ stars. TensorFlow remains one of the industry standards for building and deploying ML models at scale.",
          "stats": [{ "text": "⭐ 200k+" }, { "text": "Industry Standard", "hot": true }],
          "links": [{ "text": "View →", "url": "https://github.com/tensorflow/tensorflow" }] },
        { "kind": "github", "icon": "🎥", "title": "yt-dlp/yt-dlp", "sub": "Python · Utilities",
          "desc": "A feature-rich command-line audio/video downloader. 198k stars. The most capable open-source video downloader — supports 1000+ sites, formats, and post-processing options.",
          "stats": [{ "text": "⭐ 198k+" }],
          "links": [{ "text": "View →", "url": "https://github.com/yt-dlp/yt-dlp" }] },
        { "kind": "github", "icon": "💬", "title": "f/prompts.chat", "sub": "Prompts · AI / ChatGPT",
          "desc": "Share, discover, and collect prompts from the community. Free and open source — self-host for your organization. 173k stars. The go-to resource for effective ChatGPT / LLM prompting.",
          "stats": [{ "text": "⭐ 173k+" }],
          "links": [{ "text": "View →", "url": "https://github.com/f/prompts.chat" }] },
        { "kind": "github", "icon": "🤗", "title": "huggingface/transformers", "sub": "Python · LLM / ML Models",
          "desc": "Transformers: state-of-the-art model-definition framework for NLP, vision, audio, and multimodal. 167k+ stars. The standard library for working with pre-trained models and fine-tuning.",
          "stats": [{ "text": "⭐ 167k+" }, { "text": "🔥 Most Active", "hot": true }],
          "links": [{ "text": "View →", "url": "https://github.com/huggingface/transformers" }] },
        { "kind": "github", "icon": "🧠", "title": "rasbt/LLMs-from-scratch", "sub": "Python · LLM Education",
          "desc": "Implement a ChatGPT-like LLM in PyTorch from scratch, step by step. 106k stars. The definitive hands-on course for understanding how modern LLMs actually work under the hood.",
          "stats": [{ "text": "⭐ 106k+" }, { "text": "Rising Fast", "hot": true }],
          "links": [{ "text": "View →", "url": "https://github.com/rasbt/LLMs-from-scratch" }] },
        { "kind": "github", "icon": "🔥", "title": "pytorch/pytorch", "sub": "C++ / Python · ML Framework",
          "desc": "Tensors and Dynamic neural networks in Python with strong GPU acceleration. 104k+ stars. PyTorch has become the dominant research and production ML framework — especially for LLMs and deep learning.",
          "stats": [{ "text": "⭐ 104k+" }, { "text": "Industry Standard", "hot": true }],
          "links": [{ "text": "View →", "url": "https://github.com/pytorch/pytorch" }] },
        { "kind": "github", "icon": "📡", "title": "ruvnet/RuView", "sub": "Python / C · WiFi Sensing",
          "desc": "Turns commodity WiFi signals into real-time spatial intelligence, vital sign monitoring, and presence detection — all without video. 98k stars. Cutting-edge IoT/sensor innovation.",
          "stats": [{ "text": "⭐ 98k+" }],
          "links": [{ "text": "View →", "url": "https://github.com/ruvnet/RuView" }] },
        { "kind": "github", "icon": "🏠", "title": "home-assistant/core", "sub": "Python · Home Automation",
          "desc": "Open source home automation that puts local control and privacy first. 91k+ stars. The dominant home automation platform — integrates ESP32, Raspberry Pi, and 1000+ smart devices.",
          "stats": [{ "text": "⭐ 91k+" }, { "text": "Essential", "hot": true }],
          "links": [{ "text": "View →", "url": "https://github.com/home-assistant/core" }] },
        { "kind": "github", "icon": "🎓", "title": "Developer-Y/cs-video-courses", "sub": "Learning · Computer Science",
          "desc": "Comprehensive list of Computer Science courses with video lectures. 83k+ stars. Covers algorithms, data structures, systems, AI, robotics, and more — all with free YouTube links.",
          "stats": [{ "text": "⭐ 83k+" }],
          "links": [{ "text": "View →", "url": "https://github.com/Developer-Y/cs-video-courses" }] }
      ]
    },
    {
      "title": "🛠️ Tools Making Waves in 2026",
      "color": "amber",
      "type": "cards",
      "items": [
        { "kind": "tool", "icon": "🌊", "title": "Marimo", "sub": "Reactive Python Notebooks",
          "desc": "Reactive notebooks where cells re-run automatically. No more stale outputs. Deployable as web apps, shareable as .py scripts. Serious competition for Jupyter.",
          "stats": [{ "text": "2024" }, { "text": "Rising", "hot": true }],
          "links": [{ "text": "Try →", "url": "https://marimo.io/" }] },
        { "kind": "tool", "icon": "🏃", "title": "micro-ROS", "sub": "ROS 2 on Microcontrollers",
          "desc": "Run ROS 2 nodes directly on ESP32 and Arduino. Bridges the gap between your maker hardware and ROS 2 robotics stack. Huge for serious robot projects.",
          "stats": [{ "text": "ESP32 + ROS 2" }],
          "links": [{ "text": "micro.ros.org →", "url": "https://micro.ros.org/" }] },
        { "kind": "tool", "icon": "👁️", "title": "OpenMV", "sub": "Machine Vision on Microcontrollers",
          "desc": "MicroPython-based computer vision on tiny boards. Face detection, object tracking, color recognition — no Raspberry Pi needed. OpenMV Cam H7 is the flagship board.",
          "stats": [{ "text": "MicroPython" }, { "text": "Vision" }],
          "links": [{ "text": "openmv.io →", "url": "https://openmv.io/" }] },
        { "kind": "tool", "icon": "📐", "title": "Evidence", "sub": "BI as Code",
          "desc": "SQL + Markdown → beautiful data reports deployed as static sites. Version-controlled analytics that lives in git. Great alternative to Power BI for personal portfolio work.",
          "stats": [{ "text": "New" }],
          "links": [{ "text": "evidence.dev →", "url": "https://evidence.dev/" }] }
      ]
    },
    {
      "title": "💬 Community Buzz — What's Being Discussed",
      "color": "purple",
      "type": "cards",
      "items": [
        { "kind": "data", "icon": "🧵", "title": "r/arduino — Hot This Week", "sub": "Embedded & Maker Projects",
          "desc": "Top discussion: \"Why buy a smartwatch when you can hold a 3D-rendering, game-playing RGB square in your hand?\" ESP32 CAM video playback, Teensy 4.1 hand exoskeleton builds, Arduino Nanos shipping. DIY wearables and custom hardware dominating.",
          "stats": [],
          "links": [
            { "text": "RGB Square Post →", "url": "https://www.reddit.com/r/arduino/comments/1x1gc6v/why_buy_a_smartwatch_when_you_can_hold_a/" },
            { "text": "Top This Week →", "url": "https://www.reddit.com/r/arduino/top/?t=week" }
          ] },
        { "kind": "data", "icon": "🔍", "title": "Hacker News — Security & AI", "sub": "Tech Trends & Discussion",
          "desc": "Top story (933 points): \"Containment and monitoring failures are to blame for AI hacking reports — experts.\" Also trending: \"Has AI tells\" (132 pts), \"$15M Simons Foundation effort to help mathematicians navigate AI era\" (152 pts), \"Market selloff tests AI data centre deal boom.\"",
          "stats": [],
          "links": [
            { "text": "HN Front Page →", "url": "https://news.ycombinator.com/front" },
            { "text": "Show HN →", "url": "https://news.ycombinator.com/show" }
          ] },
        { "kind": "data", "icon": "💻", "title": "HN Maker Trends", "sub": "Development & Tools",
          "desc": "HN Show HN highlights: \"Proa — Rust web framework with fast SSR\" (21 pts), \"Game of Life but Multiplayer, Hypermedia and Python\" (7 pts), \"BlastLoop — structure-first coding for AI agents\" (5 pts). Web framework and AI tooling discussions leading the week.",
          "stats": [],
          "links": [
            { "text": "Proa Framework →", "url": "https://proa.so/" },
            { "text": "Show HN Search →", "url": "https://hn.algolia.com/?type=story&query=Show%20HN" }
          ] }
      ]
    },
    {
      "title": "🎥 YouTube Topics Blowing Up",
      "color": "",
      "type": "cards",
      "items": [
        { "kind": "yt", "icon": "🤖", "title": "Open-Source Robot Arms",
          "desc": "SO-ARM100, Trossen, custom SCARA arms — maker-priced 6-DOF arms paired with LeRobot are producing a wave of hobbyist manipulation projects. Watch: James Bruton + HuggingFace collabs.",
          "stats": [{ "text": "🔥 Hot Topic", "hot": true }], "links": [] },
        { "kind": "yt", "icon": "🏠", "title": "Matter / Zigbee Projects",
          "desc": "ESP32-C6 enabling Zigbee devices built from scratch. Home Assistant Matter integration tutorials are surging. \"Build your own Zigbee sensor\" videos are getting millions of views.",
          "stats": [{ "text": "Rising Fast", "hot": true }], "links": [] },
        { "kind": "yt", "icon": "🦆", "title": "Local Data Analysis Stack",
          "desc": "DuckDB + Polars + Marimo tutorials are multiplying fast. The narrative is \"pandas is fine but here's why pros are switching.\" Very relevant to your WGU BSDA work.",
          "stats": [{ "text": "2025–2026" }], "links": [] },
        { "kind": "yt", "icon": "🧠", "title": "Edge AI on Microcontrollers",
          "desc": "Running small ML models on ESP32-S3 (with AI acceleration) and Pi 5 for local inference. TensorFlow Lite Micro and Edge Impulse are the main tools. OpenMV is the plug-and-play entry point.",
          "stats": [{ "text": "Hot", "hot": true }], "links": [] }
      ]
    },
    {
      "title": "🔗 Live Feed Links",
      "color": "",
      "type": "links",
      "items": [
        { "icon": "🐍", "text": "GitHub Trending — Python (weekly)",       "url": "https://github.com/trending/python?since=weekly", "meta": "Live" },
        { "icon": "📡", "text": "GitHub Trending — C++ / Arduino (weekly)", "url": "https://github.com/trending/c++?since=weekly",    "meta": "Live" },
        { "icon": "🔨", "text": "Hackster.io — Trending Projects",          "url": "https://www.hackster.io/projects?sort=trending",  "meta": "Live" },
        { "icon": "📡", "text": "r/esp32 — Top This Week",                  "url": "https://www.reddit.com/r/esp32/top/?t=week",      "meta": "Weekly" },
        { "icon": "🤖", "text": "r/arduino — Top This Week",                "url": "https://www.reddit.com/r/arduino/top/?t=week",    "meta": "Weekly" },
        { "icon": "💻", "text": "Hacker News — Show HN",                    "url": "https://news.ycombinator.com/show",               "meta": "Daily" },
        { "icon": "🔍", "text": "HN Search — Robotics (past month)",        "url": "https://hn.algolia.com/?dateRange=pastMonth&query=robotics&type=story", "meta": "Filtered" },
        { "icon": "📈", "text": "r/dataanalysis — Top This Week",           "url": "https://www.reddit.com/r/dataanalysis/top/?t=week", "meta": "Weekly" }
      ]
    }
  ]
};

# pubmedsearch-polymind
A simple plugin for [PolyMind](https://github.com/itsme2417/PolyMind) adding a function for PubMed search queries

## Installation:
1. Clone this repository into your PolyMind plugins folder
2. Enter your PolyMind Python venv or conda environment
3. Install the plugin's requirements with `pip install -r requirements.txt`; if this is unsuccessful, you pay need to run `pip install wheel` and try adding the argument `--no-build-isolation`
4. Make a copy of the plugin's `config.example.json` named `config.json` and edit settings as appropriate
5. Edit PolyMind's config.json and add `pubmedsearch-polymind` to the list of enabled plugins

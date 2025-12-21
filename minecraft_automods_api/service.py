import os
import google.generativeai as genai

from dotenv import load_dotenv
from pathlib import Path


from minecraft_modpack_api import (
    enrich_mods,
    resolve_dependencies,
    get_mods_download_urls,
    create_zip_from_links
)

load_dotenv()

api_key = "AIzaSyAW4JK6uexyJoaga-wVv1hYLmud-oR4R8A"
genai.configure(api_key=api_key)
model = genai.GenerativeModel("models/gemini-2.5-flash")

def generate_modpack_and_zip(game_version: str, loader: str, theme: str) -> str:
    prompt = f"""
If the user 'Theme' request IS NOT RELATED to Minecraft mods, AWAYS give 'N/A' as response.
Return ONLY mod names.
One per line.
No explanations.
NEVER repeat mods.
Prioritize EXTREMELY COMPLETE modpacks.
Prioritize including Quality of Life mods, e.g., Mouse Tweaks, Inventory Tweaks, etc.
NEVER deviate from the required modpack theme.
If the user requests a specific number of mods, provide that number without repeats. If it's not possible, aim for the closest amount.
If the user requests specific mods, AWAYS provide them without repeats.

ATTEMPS:
    AVOID mods that are not related to the theme.
    AVOID mods that are not compatible with other mods in the modpack.

RULES:
    NEVER include mods that are not compatible with the loader.
    NEVER include mods that are not compatible with the game version.

Minecraft {game_version}
Loader {loader}

Theme:
{theme}
"""
    print("\n" + "=" * 50)
    print(f"\n=====[ USER REQUEST ]=====\nVersion: {game_version}\nLoader: {loader}\nTheme: {theme}")
    print("\n" + "=" * 50)
    
    print("🤖 Generating mod list...")
    response = model.generate_content(prompt)
    
    if not response or response.text == "N/A":
        raise Exception("Failed to generate mod list: 🚫 User request is not related to Minecraft mods.")
    
    print(f"\n Generated List: \n {response.text}")
    
    initial_mods = [
        m.strip() for m in response.text.split("\n") if m.strip()
    ]
    
    print(f"📚 Total mods before dependency resolution: {len(initial_mods)}")

    mods = enrich_mods(initial_mods, theme)
    validated_slugs = [m["slug"] for m in mods]

    print("\n" + "=" * 50)
    print("🤖 Resolving dependencies...")
    print("=" * 50 + "\n")

    all_slugs = resolve_dependencies(
        validated_slugs,
        game_version,
        loader
    )
    
    print(f"📚 Total mods after dependency resolution: {len(all_slugs)}")

    download_urls = get_mods_download_urls(
        all_slugs,
        game_version,
        loader
    )
    
    zip_filename = f"minecraft_{game_version}_{loader}_modpack.zip"
    zip_path = create_zip_from_links(download_urls, zip_filename)

    print("\n" + "=" * 50)
    print(f"Modpack: {zip_filename} created successfully")
    print("=" * 50 + "\n")

    return zip_path

from minecraft_modpack_api import *
import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-2.5-flash")

mc_version = input("🎮 Minecraft version: ")
loader = input("🧩 Loader: ")
theme = input("🎨 Modpack theme: ")

print("\n" + "=" * 50)
print("🤖 Generating initial mod list...")
print("=" * 50 + "\n")

first_prompt = f"""
Return ONLY mod names.
One per line.
No explanations.
NEVER repeat mods.
If the user requests a specific number of mods, try to provide that number without repeats. If it's not possible, aim for the closest amount.

Minecraft {mc_version}
Loader {loader}

Theme:
{theme}
"""

response = model.generate_content(first_prompt)

initial_mods = [m.strip() for m in response.text.split("\n") if m.strip()]

print("📦 Initial mods generated:")
for mod in initial_mods:
    print(f"  • {mod}")

print("\n" + "=" * 50)
print("🧠 Enriching mod list (metadata lookup)...")
print("=" * 50 + "\n")

mods = enrich_mods(initial_mods, theme)

print(f"📊 Mods found on Modrinth: {len(mods)}")

validated_slugs = [m["slug"] for m in mods]

print("\n✅ Mods accepted (no AI validation):")
for m in mods:
    print(f"  • {m['name']}")

print("\n" + "=" * 50)
print("🧬 Resolving dependencies...")
print("=" * 50 + "\n")

all_slugs = resolve_dependencies(validated_slugs, mc_version, loader)

print(f"📚 Total mods after dependency resolution: {len(all_slugs)}")

print("\n" + "=" * 50)
print("⬇️  Downloading mods...")
print("=" * 50 + "\n")

urls = get_mods_download_urls(all_slugs, mc_version, loader)
download_mod_list(urls)

print("\n" + "=" * 50)
print("✅ Done! Mods downloaded successfully.")
print("📁 Check the ./mods directory")
print("=" * 50)

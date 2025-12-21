import requests
import zipfile
import json
import os
from pathlib import Path
from urllib.parse import urlparse
from typing import List, Dict, Set

MODRINTH_API = "https://api.modrinth.com/v2"

HEADERS = {
    "User-Agent": "minecraft-automods/1.0"
}

extra_game_versions = [
    "1.21.1",
    "1.21.3",
    "1.21.4",
    "1.21.5"
]

SEARCH_CACHE: Dict[str, dict] = {}
VERSIONS_CACHE: Dict[str, list] = {}

def search_for_mod(name: str) -> dict | None:
    if name in SEARCH_CACHE:
        return SEARCH_CACHE[name]

    r = requests.get(
        f"{MODRINTH_API}/search",
        params={
            "query": name,
            "limit": 1,
            "index": "downloads"
        },
        headers=HEADERS,
        timeout=10
    )

    if r.status_code != 200:
        return None

    data = r.json().get("hits", [])
    mod = data[0] if data else None

    SEARCH_CACHE[name] = mod
    return mod

def get_versions(project_id: str, mc_version: str, loader: str) -> list:
    cache_key = f"{project_id}:{mc_version}:{loader}"
    if cache_key in VERSIONS_CACHE:
        return VERSIONS_CACHE[cache_key]

    r = requests.get(
        f"{MODRINTH_API}/project/{project_id}/version",
        params={
            "game_versions": json.dumps([mc_version]),
            "loaders": json.dumps([loader.lower()])
        },
        headers=HEADERS,
        timeout=20
    )

    if r.status_code != 200:
        return []

    versions = r.json()

    valid = [
        v for v in versions
        if mc_version in v.get("game_versions", [])
        and loader.lower() in v.get("loaders", [])
    ]

    valid.sort(key=lambda v: v["date_published"], reverse=True)

    VERSIONS_CACHE[cache_key] = valid
    return valid

def resolve_dependencies(project_ids: List[str], mc_version: str, loader: str) -> List[str]:
    resolved: Set[str] = set(project_ids)
    queue: List[str] = list(project_ids)

    while queue:
        project_id = queue.pop()
        versions = get_versions(project_id, mc_version, loader)
        if not versions:
            continue

        deps = versions[0].get("dependencies", [])
        for dep in deps:
            if dep.get("dependency_type") != "required":
                continue

            dep_id = dep.get("project_id")
            if dep_id and dep_id not in resolved:
                resolved.add(dep_id)
                queue.append(dep_id)

    return list(resolved)

def get_mods_download_urls(project_ids: List[str], mc_version: str, loader: str) -> Set[str]:
    urls: Set[str] = set()

    for project_id in project_ids:
        versions = get_versions(project_id, mc_version, loader)
        if not versions:
            continue

        files = versions[0].get("files", [])
        primary = next((f for f in files if f.get("primary")), None)
        urls.add((primary or files[0])["url"])

    return urls

def download_mod(url: str, mods_dir: str = "./mods"):
    p = Path(mods_dir)
    p.mkdir(exist_ok=True)

    filename = os.path.basename(urlparse(url).path)
    path = p / filename

    with requests.get(url, stream=True, headers=HEADERS, timeout=30) as r:
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)

def download_mod_list(urls: Set[str], mods_dir: str = "./mods"):
    for url in urls:
        download_mod(url, mods_dir)

def enrich_mods(mod_names: List[str], user_request: str) -> List[dict]:
    data = []

    for name in mod_names:
        mod = search_for_mod(name)
        if not mod or mod.get("project_type") != "mod":
            continue

        data.append({
            "name": mod["title"],
            "slug": mod["slug"],
            "project_id": mod["project_id"],
            "downloads": mod.get("downloads", 0),
            "categories": mod.get("categories", []),
            "requested_by_user": name.lower() in user_request.lower()
        })

    return data

def create_zip_from_links(links: Set[str], zip_name: str = "mods.zip"):
    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zipf:
        for url in links:
            r = requests.get(url, headers=HEADERS, timeout=30)
            r.raise_for_status()
            filename = os.path.basename(urlparse(url).path)
            zipf.writestr(filename, r.content)

    return zip_name

def get_avaliable_game_versions() -> List[str]:
    api_versions = requests.get(
        "https://mc-versions-api.net/api/java",
        timeout=10
    ).json()["result"]

    all_versions = api_versions + extra_game_versions
    return sort_versions_desc(all_versions)

def sort_versions_desc(versions: List[str]) -> List[str]:
    def version_key(v: str):
        return tuple(map(int, v.split(".")))

    return sorted(set(versions), key=version_key, reverse=True)

def get_avaliable_loader_versions() -> List[str]:
    return ["forge", "fabric", "neoforge", "quilt"]

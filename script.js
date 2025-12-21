const promptInput = document.querySelector(".prompt-input");
const gameVersion = document.querySelector(".game-version");
const modLoader = document.querySelector(".mod-loader");
const generateButton = document.querySelector(".generate-button");
const soundIcon = document.querySelector(".sound-icon");

const generateButtonSound = document.querySelector("#generate_sound");
const typeSounds = document.querySelectorAll("#type_sound");
const pageSounds = document.querySelectorAll("#page_sfx");
const xpSound = document.querySelector("#xp_sfx");
const breakSound = document.querySelector("#break_sfx");

const automodsApi = "https://corolitic-hattie-pseudoeconomically.ngrok-free.dev";

let mutedSounds = false;


function sendModpackRequest() {
    playSound(generateButtonSound, 0.4);

    const params = {
        game_version: gameVersion.value,
        loader: modLoader.value,
        theme: promptInput.value || promptInput.placeholder
    };

    startLoading();

    fetch(automodsApi + "/generate_modpack", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(params)
    })
    .then(res => {
        if (!res.ok) {
            stopLoading();
            return;
        }
        return res.blob();
    })
    .then(blob => {
        if (!blob) return;

        const url = URL.createObjectURL(blob);
        const fileName = `minecraft_${params.game_version}_${params.loader}_modpack.zip`;

        downloadFile(url, fileName);
        URL.revokeObjectURL(url);
        stopLoading();

        playSound(xpSound, .6);
    })
    .catch(() => {
        stopLoading();
        playSound(breakSound, .5);
    });
}

function playerRandomSound(sounds, volume = 1) {
    const sound = sounds[Math.floor(Math.random() * (sounds.length - 1))];
    playSound(sound, volume);
}

function playSound(sound, volume = 1) {
    if (mutedSounds) return;
    sound.volume = volume;
    sound.currentTime = 0;
    sound.play();
}

function startLoading() {
    generateButton.removeEventListener("click", sendModpackRequest);
    document.removeEventListener("keydown", (e) => e.key === "Enter" && sendModpackRequest());
    generateButton.classList.add("generating");
}

function stopLoading() {
    generateButton.addEventListener("click", sendModpackRequest);
    document.addEventListener("keydown", (e) => e.key === "Enter" && sendModpackRequest());
    generateButton.classList.remove("generating");
}

function downloadFile(url, filename) {
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
}

function updateGameVersionsList() {
    return new Promise((resolve, reject) => fetch(automodsApi + "/game-versions")
        .then(res => res.json())
        .then(data => {
            gameVersion.innerHTML = "";
            data.forEach(version => {
                gameVersion.innerHTML += `<option value="${version}">${version}</option>`;
            });
            gameVersion.classList.remove("loading");
            resolve();
    }) 
        .catch(reject)
    );
}

function updateLoaderVersionsList() {
    return new Promise((resolve, reject) => fetch(automodsApi + "/loader-versions")
        .then(res => res.json())
        .then(data => {
            modLoader.innerHTML = "";
            data.forEach(loader => {
                modLoader.innerHTML += `<option value="${loader}">${loader}</option>`;
            });
            modLoader.classList.remove("loading");
            resolve();
    })
        .catch(reject)
    );
}

function toggleMutedSounds() {
    mutedSounds = !mutedSounds;
}

function toggleMutedSoundsIcon() {
    soundIcon.classList.toggle("muted");
    generateButtonSound.volume = .3;
    generateButtonSound.play();
}

async function setup() {
    soundIcon.addEventListener("click", () => {
        toggleMutedSounds();
        toggleMutedSoundsIcon();
    })

    await updateGameVersionsList();
    await updateLoaderVersionsList();

    generateButton.classList.remove("loading");
    generateButton.addEventListener("click", sendModpackRequest);
    promptInput.addEventListener("input", () => playerRandomSound(typeSounds));
    gameVersion.addEventListener("click", () => playerRandomSound(pageSounds, .4));
    modLoader.addEventListener("click", () => playerRandomSound(pageSounds, .4));
    promptInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            sendModpackRequest();
        }
    });
}

setup();
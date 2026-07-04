/* state.js Serial: #012 */
import { STR_TO_ACC, ACC_TO_STR } from './spelling.js';

export const VOWEL_PRESETS_LEGACY = {
    'i': [270, 2290, 3010], 'y': [270, 1800, 2300], 'ɪ': [390, 1990, 2550],
    'e': [390, 2300, 2850], 'ɛ': [530, 1840, 2480], 'æ': [660, 1720, 2410],
    'a': [730, 1090, 2440], 'ə': [500, 1500, 2500], 'ʌ': [640, 1190, 2390],
    'ɑ': [700, 1100, 2400], 'ɒ': [600, 900, 2400], 'ɔ': [570, 840, 2410],
    'o': [460, 1100, 2490], 'ʊ': [440, 1020, 2240], 'u': [300, 870, 2240],
    'ɚ': [500, 1400, 1600], 'ɑ˞': [700, 1100, 1600], 'ɔ˞': [570, 840, 1600]
};

export const VOWEL_PRESETS_EAR = {
    'i': [270, 2290, 3010], 'y': [270, 1800, 2300], 'ɪ': [390, 1990, 2550],
    'e': [480, 2000, 2600], 'ɛ': [530, 1840, 2480], 'æ': [660, 1720, 2410],
    'a': [730, 1090, 2440], 'ə': [500, 1500, 2500], 'ʌ': [640, 1190, 2390],
    'ɑ': [700, 1100, 2400], 'ɒ': [600, 900, 2400], 'ɔ': [570, 840, 2410],
    'o': [442, 780, 2490], 'ʊ': [440, 1020, 2240], 'u': [300, 750, 1900],
    'ɚ': [500, 1300, 1750], 'ɑ˞': [680, 1250, 1900], 'ɔ˞': [550, 1000, 1900]
};

const AUDIO_MAP = {
    'f1': 'f1', 'f2': 'f2', 'f3': 'f3',
    'jc': 'vibratoJitterCutoff',
    'ja': 'vibratoJitterAmount',
    'pj': 'phaseJitter',
    'vd': 'vibratoDepth',
    'rm': 'vibratoRateMean',
    'rr': 'vibratoRateRange',
    'q1': 'q1',
    'q2': 'q2'
};

const PART_PROPS = { 'p': 'ping', 't': 'tilt', '4': 'f4', '5': 'f5' };

export const appState = {
    chords: [{
        voices: [
            { part: 'Bass', step: 'g', acc: 0, oct: 3 },
            { part: 'Bari', step: 'b', acc: 0, oct: 3 },
            { part: 'Lead', step: 'd', acc: 0, oct: 4 },
            { part: 'Tenor', step: 'f', acc: 0, oct: 4 }
        ],
        tuning: [0, 0, 0, 0],
        analysis: null
    }],
    activeChordIndex: 0,
    ui: {
        selectedIdx: 2,
        focusedElementId: null,
        analysisId: 0,
        offlineMode: false,
        rootless: false
    },
    settings: {
        intonation: 'just',
        vowel: 'a',
        vps: 4,
        duration: 5,
        volume: 0.05,
        presetVersion: 'ear',
        audio: {
            f1: 730, f2: 1090, f3: 2440,
            vibratoJitterCutoff: 100, vibratoJitterAmount: 2.5,
            phaseJitter: 0.08, vibratoDepth: 0.006,
            vibratoRateMean: 5.2, vibratoRateRange: 1.2,
            q1: 10, q2: 15
        },
        partSettings: [
            { name: 'Bass', f4: 3500, f5: 4500, ping: 0.0, tilt: 0.0, volume: 1.0, mute: false },
            { name: 'Bari', f4: 3500, f5: 4500, ping: 0.0, tilt: 0.0, volume: 1.0, mute: false },
            { name: 'Lead', f4: 3500, f5: 4500, ping: 0.0, tilt: 0.0, volume: 1.0, mute: false },
            { name: 'Tenor', f4: 3500, f5: 4500, ping: 0.0, tilt: 0.0, volume: 1.0, mute: false }
        ]
    }
};

export function getNoteString(obj) { 
    if (!obj || !obj.step) return "";
    return obj.step + (ACC_TO_STR[obj.acc] || "") + (obj.oct ?? ""); 
}

export function syncInputsToState() {
    const rToggle = document.getElementById('rootlessToggle');
    if (rToggle) appState.ui.rootless = rToggle.checked;
    
    const oToggle = document.getElementById('offlineToggle');
    if (oToggle) appState.ui.offlineMode = oToggle.checked;

    const vToggle = document.getElementById('legacyVocalToggle');
    if (vToggle) appState.settings.presetVersion = vToggle.checked ? 'legacy' : 'ear';
    
    const intRad = document.querySelector('input[name="intonation"]:checked');
    if (intRad) appState.settings.intonation = intRad.value;
    
    const vowRad = document.querySelector('input[name="vowel"]:checked');
    if (vowRad) appState.settings.vowel = vowRad.value;

    const vps = document.getElementById('vpsCount');
    if (vps) appState.settings.vps = parseInt(vps.value) || 4;
    
    const dur = document.getElementById('duration');
    if (dur) appState.settings.duration = parseFloat(dur.value) || 5;
    
    const vol = document.getElementById('volume');
    if (vol) appState.settings.volume = parseFloat(vol.value) || 0.05;
    
    Object.values(AUDIO_MAP).forEach(key => {
        const id = (key === 'q1') ? 'formantQ1' : (key === 'q2' ? 'formantQ2' : key);
        const el = document.getElementById(id);
        const nel = document.getElementById('n_' + id);
        if (nel && nel === document.activeElement) {
            appState.settings.audio[key] = parseFloat(nel.value) || 0;
        } else if (el) {
            appState.settings.audio[key] = parseFloat(el.value) || 0;
        }
    });

    appState.settings.partSettings.forEach((part, i) => {
        const pingEl = document.getElementById(`part-ping-${i}`);
        if (pingEl) part.ping = parseFloat(pingEl.value) || 0;
        const tiltEl = document.getElementById(`part-tilt-${i}`);
        if (tiltEl) part.tilt = parseFloat(tiltEl.value) || 0;
        const f4El = document.getElementById(`part-f4-${i}`);
        if (f4El) part.f4 = parseFloat(f4El.value) || 3500;
        const f5El = document.getElementById(`part-f5-${i}`);
        if (f5El) part.f5 = parseFloat(f5El.value) || 4500;
        const vEl = document.getElementById(`part-vol-${i}`);
        if (vEl) part.volume = parseFloat(vEl.value) || 0;
        const mEl = document.getElementById(`part-mute-${i}`);
        if (mEl) part.mute = mEl.classList.contains('active');
    });
}

export function syncStateToInputs() {
    const rToggle = document.getElementById('rootlessToggle');
    if (rToggle) rToggle.checked = appState.ui.rootless;

    const oToggle = document.getElementById('offlineToggle');
    if (oToggle) oToggle.checked = appState.ui.offlineMode;

    const vToggle = document.getElementById('legacyVocalToggle');
    if (vToggle) vToggle.checked = (appState.settings.presetVersion === 'legacy');
    
    const intRad = document.querySelector(`input[name="intonation"][value="${appState.settings.intonation}"]`);
    if (intRad) intRad.checked = true;
    
    const vowRad = document.querySelector(`input[name="vowel"][value="${appState.settings.vowel}"]`);
    if (vowRad) vowRad.checked = true;

    const vps = document.getElementById('vpsCount');
    if (vps && document.activeElement !== vps) vps.value = appState.settings.vps;
    
    const dur = document.getElementById('duration');
    if (dur && document.activeElement !== dur) dur.value = appState.settings.duration;
    
    const vol = document.getElementById('volume');
    if (vol && document.activeElement !== vol) vol.value = appState.settings.volume;

    Object.entries(AUDIO_MAP).forEach(([code, key]) => {
        const id = (key === 'q1') ? 'formantQ1' : (key === 'q2' ? 'formantQ2' : key);
        const el = document.getElementById(id);
        const nel = document.getElementById('n_' + id);
        const val = appState.settings.audio[key];
        
        if (el && document.activeElement !== el) el.value = val;
        if (nel && document.activeElement !== nel) nel.value = val;

        const disp = document.getElementById('v_' + id);
        if (disp) {
            let suffix = (id.includes('Rate') || id.includes('Cutoff') || (id.startsWith('f') && !id.includes('Q'))) ? "Hz" : (id === 'phaseJitter' ? "s" : "");
            disp.innerText = val + suffix;
        }
    });

    appState.settings.partSettings.forEach((part, i) => {
        ['ping', 'tilt', 'f4', 'f5', 'vol'].forEach(k => {
            const id = `part-${k}-${i}`;
            const el = document.getElementById(id);
            const val = part[k === 'vol' ? 'volume' : k];
            if (el && document.activeElement !== el) el.value = val;

            const disp = document.getElementById('v_' + id);
            if (disp) {
                if (k === 'ping' || k === 'tilt') disp.innerText = val.toFixed(2);
                else if (k === 'f4' || k === 'f5') disp.innerText = Math.round(val) + "Hz";
            }
        });
        const mEl = document.getElementById(`part-mute-${i}`);
        if (mEl) mEl.classList.toggle('active', part.mute);
    });
}

export function loadStateFromURL() {
    const params = new URLSearchParams(window.location.search);
    const chord = appState.chords[0];
    
    if (params.has('n')) {
        params.get('n').split(',').forEach((n, i) => {
            if (i < 4) {
                const match = n.match(/^([a-gA-G])(bb|b|#|x)?([0-8])$/i);
                if (match) {
                    chord.voices[i].step = match[1].toLowerCase();
                    chord.voices[i].acc = STR_TO_ACC[match[2] ? match[2].toLowerCase() : ""];
                    chord.voices[i].oct = parseInt(match[3]);
                }
            }
        });
    }
    if (params.has('c')) {
        chord.tuning = params.get('c').split(',').map(val => parseFloat(val) || 0);
    }
    if (params.has('t')) appState.settings.intonation = params.get('t');
    if (params.has('v')) {
        appState.settings.vowel = params.get('v');
        const presets = appState.settings.presetVersion === 'legacy' ? VOWEL_PRESETS_LEGACY : VOWEL_PRESETS_EAR;
        const freqs = presets[appState.settings.vowel];
        if (freqs) [appState.settings.audio.f1, appState.settings.audio.f2, appState.settings.audio.f3] = freqs;
    }
    if (params.has('vps')) appState.settings.vps = parseInt(params.get('vps')) || 4;
    
    if (params.has('a')) {
        params.get('a').split(',').forEach(pair => {
            const [code, val] = pair.split(':');
            const num = parseFloat(val);
            if (isNaN(num)) return;

            if (AUDIO_MAP[code]) {
                appState.settings.audio[AUDIO_MAP[code]] = num;
            } else if (code.startsWith('p')) {
                const pIdx = parseInt(code[1]);
                const pProp = PART_PROPS[code[2]];
                if (pIdx < 4 && pProp) appState.settings.partSettings[pIdx][pProp] = num;
            }
        });
    }
    
    syncStateToInputs();
}

export function generatePermalink() {
    const chord = appState.chords[appState.activeChordIndex];
    const p = new URLSearchParams();
    
    p.set('n', chord.voices.map(s => getNoteString(s)).join(','));
    p.set('c', chord.tuning.join(','));
    p.set('t', appState.settings.intonation);
    p.set('v', appState.settings.vowel);
    p.set('vps', appState.settings.vps);
    
    const packed = [];
    Object.entries(AUDIO_MAP).forEach(([code, key]) => {
        if (appState.settings.vowel !== 'custom' && (key === 'f1' || key === 'f2' || key === 'f3')) return;
        packed.push(`${code}:${appState.settings.audio[key]}`);
    });

    appState.settings.partSettings.forEach((ps, i) => {
        Object.entries(PART_PROPS).forEach(([code, key]) => {
            packed.push(`p${i}${code}:${ps[key]}`);
        });
    });

    p.set('a', packed.join(','));
    
    const newUrl = window.location.pathname + '?' + p.toString();
    window.history.replaceState({}, '', newUrl);
    
    if (navigator.clipboard) {
        navigator.clipboard.writeText(window.location.href);
    }
    
    const btn = document.getElementById('shareBtn');
    if (btn) {
        const oldHtml = btn.innerHTML;
        btn.innerHTML = "<span>✅</span> Copied!";
        setTimeout(() => btn.innerHTML = oldHtml, 2000);
    }
}
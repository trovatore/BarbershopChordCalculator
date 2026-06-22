/* main.js Serial: #007 */
import { getAbsSemitone, getVariations, STR_TO_ACC, STEP_TO_SEMI, SERIAL as S_SPEL } from './spelling.js';
import { renderControls, handleGlobalKey, SERIAL as S_UI } from './ui-controls.js';
import { drawChord, SERIAL as S_NOT } from './notation.js';
import { playChord, saveChordAsWav, analyzeAndShow, SERIAL as S_AUD } from './audio.js';
import { analyzeChord, SERIAL as S_THY } from './theory.js';
import { appState, syncInputsToState, syncStateToInputs, loadStateFromURL, generatePermalink, getNoteString, VOWEL_PRESETS } from './state.js';

const S_IDX = "#062";
const SHOW_SERIALS = false;

function getAudioSettings() {
    return {
        ...appState.settings.audio,
        partSettings: appState.settings.partSettings,
        vps: appState.settings.vps,
        duration: appState.settings.duration,
        volume: appState.settings.volume
    };
}

async function fetchAnalysis() {
    const currentId = ++appState.ui.analysisId;
    const chord = appState.chords[appState.activeChordIndex];
    const noteStrs = chord.voices.map(s => getNoteString(s));

    if (appState.ui.offlineMode) {
        const data = analyzeChord(noteStrs, { 
            allow_rootless: appState.ui.rootless, 
            tuning_style: appState.settings.intonation 
        });
        updateAnalysisResult(data, chord);
        return;
    }

    const resultEl = document.getElementById('analysis-result');
    const pendingEl = document.getElementById('pendingIndicator');
    resultEl.classList.add('pending');
    pendingEl.style.display = 'inline';

    try {
        const res = await fetch('/analyze', { 
            method: 'POST', headers: {'Content-Type': 'application/json'}, 
            body: JSON.stringify({ 
                notes: noteStrs, 
                allow_rootless: appState.ui.rootless, 
                tuning_style: appState.settings.intonation 
            }) 
        });
        const data = await res.json();
        if (currentId === appState.ui.analysisId && !data.error) {
            updateAnalysisResult(data, chord);
        }
    } catch (e) { console.error(e); }
    finally {
        if (currentId === appState.ui.analysisId) {
            resultEl.classList.remove('pending');
            pendingEl.style.display = 'none';
        }
    }
}

function updateAnalysisResult(data, chord) {
    chord.analysis = data;
    document.getElementById('chordName').innerText = data.common_name || "Unknown Chord";
    document.getElementById('meta').innerText = (data.inversion + " - " + data.voicing).toUpperCase();
    document.getElementById('roles').innerHTML = (data.notes || []).map(n => "<div>" + n.part + ": <strong>" + n.role + "</strong></div>").join('');
    if (appState.settings.intonation !== 'custom') {
        chord.tuning = data.notes.map(n => n.tuning);
    }
    renderUI();
}

function renderUI() {
    const chord = appState.chords[appState.activeChordIndex];
    renderControls(document.querySelector('.controls'), chord.voices, appState.ui.selectedIdx, chord.tuning, manualUpdate, updateNote, cycleEnharmonic);
    drawChord("notation", chord.voices);
    
    syncStateToInputs();

    if (appState.ui.focusedElementId) {
        const el = document.getElementById(appState.ui.focusedElementId);
        if (el) el.focus();
    }

    const manifestEl = document.getElementById('manifest');
    const docsLink = "<a href='/help' target='_blank'>Documentation (not up to date)</a>";
    if (SHOW_SERIALS) {
        manifestEl.innerHTML = `index: ${S_IDX} | ${docsLink}<br>spel: ${S_SPEL} | ui: ${S_UI} | not: ${S_NOT} | aud: ${S_AUD} | thy: ${S_THY}`;
    } else {
        manifestEl.innerHTML = docsLink;
    }
}

function triggerMutation() {
    syncInputsToState();
    renderUI();
    fetchAnalysis();
}

function updateNote(idx, semiChange) {
    const chord = appState.chords[appState.activeChordIndex];
    const context = chord.voices.map((s, i) => ({ step: s.step, semi: getAbsSemitone(s), idx: i })).filter(n => n.idx !== idx);
    chord.voices[idx] = Object.assign({}, chord.voices[idx], getVariations(getAbsSemitone(chord.voices[idx]) + semiChange, chord.voices[idx].oct, context)[0]);
    triggerMutation();
}

function manualUpdate(idx, val) {
    const match = val.match(/^([a-gA-G])(bb|b|#|x)?([0-8])$/i);
    if (match) {
        const step = match[1].toLowerCase();
        const acc = STR_TO_ACC[match[2] ? match[2].toLowerCase() : ""];
        const oct = parseInt(match[3]);
        const chord = appState.chords[appState.activeChordIndex];
        const context = chord.voices.map((s, i) => ({ step: s.step, semi: getAbsSemitone(s), idx: i })).filter(n => n.idx !== idx);
        chord.voices[idx] = Object.assign({}, chord.voices[idx], getVariations((oct * 12) + STEP_TO_SEMI[step] + acc, chord.voices[idx].oct, context)[0]);
        triggerMutation();
    }
}

function cycleEnharmonic(idx) {
    const chord = appState.chords[appState.activeChordIndex];
    const vars = getVariations(getAbsSemitone(chord.voices[idx]), chord.voices[idx].oct, chord.voices.map((s, i) => ({ step: s.step, semi: getAbsSemitone(s), idx: i })).filter(n => n.idx !== idx));
    let curIdx = vars.findIndex(v => v.step === chord.voices[idx].step && v.acc === chord.voices[idx].acc && v.oct === chord.voices[idx].oct);
    chord.voices[idx] = Object.assign({}, chord.voices[idx], vars[(curIdx + 1) % vars.length]);
    triggerMutation();
}

function init() {
    loadStateFromURL();
    syncStateToInputs();

    document.getElementById('rootlessToggle').onchange = triggerMutation;
    document.getElementById('offlineToggle').onchange = triggerMutation;
    document.getElementById('vpsCount').oninput = triggerMutation;
    document.getElementById('duration').oninput = triggerMutation;
    document.getElementById('volume').oninput = triggerMutation;
    document.querySelectorAll('input[name="intonation"]').forEach(r => r.onchange = triggerMutation);
    
    document.querySelectorAll('input[name="vowel"]').forEach(radio => {
        radio.onchange = () => {
            appState.settings.vowel = radio.value;
            if (radio.value === 'custom') {
                document.getElementById('advDetails').open = true;
            } else {
                const freqs = VOWEL_PRESETS[radio.value];
                if (freqs) {
                    appState.settings.audio.f1 = freqs[0];
                    appState.settings.audio.f2 = freqs[1];
                    appState.settings.audio.f3 = freqs[2];
                }
                syncStateToInputs(); // Ensure UI sliders move to the preset values
            }
            triggerMutation();
        }
    });

    ['f1', 'f2', 'f3', 'vibratoJitterCutoff', 'vibratoJitterAmount', 'phaseJitter', 
     'vibratoDepth', 'vibratoRateMean', 'vibratoRateRange', 'formantQ1', 'formantQ2'].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.oninput = () => {
                if (id.startsWith('f')) {
                    const customRad = document.querySelector('input[name="vowel"][value="custom"]');
                    if (customRad) customRad.checked = true;
                    appState.settings.vowel = 'custom';
                }
                triggerMutation();
            };
        }
    });

    // Part-specific formants listeners
    for (let i = 0; i < 4; i++) {
        ['gain', 'f4', 'f5'].forEach(key => {
            const el = document.getElementById(`part-${key}-${i}`);
            if (el) {
                el.oninput = () => {
                    syncInputsToState();
                    syncStateToInputs(); // This updates the v_part... divs
                    // We call fetchAnalysis but skip it if in offline mode for speed
                    if (!appState.ui.offlineMode) fetchAnalysis();
                };
            }
        });
    }

    document.getElementById('playBtn').onclick = () => playChord(appState.chords[appState.activeChordIndex].voices, appState.chords[appState.activeChordIndex].tuning, getAudioSettings());
    document.getElementById('saveBtn').onclick = () => saveChordAsWav(appState.chords[appState.activeChordIndex].voices, appState.chords[appState.activeChordIndex].tuning, getAudioSettings());
    document.getElementById('shareBtn').onclick = generatePermalink;
    document.getElementById('analyzeBtn').onclick = async () => {
        const btn = document.getElementById('analyzeBtn');
        btn.disabled = true;
        setTimeout(async () => {
            try { await analyzeAndShow(appState.chords[appState.activeChordIndex].voices, appState.chords[appState.activeChordIndex].tuning, getAudioSettings()); }
            finally { btn.disabled = false; }
        }, 50);
    };

    window.addEventListener('selectPart', (e) => {
        appState.ui.selectedIdx = e.detail;
        appState.ui.focusedElementId = null;
        renderUI();
    });

    window.addEventListener('inputFocus', (e) => {
        appState.ui.selectedIdx = e.detail.idx;
        appState.ui.focusedElementId = e.detail.id;
        document.querySelectorAll('.part-ctrl').forEach((c, i) => c.classList.toggle('active', i === appState.ui.selectedIdx));
    });

    window.addEventListener('tuningUpdate', (e) => {
        const chord = appState.chords[appState.activeChordIndex];
        const val = parseFloat(e.detail.val);
        chord.tuning[e.detail.idx] = isNaN(val) ? e.detail.val : val;
        if (e.detail.manual) {
            appState.settings.intonation = 'custom';
            const customInt = document.querySelector('input[name="intonation"][value="custom"]');
            if (customInt) customInt.checked = true;
        }
    });

    window.addEventListener('keydown', (e) => {
        handleGlobalKey(e, 
            { selectedIdx: appState.ui.selectedIdx, isTyping: document.activeElement.tagName === 'INPUT' },
            {
                updateNote,
                cycleEnharmonic,
                renderUI,
                playChord: () => document.getElementById('playBtn').click(),
                navigate: (idx) => {
                    appState.ui.selectedIdx = idx;
                    appState.ui.focusedElementId = null;
                    renderUI();
                }
            }
        );
    });

    renderUI();
    fetchAnalysis();
}

init();

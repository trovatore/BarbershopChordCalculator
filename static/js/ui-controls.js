/* ui-controls.js Serial: #023 */
import { ACC_TO_STR } from './spelling.js';
export const SERIAL = "#023";

/**
 * Renders the four voice control cards.
 */
export function renderControls(container, chordState, selectedIdx, tuningState, onManualUpdate, onUpdateNote, onCycle) {
    container.innerHTML = '';
    chordState.forEach((p, i) => {
        const div = document.createElement('div');
        div.className = `part-ctrl ${i === selectedIdx ? 'active' : ''}`;
        
        // Clicking the card area updates selection but does NOT focus input
        div.onclick = () => {
            window.dispatchEvent(new CustomEvent('selectPart', { detail: i }));
        };
        
        const display = p.step.toUpperCase() + ACC_TO_STR[p.acc] + p.oct;
        const currentTuning = tuningState[i];
        const displayTuning = (currentTuning === "" || currentTuning === undefined) ? "" : (currentTuning > 0 ? "+" + currentTuning : currentTuning);

        div.innerHTML = `
            <div style="font-weight:600; font-size: 0.7rem; margin-bottom:5px; color:#666">${p.part.toUpperCase()}</div>
            <div class="note-row">
                <input type="text" class="note-input" id="note-input-${i}" value="${display}" autocomplete="off">
                <input type="text" class="tuning-input" id="tuning-${i}" title="Adjustment (cents)" value="${displayTuning}" placeholder="0" autocomplete="off">
            </div>
            <div class="btn-group">
                <button class="down-btn" tabindex="-1">↓</button>
                <button class="up-btn" tabindex="-1">↑</button>
                <button class="cycle-btn" tabindex="-1">↻</button>
            </div>`;
        
        const nInput = div.querySelector(`#note-input-${i}`);
        nInput.onchange = (e) => onManualUpdate(i, e.target.value);
        nInput.onclick = (e) => { e.stopPropagation(); nInput.focus(); };
        nInput.onfocus = () => {
            setTimeout(() => nInput.select(), 0);
            window.dispatchEvent(new CustomEvent('inputFocus', { detail: { idx: i, id: nInput.id } }));
        };

        const tInput = div.querySelector(`#tuning-${i}`);
        tInput.onclick = (e) => { e.stopPropagation(); tInput.focus(); };
        tInput.onfocus = () => {
            setTimeout(() => tInput.select(), 0);
            window.dispatchEvent(new CustomEvent('inputFocus', { detail: { idx: i, id: tInput.id } }));
        };
        
        tInput.oninput = (e) => {
            window.dispatchEvent(new CustomEvent('tuningUpdate', { 
                detail: { idx: i, val: e.target.value, manual: true } 
            }));
        };
        
        div.querySelector('.down-btn').onclick = (e) => { e.stopPropagation(); onUpdateNote(i, -1); };
        div.querySelector('.up-btn').onclick = (e) => { e.stopPropagation(); onUpdateNote(i, 1); };
        div.querySelector('.cycle-btn').onclick = (e) => { e.stopPropagation(); onCycle(i); };
        
        container.appendChild(div);
    });
}

/**
 * Shared Keyboard Logic: Handles navigation and quick-entry replacement.
 */
export function handleGlobalKey(e, state, callbacks) {
    const { selectedIdx, isTyping } = state;
    const { updateNote, cycleEnharmonic, renderUI, playChord, navigate } = callbacks;

    // Navigation (Arrows) always terminate typing and move voice
    if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
        e.preventDefault();
        if (isTyping) document.activeElement.blur();
        const nextIdx = (e.key === 'ArrowLeft') ? (selectedIdx + 3) % 4 : (selectedIdx + 1) % 4;
        navigate(nextIdx);
        return;
    }

    if (isTyping) {
        if (e.key === 'Enter') document.activeElement.blur();
        return; // Let Tab and normal typing work
    }

    // Quick Entry: Note [A-G] -> Replace Note
    if (e.key.match(/^[a-g]$/i)) {
        e.preventDefault();
        const input = document.getElementById(`note-input-${selectedIdx}`);
        if (input) {
            input.focus();
            setTimeout(() => {
                input.value = e.key.toUpperCase();
                input.setSelectionRange(1, 1);
            }, 10);
        }
        return;
    }

    // Quick Entry: [0-9, +, -] -> Replace Cents & Switch to Custom
    if (e.key.match(/^[0-9\+\-]$/)) {
        e.preventDefault();
        const input = document.getElementById(`tuning-${selectedIdx}`);
        if (input) {
            input.focus();
            setTimeout(() => {
                input.value = e.key;
                input.setSelectionRange(1, 1);
                window.dispatchEvent(new CustomEvent('tuningUpdate', { 
                    detail: { idx: selectedIdx, val: e.key, manual: true } 
                }));
            }, 10);
        }
        return;
    }

    if (e.key === 'p') { e.preventDefault(); playChord(); }
    if (e.key === 'ArrowUp') { e.preventDefault(); updateNote(selectedIdx, 1); }
    if (e.key === 'ArrowDown') { e.preventDefault(); updateNote(selectedIdx, -1); }
    if (e.key === 'Enter') { e.preventDefault(); cycleEnharmonic(selectedIdx); }
}
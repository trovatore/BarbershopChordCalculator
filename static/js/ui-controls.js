/* ui-controls.js Serial: #020 */
import { ACC_TO_STR } from './spelling.js';
export const SERIAL = "#020";

export function renderControls(container, chordState, selectedIdx, tuningState, onManualUpdate, onUpdateNote, onCycle) {
    container.innerHTML = '';
    chordState.forEach((p, i) => {
        const div = document.createElement('div');
        div.className = `part-ctrl ${i === selectedIdx ? 'active' : ''}`;
        
        div.onclick = () => {
            const input = document.getElementById(`note-input-${i}`);
            if (input) input.focus();
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
        nInput.onclick = (e) => e.stopPropagation();
        nInput.onfocus = () => {
            // setTimeout ensures selection happens AFTER the browser finishes focusing
            setTimeout(() => nInput.select(), 0);
            window.dispatchEvent(new CustomEvent('inputFocus', { detail: { idx: i, id: nInput.id } }));
        };

        const tInput = div.querySelector(`#tuning-${i}`);
        tInput.onclick = (e) => e.stopPropagation();
        tInput.onfocus = () => {
            setTimeout(() => tInput.select(), 0);
            window.dispatchEvent(new CustomEvent('inputFocus', { detail: { idx: i, id: tInput.id } }));
        };
        
        tInput.oninput = (e) => {
            window.dispatchEvent(new CustomEvent('tuningUpdate', { 
                detail: { idx: i, val: e.target.value } 
            }));
        };
        
        div.querySelector('.down-btn').onclick = (e) => { e.stopPropagation(); onUpdateNote(i, -1); };
        div.querySelector('.up-btn').onclick = (e) => { e.stopPropagation(); onUpdateNote(i, 1); };
        div.querySelector('.cycle-btn').onclick = (e) => { e.stopPropagation(); onCycle(i); };
        
        container.appendChild(div);
    });
}
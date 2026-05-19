import { ACC_TO_STR } from './spelling.js';
export const SERIAL = "#013";

export function renderControls(container, chordState, selectedIdx, onManualUpdate, onUpdateNote, onCycle) {
    container.innerHTML = '';
    chordState.forEach((p, i) => {
        const div = document.createElement('div');
        div.className = `part-ctrl ${i === selectedIdx ? 'active' : ''}`;
        div.onclick = () => { window.dispatchEvent(new CustomEvent('selectPart', {detail: i})); };
        const display = p.step.toUpperCase() + ACC_TO_STR[p.acc] + p.oct;
        div.innerHTML = `
            <div style="font-weight:600; font-size: 0.7rem; margin-bottom:5px; color:#666">${p.part.toUpperCase()}</div>
            <input type="text" class="note-input" value="${display}">
            <div class="btn-group">
                <button class="down-btn">↓</button>
                <button class="up-btn">↑</button>
                <button class="cycle-btn">↻</button>
            </div>`;
        
        const input = div.querySelector('input');
        input.onchange = (e) => onManualUpdate(i, e.target.value);
        input.onclick = (e) => e.stopPropagation();
        div.querySelector('.down-btn').onclick = (e) => { e.stopPropagation(); onUpdateNote(i, -1); };
        div.querySelector('.up-btn').onclick = (e) => { e.stopPropagation(); onUpdateNote(i, 1); };
        div.querySelector('.cycle-btn').onclick = (e) => { e.stopPropagation(); onCycle(i); };
        
        container.appendChild(div);
    });
}

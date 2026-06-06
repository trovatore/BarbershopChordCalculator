/* audio.js Serial: #007 */
import { getAbsSemitone } from './spelling.js';

export const SERIAL = "#007";

let audioCtx = null;
const FORMANT_MAP = {
    'a': [730, 1090, 2440], 'æ': [660, 1720, 2410], 'ɛ': [530, 1840, 2480],
    'ʌ': [640, 1190, 2390], 'ɔ': [570, 840, 2410], 'e': [390, 2300, 2850],
    'o': [460, 1100, 2490], 'i': [270, 2290, 3010], 'ɪ': [390, 1990, 2550],
    'ʊ': [440, 1020, 2240], 'u': [300, 870, 2240]
};

function createVoice(ctx, freq, vowel, startTime, duration) {
    const attack = 0.15, release = 0.5;
    const formants = FORMANT_MAP[vowel] || FORMANT_MAP['a'];
    const osc = ctx.createOscillator();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(freq, startTime);

    const vibrato = ctx.createOscillator();
    const vibratoGain = ctx.createGain();
    vibrato.frequency.value = 4.8 + (Math.random() * 0.4);
    vibratoGain.gain.value = freq * 0.006;
    vibrato.connect(vibratoGain); vibratoGain.connect(osc.frequency);

    const voiceGain = ctx.createGain();
    voiceGain.gain.setValueAtTime(0, startTime);
    voiceGain.gain.linearRampToValueAtTime(0.05, startTime + attack);
    voiceGain.gain.setValueAtTime(0.05, startTime + duration - release);
    voiceGain.gain.exponentialRampToValueAtTime(0.0001, startTime + duration);

    formants.forEach((f, idx) => {
        const filter = ctx.createBiquadFilter();
        filter.type = 'bandpass';
        filter.frequency.value = f;
        filter.Q.value = idx === 0 ? 10 : 15;
        osc.connect(filter); filter.connect(voiceGain);
    });
    return { osc, vibrato, gain: voiceGain };
}

function setupAudioGraph(ctx, chordState, vowel, startTime, duration, tuningData, multiChannel = false) {
    let merger = null;
    if (multiChannel) {
        merger = ctx.createChannelMerger(4);
        merger.connect(ctx.destination);
    }
    chordState.forEach((note, i) => {
        const cents = (tuningData && tuningData[i] !== undefined) ? tuningData[i] : 0;
        const freq = 440 * Math.pow(2, (getAbsSemitone(note) - 57 + (cents / 100)) / 12);
        const voice = createVoice(ctx, freq, vowel, startTime, duration);
        if (multiChannel) voice.gain.connect(merger, 0, i);
        else voice.gain.connect(ctx.destination);
        voice.osc.start(startTime); voice.vibrato.start(startTime);
        voice.osc.stop(startTime + duration); voice.vibrato.stop(startTime + duration);
    });
}

export function playChord(chordState, vowel = 'a', tuningData = null) {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if (audioCtx.state === 'suspended') audioCtx.resume();
    setupAudioGraph(audioCtx, chordState, vowel, audioCtx.currentTime, 5.0, tuningData);
}

export async function saveChordAsWav(chordState, vowel = 'a', tuningData = null) {
    const duration = 5.0, sr = 44100;
    const offlineCtx = new OfflineAudioContext(4, sr * duration, sr);
    setupAudioGraph(offlineCtx, chordState, vowel, 0, duration, tuningData, true);
    const buffer = await offlineCtx.startRendering();
    const data = new Float32Array(buffer.length * 4);
    for (let i = 0; i < buffer.length; i++) {
        for (let ch = 0; ch < 4; ch++) data[i * 4 + ch] = buffer.getChannelData(ch)[i];
    }
    const blob = encodeWAV(data, 4, sr);
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `chord_4channel_${vowel}.wav`;
    link.click();
}

/**
 * Standard Radix-2 FFT Implementation (O(N log N))
 */
export function fft(real, imag) {
    const n = real.length;
    if (n <= 1) return;
    const evenReal = new Float32Array(n / 2), evenImag = new Float32Array(n / 2);
    const oddReal = new Float32Array(n / 2), oddImag = new Float32Array(n / 2);
    for (let i = 0; i < n / 2; i++) {
        evenReal[i] = real[2 * i]; evenImag[i] = imag[2 * i];
        oddReal[i] = real[2 * i + 1]; oddImag[i] = imag[2 * i + 1];
    }
    fft(evenReal, evenImag); fft(oddReal, oddImag);
    for (let k = 0; k < n / 2; k++) {
        const angle = -2 * Math.PI * k / n;
        const cos = Math.cos(angle), sin = Math.sin(angle);
        const tReal = oddReal[k] * cos - oddImag[k] * sin;
        const tImag = oddReal[k] * sin + oddImag[k] * cos;
        real[k] = evenReal[k] + tReal; imag[k] = evenImag[k] + tImag;
        real[k + n / 2] = evenReal[k] - tReal; imag[k + n / 2] = evenImag[k] - tImag;
    }
}

export function getMagnitudes(signal, sr) {
    const n = signal.length;
    const real = new Float32Array(signal), imag = new Float32Array(n);
    fft(real, imag);
    const mag = new Float32Array(n / 2);
    const freqs = new Float32Array(n / 2).map((_, i) => i * sr / n);
    for (let i = 0; i < n / 2; i++) {
        const m = Math.sqrt(real[i] * real[i] + imag[i] * imag[i]) / n;
        mag[i] = 20 * Math.log10(m + 1e-9);
    }
    return { freqs, mag };
}

export async function analyzeAndShow(chordState, vowel, tuningData) {
    const duration = 5.0, sr = 44100, N = 16384; 
    const offlineCtx = new OfflineAudioContext(4, sr * duration, sr);
    setupAudioGraph(offlineCtx, chordState, vowel, 0, duration, tuningData, true);
    const buffer = await offlineCtx.startRendering();
    
    const analysis = { freqs: [], parts: [] };
    const hann = new Float32Array(N).map((_, i) => 0.5 * (1 - Math.cos(2 * Math.PI * i / (N - 1))));
    const names = ['Bass', 'Bari', 'Lead', 'Tenor'];
    const summedData = new Float32Array(N);

    for (let ch = 0; ch < 4; ch++) {
        const samples = buffer.getChannelData(ch).slice(sr * 2, sr * 2 + N);
        const windowed = samples.map((s, i) => s * hann[i]);
        const { freqs, mag } = getMagnitudes(windowed, sr);
        if (ch === 0) analysis.freqs = Array.from(freqs);
        analysis.parts.push({ name: names[ch], magnitudes: Array.from(mag), peaks: findPeaks(mag, freqs) });
        samples.forEach((s, i) => summedData[i] += s / 4);
    }

    const summedMag = getMagnitudes(summedData.map((s, i) => s * hann[i]), sr).mag;
    analysis.parts.push({ name: 'Summed', magnitudes: Array.from(summedMag), peaks: findPeaks(summedMag, analysis.freqs) });

    localStorage.setItem('chordAnalysisData', JSON.stringify(analysis));
    window.open('/analysis', '_blank');
}

export function findPeaks(mag, freqs) {
    const peaks = [];
    const minSNR = 10;
    for (let i = 2; i < mag.length - 2; i++) {
        if (mag[i] > mag[i-1] && mag[i] > mag[i+1] && mag[i] > -70) {
            const localMean = (mag[i-2] + mag[i-1] + mag[i+1] + mag[i+2]) / 4;
            if (mag[i] - localMean > minSNR) {
                const alpha = mag[i-1], beta = mag[i], gamma = mag[i+1];
                const p = 0.5 * (alpha - gamma) / (alpha - 2*beta + gamma);
                const preciseFreq = freqs[i] + p * (freqs[1] - freqs[0]);
                peaks.push({ freq: Math.round(preciseFreq * 10) / 10, db: Math.round(beta), ...getNoteInfo(preciseFreq) });
            }
        }
    }
    return peaks.sort((a, b) => b.db - a.db).slice(0, 10);
}

export function getNoteInfo(f) {
    const semis = 12 * Math.log2(f / 440) + 57;
    const noteNames = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"];
    const rounded = Math.round(semis);
    const note = noteNames[((rounded % 12) + 12) % 12] + Math.floor(rounded / 12);
    const cents = Math.round((semis - rounded) * 100);
    return { note, cents };
}

function encodeWAV(samples, numChannels, sr) {
    const buffer = new ArrayBuffer(44 + samples.length * 2);
    const view = new DataView(buffer);
    const writeStr = (o, s) => { for (let i = 0; i < s.length; i++) view.setUint8(o + i, s.charCodeAt(i)); };
    writeStr(0, 'RIFF'); view.setUint32(4, 36 + samples.length * 2, true); writeStr(8, 'WAVE');
    writeStr(12, 'fmt '); view.setUint32(16, 16, true); view.setUint16(20, 1, true);
    view.setUint16(22, numChannels, true); view.setUint32(24, sr, true);
    view.setUint32(28, sr * numChannels * 2, true); view.setUint16(32, numChannels * 2, true);
    view.setUint16(34, 16, true); writeStr(36, 'data'); view.setUint32(40, samples.length * 2, true);
    for (let i = 0, o = 44; i < samples.length; i++, o += 2) {
        let s = Math.max(-1, Math.min(1, samples[i]));
        view.setInt16(o, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
    }
    return new Blob([buffer], { type: 'audio/wav' });
}
/* audio.js Serial: #003 */
import { getAbsSemitone } from './spelling.js';

export const SERIAL = "#003";

let audioCtx = null;

const FORMANT_MAP = {
    'a': [730, 1090, 2440],
    'æ': [660, 1720, 2410],
    'ɛ': [530, 1840, 2480],
    'ʌ': [640, 1190, 2390],
    'ɔ': [570, 840, 2410],
    'e': [390, 2300, 2850],
    'o': [460, 1100, 2490],
    'i': [270, 2290, 3010],
    'ɪ': [390, 1990, 2550],
    'ʊ': [440, 1020, 2240],
    'u': [300, 870, 2240]
};

/**
 * Shared synthesis logic for both real-time playback and offline rendering.
 */
function createVoice(ctx, freq, vowel, startTime, duration) {
    const attack = 0.15;
    const release = 0.5;
    const formants = FORMANT_MAP[vowel] || FORMANT_MAP['a'];

    // Source: Sawtooth
    const osc = ctx.createOscillator();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(freq, startTime);

    // Vibrato
    const vibrato = ctx.createOscillator();
    const vibratoGain = ctx.createGain();
    vibrato.frequency.value = 4.8 + (Math.random() * 0.4);
    vibratoGain.gain.value = freq * 0.006;
    vibrato.connect(vibratoGain);
    vibratoGain.connect(osc.frequency);

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
        osc.connect(filter);
        filter.connect(voiceGain);
    });

    return { osc, vibrato, gain: voiceGain };
}

export function playChord(chordState, vowel = 'a', tuningData = null) {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if (audioCtx.state === 'suspended') audioCtx.resume();

    const now = audioCtx.currentTime;
    const duration = 5.0;

    chordState.forEach((note, i) => {
        const semi = getAbsSemitone(note);
        const cents = (tuningData && tuningData[i] !== undefined) ? tuningData[i] : 0;
        const freq = 440 * Math.pow(2, (semi - 57 + (cents / 100)) / 12);

        const voice = createVoice(audioCtx, freq, vowel, now, duration);
        voice.gain.connect(audioCtx.destination);
        voice.osc.start(now);
        voice.vibrato.start(now);
        voice.osc.stop(now + duration);
        voice.vibrato.stop(now + duration);
    });
}

/**
 * Renders the chord to a WAV blob and triggers a download.
 */
export async function saveChordAsWav(chordState, vowel = 'a', tuningData = null) {
    const sampleRate = 44100;
    const duration = 5.0;
    const offlineCtx = new OfflineAudioContext(1, sampleRate * duration, sampleRate);

    chordState.forEach((note, i) => {
        const semi = getAbsSemitone(note);
        const cents = (tuningData && tuningData[i] !== undefined) ? tuningData[i] : 0;
        const freq = 440 * Math.pow(2, (semi - 57 + (cents / 100)) / 12);

        const voice = createVoice(offlineCtx, freq, vowel, 0, duration);
        voice.gain.connect(offlineCtx.destination);
        voice.osc.start(0);
        voice.vibrato.start(0);
        voice.osc.stop(duration);
        voice.vibrato.stop(duration);
    });

    const renderedBuffer = await offlineCtx.startRendering();
    const wavBlob = encodeWAV(renderedBuffer);
    
    const url = URL.createObjectURL(wavBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `chord_${vowel}_${new Date().getTime()}.wav`;
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
}

/**
 * Simple PCM WAV encoder helper
 */
function encodeWAV(buffer) {
    const numChannels = 1;
    const sampleRate = buffer.sampleRate;
    const format = 1; // PCM
    const bitDepth = 16;
    
    const samples = buffer.getChannelData(0);
    const bytesPerSample = bitDepth / 8;
    const blockAlign = numChannels * bytesPerSample;
    
    const bufferData = new ArrayBuffer(44 + samples.length * bytesPerSample);
    const view = new DataView(bufferData);
    
    const writeString = (offset, string) => {
        for (let i = 0; i < string.length; i++) {
            view.setUint8(offset + i, string.charCodeAt(i));
        }
    };

    writeString(0, 'RIFF');
    view.setUint32(4, 36 + samples.length * bytesPerSample, true);
    writeString(8, 'WAVE');
    writeString(12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, format, true);
    view.setUint16(22, numChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * blockAlign, true);
    view.setUint16(32, blockAlign, true);
    view.setUint16(34, bitDepth, true);
    writeString(36, 'data');
    view.setUint32(40, samples.length * bytesPerSample, true);

    let offset = 44;
    for (let i = 0; i < samples.length; i++, offset += 2) {
        let s = Math.max(-1, min(1, samples[i]));
        view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
    }

    function min(a, b) { return a < b ? a : b; }

    return new Blob([bufferData], { type: 'audio/wav' });
}
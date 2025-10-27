"""
Audio Transcription Service using Basic Pitch
"""
import base64
import time
import tempfile
import os
from typing import Dict, Optional, List, Tuple
try:
    import pretty_midi
    PRETTY_MIDI_AVAILABLE = True
except ImportError:
    PRETTY_MIDI_AVAILABLE = False

# Audio processing imports
try:
    import numpy as np
    import librosa
    import soundfile as sf
    from basic_pitch.inference import predict as bp_predict
    BASIC_PITCH_AVAILABLE = True
except ImportError as e:
    BASIC_PITCH_AVAILABLE = False
    print(f"Basic Pitch not available: {e}")

try:
    import crepe
    CREPE_AVAILABLE = True
except ImportError as e:
    CREPE_AVAILABLE = False
    print(f"CREPE not available: {e}")

from ..config import settings

class AudioTranscriptionService:
    """Service for transcribing audio to ABC notation using Basic Pitch"""
    
    def __init__(self):
        self.model = None  # We'll pass model_path to predict function directly
        
    async def transcribe_audio(self, audio_data: str, audio_format: str, use_crepe: bool = False) -> Dict:
        """
        Transcribe audio to ABC notation
        
        Args:
            audio_data: Base64 encoded audio data
            audio_format: Audio format (wav, mp3, m4a)
            
        Returns:
            Dict with transcription results
        """
        if use_crepe and not CREPE_AVAILABLE:
            raise Exception("CREPE is not available. Please install the 'crepe' package.")
        if (not use_crepe) and not BASIC_PITCH_AVAILABLE:
            raise Exception("Basic Pitch is not available. Please install audio dependencies.")
        
        start_time = time.time()
        
        try:
            # Decode base64 audio data
            audio_bytes = base64.b64decode(audio_data)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=f".{audio_format}", delete=False) as temp_file:
                temp_file.write(audio_bytes)
                temp_file_path = temp_file.name
            
            try:
                # Load audio with librosa to get metadata
                target_sr = 16000 if use_crepe else 22050
                audio, sample_rate = librosa.load(temp_file_path, sr=target_sr, mono=True)

                # Transcribe: CREPE or Basic Pitch
                if use_crepe:
                    midi_data, note_events = self._transcribe_with_crepe(audio, sample_rate)
                else:
                    model_output, midi_data, note_events = self._transcribe_with_basic_pitch(temp_file_path)
                
                # Convert MIDI to ABC notation
                abc_notation = await self._midi_to_abc(midi_data, note_events, sample_rate)
                
                # Analyze the audio for metadata
                key_detected = self._detect_key(audio, sample_rate)
                time_signature = self._detect_time_signature(audio, sample_rate)
                notes_detected = len(note_events) if note_events else 0
                
                processing_time = int((time.time() - start_time) * 1000)
                
                return {
                    'abc_notation': abc_notation,
                    'confidence': self._calculate_confidence(midi_data, note_events),
                    'key_detected': key_detected,
                    'time_signature': time_signature,
                    'notes_detected': notes_detected,
                    'processing_time_ms': processing_time
                }
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            raise Exception(f"Audio transcription failed: {str(e)}")

    def _transcribe_with_basic_pitch(self, file_path: str) -> Tuple[object, pretty_midi.PrettyMIDI, list]:
        """Run Basic Pitch and return (model_output, pretty_midi, note_events)."""
        model_output, midi_data, note_events = bp_predict(file_path)
        return model_output, midi_data, note_events

    def _transcribe_with_crepe(self, audio: np.ndarray, sample_rate: int) -> Tuple[pretty_midi.PrettyMIDI, list]:
        """Use CREPE to estimate F0 and build a monophonic PrettyMIDI."""
        # Predict pitch track (10 ms hop)
        times, freqs, confidences, _ = crepe.predict(audio, sample_rate, viterbi=True, step_size=10, verbose=0)
        # Convert to MIDI numbers; mask low-confidence frames
        midi_vals: List[Optional[float]] = []
        for f, c in zip(freqs, confidences):
            if c < 0.5 or f <= 0:
                midi_vals.append(None)
            else:
                midi_vals.append(69 + 12 * np.log2(f / 440.0))

        # Quantize to nearest semitone and group into notes
        notes: List[Tuple[float, float, int, int]] = []  # (start_s, end_s, pitch, velocity)
        cur_pitch: Optional[int] = None
        cur_start: Optional[float] = None
        for t, m in zip(times, midi_vals):
            q = int(round(m)) if m is not None else None
            if q is None:
                if cur_pitch is not None and cur_start is not None:
                    notes.append((cur_start, t, cur_pitch, 80))
                    cur_pitch = None
                    cur_start = None
                continue
            if cur_pitch is None:
                cur_pitch = q
                cur_start = t
            elif q != cur_pitch:
                # pitch change → close previous
                notes.append((cur_start, t, cur_pitch, 80))
                cur_pitch = q
                cur_start = t
        # tail
        if cur_pitch is not None and cur_start is not None:
            notes.append((cur_start, times[-1] if len(times) else cur_start + 0.1, cur_pitch, 80))

        # Merge very short notes and remove spurious blips (<80 ms)
        merged: List[Tuple[float, float, int, int]] = []
        for s, e, p, v in notes:
            if e - s < 0.08:
                continue
            if merged and p == merged[-1][2] and s - merged[-1][1] < 0.05:
                ms = merged[-1]
                merged[-1] = (ms[0], e, p, v)
            else:
                merged.append((s, e, p, v))

        pm = pretty_midi.PrettyMIDI()
        inst = pretty_midi.Instrument(program=0)
        for s, e, p, v in merged:
            inst.notes.append(pretty_midi.Note(velocity=v, pitch=int(p), start=float(s), end=float(max(e, s + 0.05))))
        pm.instruments.append(inst)
        return pm, inst.notes
    
    async def _midi_to_abc(self, midi_data: pretty_midi.PrettyMIDI, note_events: list, sample_rate: int) -> str:
        """Convert MIDI data to simplified ABC melody using heuristic anchors."""
        try:
            # Flatten all notes
            notes = []
            for instrument in midi_data.instruments:
                for note in instrument.notes:
                    notes.append({
                        'pitch': note.pitch,
                        'start': float(note.start),
                        'end': float(note.end),
                        'velocity': int(note.velocity)
                    })
            if not notes:
                return "\n".join(["X:1", "T:Transcribed Melody", "M:4/4", "L:1/4", "K:C"])  # empty

            notes.sort(key=lambda x: x['start'])

            # Estimate tempo to derive quarter duration; fall back to 120 BPM
            try:
                tempo = pretty_midi.estimate_tempo(midi_data)
                beat_length = 60.0 / tempo if tempo and tempo > 0 else 0.5
            except Exception:
                beat_length = 0.5

            # Choose segment count based on phrase length (4–8 anchors)
            end_time = max(n['end'] for n in notes)
            approx_beats = max(1, int(round(end_time / beat_length)))
            segments = min(8, max(4, approx_beats // 2))

            anchors = self._pick_segment_anchors(notes, segments)

            # Transpose so first pitch class maps to C
            if anchors:
                first_pc = anchors[0]['pitch'] % 12
                transpose = (12 - first_pc) % 12
            else:
                transpose = 0

            abc_line = self._anchors_to_abc_line(anchors, transpose, beat_length)

            return "\n".join([
                "X:1",
                "T:Transcribed Melody",
                "M:4/4",
                "L:1/4",
                "K:C",
                abc_line
            ])

        except Exception as e:
            raise Exception(f"Failed to convert MIDI to ABC: {str(e)}")
    
    def _pitch_to_abc(self, midi_note: int) -> str:
        """Convert MIDI note number to ABC note"""
        # Keep simple pitch-class spelling to match our ABC simplifier style
        pc_map = {
            0: 'C', 1: '^C', 2: 'D', 3: '^D', 4: 'E', 5: 'F', 6: '^F', 7: 'G', 8: '^G', 9: 'A', 10: '_B', 11: 'B'
        }
        return pc_map[midi_note % 12]

    def _pick_segment_anchors(self, notes: list, segments: int) -> list:
        """Pick one salient note per segment by duration/velocity/scale membership."""
        if not notes or segments <= 0:
            return []
        end_time = max(n['end'] for n in notes)
        seg_len = end_time / segments
        major_set = {0, 2, 4, 5, 7, 9, 11}
        anchors = []
        for i in range(segments):
            a = i * seg_len
            b = (i + 1) * seg_len if i < segments - 1 else end_time + 1e-6
            cand = []
            for n in notes:
                if a <= n['start'] < b:
                    dur = max(0.0, n['end'] - n['start'])
                    pc = n['pitch'] % 12
                    sal = dur + (n['velocity'] / 127.0) * 0.1 + (pc in major_set) * 0.05 + (n['pitch'] / 127.0) * 0.02
                    cand.append((sal, n))
            if not cand:
                continue
            cand.sort(key=lambda x: x[0], reverse=True)
            anchors.append(cand[0][1])
        return anchors

    def _anchors_to_abc_line(self, anchors: list, transpose: int, beat_length: float) -> str:
        """Convert anchors to a single ABC melody line using coarse durations."""
        tokens = []
        for n in anchors:
            pc = (n['pitch'] + transpose) % 12
            base = self._pitch_to_abc(pc)
            dur = max(0.0, n['end'] - n['start'])
            # Express duration as multiples of a quarter note
            q = 1.0 if beat_length <= 0 else dur / beat_length
            # Collapse to half/quarter/eighth
            if abs(q - 2.0) < 0.35:
                suf = '2'
            elif abs(q - 1.0) < 0.35:
                suf = ''
            elif abs(q - 0.5) < 0.25:
                suf = '/'
            else:
                suf = ''
            tokens.append(base + suf)
        return " ".join(tokens)
    
    def _detect_key(self, audio: np.ndarray, sample_rate: int) -> str:
        """Detect the key signature of the audio"""
        try:
            # Use librosa to detect key
            chroma = librosa.feature.chroma_stft(y=audio, sr=sample_rate)
            key_profiles = {
                'C': [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
                'G': [1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
                'D': [1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
            }
            
            # Simple key detection (this is a basic implementation)
            return "C"  # Default to C major
            
        except Exception:
            return "C"
    
    def _detect_time_signature(self, audio: np.ndarray, sample_rate: int) -> str:
        """Detect the time signature of the audio"""
        try:
            # Use librosa to detect tempo and infer time signature
            tempo, _ = librosa.beat.beat_track(y=audio, sr=sample_rate)
            
            if 100 <= tempo <= 160:
                return "4/4"
            elif 60 <= tempo <= 100:
                return "3/4"
            else:
                return "4/4"
                
        except Exception:
            return "4/4"
    
    def _calculate_confidence(self, midi_data: pretty_midi.PrettyMIDI, note_events: list) -> float:
        """Calculate confidence score for the transcription"""
        if not midi_data or not note_events:
            return 0.0
        
        # Simple confidence calculation based on number of notes detected
        note_count = len(note_events)
        if note_count == 0:
            return 0.0
        elif note_count < 3:
            return 0.3
        elif note_count < 10:
            return 0.6
        else:
            return 0.85

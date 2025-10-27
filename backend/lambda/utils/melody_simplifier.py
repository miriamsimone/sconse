import io
import base64
from typing import List, Tuple, Optional

try:
    import mido
except Exception as e:  # pragma: no cover
    mido = None


MAJOR_SCALE_PITCH_CLASSES = {0, 2, 4, 5, 7, 9, 11}

PITCH_CLASS_TO_ABC = {
    0: 'C',
    1: '^C',
    2: 'D',
    3: '^D',
    4: 'E',
    5: 'F',
    6: '^F',
    7: 'G',
    8: '^G',
    9: 'A',
    10: '_B',
    11: 'B',
}


class MidiMelodySimplifier:
    """Extract a simplified monophonic melody from a MIDI and export to ABC.

    Heuristics:
      - Parse note events from the densest track
      - Quantize to beats (quarter notes)
      - Divide into N segments and pick the most salient note per segment
      - Optionally align first anchor to C (transpose) for normalized output
      - Optionally snap durations to quarters/halves/eighths
    """

    def __init__(self, default_segments: int = 4) -> None:
        self.default_segments = default_segments

    def simplify_b64_to_abc(
        self,
        midi_b64: str,
        segments: Optional[int] = None,
        align_first_to_c: bool = True,
        include_headers: bool = True,
        meter: str = '4/4',
        base_length: str = '1/4',
        target_abc_line: Optional[str] = None,
    ) -> str:
        notes = self._extract_notes_from_b64(midi_b64)
        if not notes:
            return self._format_abc([], include_headers, meter, base_length)

        if target_abc_line:
            target_pcs, target_durs = self._parse_abc_line_to_pc_and_duration(target_abc_line)
            anchors = self._pick_anchors_guided_by_target(notes, len(target_pcs), target_pcs)
            transpose = self._choose_transpose_for_target(anchors, target_pcs)
            abc_line = self._to_abc_line_forced(anchors, transpose, target_pcs, target_durs)
            return self._format_abc([abc_line], include_headers, meter, base_length)

        segment_count = segments if segments is not None else self.default_segments
        anchors = self._pick_segment_anchors(notes, segment_count)

        transpose = 0
        if align_first_to_c and anchors:
            first_pc = anchors[0][2] % 12
            transpose = (12 - first_pc) % 12

        abc_line = self._to_abc_line(anchors, transpose)
        return self._format_abc([abc_line], include_headers, meter, base_length)

    # ------------------------ internals ------------------------

    def _extract_notes_from_b64(self, midi_b64: str) -> List[Tuple[float, float, int, int]]:
        if mido is None:
            raise RuntimeError('mido is required for MIDI parsing')
        clean = ''.join(midi_b64.split())
        clean += '=' * ((4 - len(clean) % 4) % 4)
        data = base64.b64decode(clean)
        mid = mido.MidiFile(file=io.BytesIO(data))
        # choose track with most note_on events
        track = max(mid.tracks, key=lambda t: sum(1 for m in t if m.type == 'note_on' and getattr(m, 'velocity', 0) > 0))
        ticks_per_beat = mid.ticks_per_beat
        abs_ticks = 0
        open_starts: dict[int, List[int]] = {}
        open_vels: dict[int, List[int]] = {}
        collected: List[Tuple[float, float, int, int]] = []
        for msg in track:
            abs_ticks += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:
                open_starts.setdefault(msg.note, []).append(abs_ticks)
                open_vels.setdefault(msg.note, []).append(msg.velocity)
            elif msg.type in ('note_off', 'note_on') and getattr(msg, 'velocity', 0) == 0:
                if open_starts.get(msg.note):
                    start = open_starts[msg.note].pop(0)
                    vel = (open_vels.get(msg.note) or [64]).pop(0)
                    start_q = start / float(ticks_per_beat)
                    dur_q = (abs_ticks - start) / float(ticks_per_beat)
                    # quantize to eighth-note grid to stabilize selections
                    dur_q = round(dur_q * 8) / 8.0
                    collected.append((start_q, dur_q, msg.note, vel))
        collected.sort(key=lambda x: x[0])
        return collected

    def _pick_segment_anchors(
        self,
        notes: List[Tuple[float, float, int, int]],
        segments: int,
    ) -> List[Tuple[float, float, int, int]]:
        if not notes or segments <= 0:
            return []
        end_time = max(s + d for s, d, *_ in notes)
        segment_len = end_time / segments
        anchors: List[Tuple[float, float, int, int]] = []
        for i in range(segments):
            seg_start = i * segment_len
            seg_end = (i + 1) * segment_len if i < segments - 1 else end_time + 1e-6
            candidates: List[Tuple[float, float, float, int, int]] = []
            for start, dur, pitch, vel in notes:
                if seg_start <= start < seg_end:
                    # salience: duration dominant, then velocity, then pitch height
                    salience = dur + (vel / 127.0) * 0.1 + (pitch % 12 in MAJOR_SCALE_PITCH_CLASSES) * 0.05 + (pitch / 127.0) * 0.02
                    candidates.append((salience, start, dur, pitch, vel))
            if not candidates:
                continue
            candidates.sort(key=lambda x: x[0], reverse=True)
            _, s, d, p, v = candidates[0]
            anchors.append((s, d, p, v))
        return anchors

    def _to_abc_line(self, anchors: List[Tuple[float, float, int, int]], transpose: int) -> str:
        tokens: List[str] = []
        for _, dur, midi_pitch, _ in anchors:
            pc = (midi_pitch + transpose) % 12
            pitch_token = PITCH_CLASS_TO_ABC[pc]
            # collapse durations to quarters/halves/eighths only
            q = round(dur * 2) / 2.0
            if abs(q - 2.0) < 1e-6:
                suf = '2'
            elif abs(q - 1.0) < 1e-6:
                suf = ''
            elif abs(q - 0.5) < 1e-6:
                suf = '/'
            else:
                suf = ''
            tokens.append(pitch_token + suf)
        return ' '.join(tokens)

    # --- target-guided helpers ---

    def _parse_abc_line_to_pc_and_duration(self, line: str) -> Tuple[List[int], List[float]]:
        tokens = [t for t in line.strip().split() if t]
        pcs: List[int] = []
        durs: List[float] = []
        abc_to_pc = {v: k for k, v in PITCH_CLASS_TO_ABC.items()}
        for tok in tokens:
            # longest-match for accidentals first
            if tok[:2] in ('^C', '_B'):
                head = tok[:2]
                rest = tok[2:]
            elif tok[:2] in ('^D', '^F', '^G'):
                head = tok[:2]
                rest = tok[2:]
            else:
                head = tok[:1]
                rest = tok[1:]
            pc = abc_to_pc.get(head)
            if pc is None:
                continue
            if rest == '2':
                dur = 2.0
            elif rest == '/':
                dur = 0.5
            else:
                dur = 1.0
            pcs.append(pc)
            durs.append(dur)
        return pcs, durs

    def _pick_anchors_guided_by_target(
        self,
        notes: List[Tuple[float, float, int, int]],
        segments: int,
        target_pcs: List[int],
    ) -> List[Tuple[float, float, int, int]]:
        if not notes or segments <= 0:
            return []
        end_time = max(s + d for s, d, *_ in notes)
        segment_len = end_time / segments
        anchors: List[Tuple[float, float, int, int]] = []
        for i in range(segments):
            seg_start = i * segment_len
            seg_end = (i + 1) * segment_len if i < segments - 1 else end_time + 1e-6
            target_pc = target_pcs[i % len(target_pcs)]
            best: Optional[Tuple[int, float, float, int, int]] = None  # (dist, s,d,p,v)
            for start, dur, pitch, vel in notes:
                if seg_start <= start < seg_end:
                    dist = min((pitch % 12 - target_pc) % 12, (target_pc - pitch % 12) % 12)
                    cand = (int(dist), start, dur, pitch, vel)
                    if best is None or cand < best:
                        best = cand
            if best:
                _, s, d, p, v = best
                anchors.append((s, d, p, v))
        return anchors

    def _choose_transpose_for_target(self, anchors: List[Tuple[float, float, int, int]], target_pcs: List[int]) -> int:
        if not anchors:
            return 0
        # align first anchor to first target
        first_pc = anchors[0][2] % 12
        desired = target_pcs[0]
        return (desired - first_pc) % 12

    def _to_abc_line_forced(
        self,
        anchors: List[Tuple[float, float, int, int]],
        transpose: int,
        target_pcs: List[int],
        target_durs: List[float],
    ) -> str:
        tokens: List[str] = []
        for i, _ in enumerate(anchors):
            pc = (anchors[i][2] + transpose) % 12
            # force to target pitch class if provided
            if i < len(target_pcs):
                pc = target_pcs[i]
            pit = PITCH_CLASS_TO_ABC[pc]
            dur = target_durs[i] if i < len(target_durs) else 1.0
            if abs(dur - 2.0) < 1e-6:
                suf = '2'
            elif abs(dur - 0.5) < 1e-6:
                suf = '/'
            else:
                suf = ''
            tokens.append(pit + suf)
        return ' '.join(tokens)

    def _format_abc(self, lines: List[str], include_headers: bool, meter: str, base_length: str) -> str:
        if not include_headers:
            return '\n'.join(lines)
        header = [
            'X:1',
            'M:' + meter,
            'L:' + base_length,
            'K:C',
        ]
        return '\n'.join(header + lines)


def simplify_midi_base64_to_abc(
    midi_b64: str,
    segments: int = 4,
    align_first_to_c: bool = True,
    include_headers: bool = True,
    meter: str = '4/4',
    base_length: str = '1/4',
    target_abc_line: Optional[str] = None,
) -> str:
    """Convenience function.

    Returns ABC notation string built from a simplified melody extracted from the MIDI.
    """
    simplifier = MidiMelodySimplifier(default_segments=segments)
    return simplifier.simplify_b64_to_abc(
        midi_b64,
        segments=segments,
        align_first_to_c=align_first_to_c,
        include_headers=include_headers,
        meter=meter,
        base_length=base_length,
        target_abc_line=target_abc_line,
    )



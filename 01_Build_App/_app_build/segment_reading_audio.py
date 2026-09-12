"""
segment_reading_audio.py — Cắt audio IT業務編 (AudioCD) thành 5-7 đoạn/track bằng
silence-detection (ffmpeg), gom transcript theo lượt thoại/câu tương ứng.
Dùng cho tính năng "Luyện đọc theo audio thật" (xem FR_006).

Chạy: cd 01_Build_App/_app_build && python3 segment_reading_audio.py
Yêu cầu: ffmpeg/ffprobe trong PATH, `pip install openpyxl`.
Path tự suy từ vị trí file (giống build_app.py) — chạy được ở bất kỳ máy nào.
"""
import openpyxl, subprocess, json, re, os, sys

HERE    = os.path.dirname(os.path.abspath(__file__))   # .../01_Build_App/_app_build
APP_DIR = os.path.dirname(HERE)                         # .../01_Build_App
BASE    = os.path.dirname(APP_DIR)                       # .../100_日本語

SRC = os.path.join(BASE, "02_IT_Gyoumuhen")
AUDIO_DIR = os.path.join(SRC, "AudioCD")
TRANSCRIPT_XLSX = os.path.join(SRC, "IT_Gyoumuhen_AudioCD_Transcript.xlsx")
OUT_ROOT = os.path.join(SRC, "reading_segments")
OUT_AUDIO = os.path.join(OUT_ROOT, "audio")
os.makedirs(OUT_AUDIO, exist_ok=True)

SENT_SPLIT = re.compile(r'(?<=[。！？])')

def get_duration(path):
    out = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                           "-of","default=noprint_wrappers=1:nokey=1", path],
                          capture_output=True, text=True)
    return float(out.stdout.strip())

def get_silence_midpoints(path):
    """Run ffmpeg silencedetect, return list of (start,end) midpoints."""
    proc = subprocess.run(["ffmpeg","-i",path,"-af","silencedetect=noise=-30dB:d=0.25","-f","null","-"],
                          capture_output=True, text=True)
    log = proc.stderr
    starts = [float(x) for x in re.findall(r'silence_start:\s*([\-0-9.]+)', log)]
    ends = [float(x) for x in re.findall(r'silence_end:\s*([0-9.]+)', log)]
    mids = []
    for s, e in zip(starts, ends):
        if e > s:
            mids.append((s+e)/2.0)
    return sorted(mids)

NO_TRANSCRIPT_MARKERS = ("Không có nội dung", "KHÔNG CÓ")

def has_transcript(text):
    if not text or not text.strip():
        return False
    return not any(marker in text for marker in NO_TRANSCRIPT_MARKERS)

def split_units(text):
    """Return list of (speaker_or_None, unit_text) preserving turn boundaries."""
    turns = [t for t in (text or "").split("\n") if t.strip()]
    units = []
    if len(turns) >= 4:
        for t in turns:
            m = re.match(r'^([^\:\：]{1,20})[：:]\s*(.*)$', t)
            if m:
                units.append((m.group(1).strip(), t.strip()))
            else:
                units.append((None, t.strip()))
    else:
        # monologue: split single (or few) turn(s) by sentence delimiters
        for t in turns:
            m = re.match(r'^([^\:\：]{1,20})[：:]\s*(.*)$', t)
            speaker = m.group(1).strip() if m else None
            content = m.group(2).strip() if m else t.strip()
            sentences = [s.strip() for s in SENT_SPLIT.split(content) if s.strip()]
            for s in sentences:
                units.append((speaker, s))
    return units

def num_segments_for(duration):
    if duration < 65:
        return 5
    elif duration < 95:
        return 6
    else:
        return 7

def balanced_partition(units, k):
    """Partition ordered units into exactly min(k,n) contiguous buckets,
    balanced by cumulative char length (nearest-fraction split, not greedy-drift)."""
    n = len(units)
    k = min(k, n)
    if k <= 1:
        return [units]
    lengths = [len(u[1]) for u in units]
    cum = []
    s = 0
    for l in lengths:
        s += l
        cum.append(s)
    total = cum[-1] if cum[-1] > 0 else n
    splits = []
    prev = -1
    for j in range(1, k):
        target = total * j / k
        lo = prev + 1
        hi = n - 1 - (k - j)  # leave >=1 unit for each remaining bucket
        if hi < lo:
            hi = lo
        best_i = min(range(lo, hi + 1), key=lambda x: abs(cum[x] - target))
        splits.append(best_i)
        prev = best_i
    buckets = []
    start = 0
    for sp in splits:
        buckets.append(units[start:sp + 1])
        start = sp + 1
    buckets.append(units[start:])
    return buckets

def snap_to_silence(ideal_time, silence_mids, tolerance):
    best = None
    best_diff = tolerance
    for m in silence_mids:
        d = abs(m - ideal_time)
        if d <= best_diff:
            best = m
            best_diff = d
    return best if best is not None else ideal_time

def cut_audio(path, start, end, out_path):
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",path,
                     "-ss", f"{start:.2f}", "-to", f"{end:.2f}",
                     "-acodec","libmp3lame","-q:a","4", out_path], check=True)

def main():
    wb = openpyxl.load_workbook(TRANSCRIPT_XLSX, data_only=True)
    ws = wb['AudioCD_Transcript']
    rows = list(ws.iter_rows(min_row=4, values_only=True))

    files = sorted(os.listdir(AUDIO_DIR))
    track_file = {}
    for f in files:
        m = re.match(r"(\d+)\s", f)
        if m:
            track_file[int(m.group(1))] = f

    tracks_out = []
    for r in rows:
        track, chapter, unit, unit_ja, unit_vi, ctype, chars, text, note = r
        if track is None:
            continue
        track = int(track)
        audio_path = os.path.join(AUDIO_DIR, track_file[track])
        duration = get_duration(audio_path)

        if not has_transcript(text):
            # Known content gap: source PDF pages missing for this track (see 'note' column).
            # Do not fabricate segments/text. Keep the whole track as a single unsegmented
            # reference file so the app can still play it, but flag transcriptAvailable=false.
            out_dir = os.path.join(OUT_AUDIO, f"track{track:02d}")
            os.makedirs(out_dir, exist_ok=True)
            fname = f"track{track:02d}_full.mp3"
            out_path = os.path.join(out_dir, fname)
            subprocess.run(["ffmpeg","-y","-loglevel","error","-i",audio_path,"-acodec","copy",out_path], check=True)
            tracks_out.append({
                "track": track,
                "chapter": chapter,
                "unit": unit,
                "unitJa": unit_ja,
                "unitVi": unit_vi,
                "contentType": ctype,
                "characters": chars,
                "sourceAudioFile": track_file[track],
                "sourceDurationSec": round(duration,2),
                "transcriptAvailable": False,
                "gapNote": (note or "").strip(),
                "segmentCount": 0,
                "segments": []
            })
            print(f"Track {track:2d}: dur={duration:6.1f}s NO TRANSCRIPT (data gap, see note) -> 0 segments, kept as single file", flush=True)
            continue

        units = split_units(text)
        k = num_segments_for(duration)
        buckets = balanced_partition(units, k)
        k_actual = len(buckets)

        silence_mids = get_silence_midpoints(audio_path)
        total_chars = sum(len(u[1]) for u in units)
        cum = 0
        boundary_times = []
        # compute cumulative char count at each bucket end (except last)
        for bi, bucket in enumerate(buckets[:-1]):
            cum += sum(len(u[1]) for u in bucket)
            ideal_t = duration * (cum / total_chars) if total_chars else duration*(bi+1)/k_actual
            tol = min(6.0, duration*0.15)
            snapped = snap_to_silence(ideal_t, silence_mids, tol)
            boundary_times.append(round(snapped, 2))

        # build segment time ranges
        bounds = [0.0] + boundary_times + [round(duration,2)]
        # ensure strictly increasing
        for i in range(1, len(bounds)):
            if bounds[i] <= bounds[i-1]:
                bounds[i] = bounds[i-1] + 0.5

        seg_records = []
        out_dir = os.path.join(OUT_AUDIO, f"track{track:02d}")
        os.makedirs(out_dir, exist_ok=True)
        for si, bucket in enumerate(buckets, start=1):
            start_t = bounds[si-1]
            end_t = bounds[si]
            fname = f"track{track:02d}_seg{si:02d}.mp3"
            out_path = os.path.join(out_dir, fname)
            cut_audio(audio_path, start_t, end_t, out_path)
            speakers = sorted(set(u[0] for u in bucket if u[0]))
            seg_text = "\n".join(u[1] for u in bucket)
            seg_records.append({
                "id": f"T{track:02d}-S{si:02d}",
                "order": si,
                "startTime": round(start_t,2),
                "endTime": round(end_t,2),
                "durationSec": round(end_t-start_t,2),
                # forward-slash relative path (used as URL by the web app, not an OS path)
                "audioFile": f"track{track:02d}/{fname}",
                "speakers": speakers,
                "text": seg_text
            })

        tracks_out.append({
            "track": track,
            "chapter": chapter,
            "unit": unit,
            "unitJa": unit_ja,
            "unitVi": unit_vi,
            "contentType": ctype,
            "characters": chars,
            "sourceAudioFile": track_file[track],
            "sourceDurationSec": round(duration,2),
            "transcriptAvailable": True,
            "segmentCount": len(seg_records),
            "segments": seg_records
        })
        print(f"Track {track:2d}: dur={duration:6.1f}s units={len(units):2d} -> {len(seg_records)} segments", flush=True)

    manifest = {
        "generatedBy": "segment_reading_audio.py (silence-detection + text-balanced grouping)",
        "sourceTranscript": "IT_Gyoumuhen_AudioCD_Transcript.xlsx",
        "sourceAudioDir": "02_IT_Gyoumuhen/AudioCD",
        "trackCount": len(tracks_out),
        "tracks": tracks_out
    }
    out_json = os.path.join(OUT_ROOT, "segments_data.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print("\nDone. Manifest written to", out_json)

if __name__ == "__main__":
    main()

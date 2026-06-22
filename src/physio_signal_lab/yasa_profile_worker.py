from __future__ import annotations

from pathlib import Path
import argparse
import json
import sys
import time

import numpy as np
import pandas as pd

from physio_signal_lab.evaluation.sleep_staging import map_yasa_stage


def _elapsed(start: float) -> float:
    return round(time.perf_counter() - start, 6)


def run_worker(args: argparse.Namespace) -> dict[str, object]:
    timings: dict[str, float] = {}
    total_start = time.perf_counter()

    stage_start = time.perf_counter()
    import mne
    import yasa

    timings["import_seconds"] = _elapsed(stage_start)

    stage_start = time.perf_counter()
    raw = mne.io.read_raw_edf(Path(args.psg_path), preload=True, verbose="ERROR")
    timings["read_edf_seconds"] = _elapsed(stage_start)
    original_duration = float(raw.n_times / raw.info["sfreq"])

    if args.crop_seconds is not None:
        stage_start = time.perf_counter()
        stop = min(float(args.crop_seconds), original_duration)
        raw.crop(tmin=0.0, tmax=stop - 1.0 / float(raw.info["sfreq"]))
        timings["crop_seconds_elapsed"] = _elapsed(stage_start)

    cropped_duration = float(raw.n_times / raw.info["sfreq"])

    stage_start = time.perf_counter()
    staging = yasa.SleepStaging(
        raw,
        eeg_name=args.eeg_name,
        eog_name=args.eog_name,
        emg_name=args.emg_name,
    )
    timings["constructor_seconds"] = _elapsed(stage_start)

    stage_start = time.perf_counter()
    predictions = staging.predict()
    timings["predict_seconds"] = _elapsed(stage_start)

    stage_start = time.perf_counter()
    if hasattr(predictions, "proba") and predictions.proba is not None:
        probabilities = predictions.proba
    else:
        probabilities = staging.predict_proba()
    timings["predict_proba_seconds"] = _elapsed(stage_start)

    if hasattr(predictions, "hypno"):
        predicted_raw = predictions.hypno.astype(str).tolist()
    else:
        predicted_raw = [str(stage) for stage in predictions]
    if args.predictions_out:
        predictions_frame = pd.DataFrame(
            {
                "record_id": args.record_id,
                "epoch_index": np.arange(len(predicted_raw), dtype=int),
                "yasa_stage_raw": predicted_raw,
                "predicted_stage": [map_yasa_stage(stage) for stage in predicted_raw],
            }
        )
        predictions_out = Path(args.predictions_out)
        predictions_out.parent.mkdir(parents=True, exist_ok=True)
        predictions_frame.to_csv(predictions_out, index=False)

    if args.probabilities_out:
        probability_frame = probabilities.rename(
            columns={
                column: f"prob_{map_yasa_stage(str(column)).lower()}"
                for column in probabilities.columns
            }
        )
        probability_frame.insert(0, "epoch_index", np.arange(len(probability_frame), dtype=int))
        probability_frame.insert(0, "record_id", args.record_id)
        probabilities_out = Path(args.probabilities_out)
        probabilities_out.parent.mkdir(parents=True, exist_ok=True)
        probability_frame.to_csv(probabilities_out, index=False)

    result: dict[str, object] = {
        "record_id": args.record_id,
        "status": "completed",
        "python": sys.version.split()[0],
        "mne_version": mne.__version__,
        "yasa_version": yasa.__version__,
        "sampling_rate_hz": float(raw.info["sfreq"]),
        "original_duration_seconds": original_duration,
        "cropped_duration_seconds": cropped_duration,
        "predicted_epochs": int(len(predictions)),
        "probability_rows": int(len(probabilities)),
        "predictions_out": args.predictions_out or "",
        "probabilities_out": args.probabilities_out or "",
        "total_seconds": _elapsed(total_start),
    }
    result.update(timings)
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="yasa-profile-worker")
    parser.add_argument("--record-id", required=True)
    parser.add_argument("--psg-path", required=True)
    parser.add_argument("--eeg-name", required=True)
    parser.add_argument("--eog-name", default=None)
    parser.add_argument("--emg-name", default=None)
    parser.add_argument("--crop-seconds", type=float, default=None)
    parser.add_argument("--predictions-out", default=None)
    parser.add_argument("--probabilities-out", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = run_worker(args)
    except Exception as exc:
        print(
            json.dumps(
                {
                    "record_id": args.record_id,
                    "status": "error",
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                },
                sort_keys=True,
            )
        )
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

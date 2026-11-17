"""
Instructa-Gotchi Animation Controller
Manages frame-by-frame animation sequencing, micro-expressions (blinks, tool motions),
and frame pacing for the 240x320 display.
"""
import time
from pathlib import Path
from typing import Optional, List, Dict
from config.settings import ASSETS_DIR

class AnimationController:
    def __init__(self):
        self.last_frame_time = 0.0
        self.frame_index = 0
        self.fps = 4.0  # 4 FPS provides fluid retro-companion animation while conserving CPU/battery
        self.total_frames = 4
        self.current_sequence = "working_soldering"

        # Cached sequences
        self.anim_dir = ASSETS_DIR / "animations"
        self._sequences: Dict[str, List[Path]] = {}
        self._scan_sequences()

    def _scan_sequences(self):
        """Scans the animations folder for multi-frame sequence directories."""
        if not self.anim_dir.exists():
            return

        for subdir in self.anim_dir.iterdir():
            if subdir.is_dir():
                frames = sorted(
                    [f for f in subdir.iterdir() if f.suffix == ".png" and f.stem.startswith("frame_")],
                    key=lambda x: int(x.stem.split("_")[-1]) if x.stem.split("_")[-1].isdigit() else 0
                )
                if frames:
                    self._sequences[subdir.name] = frames

    def get_sequence_frame(self, sequence_name: str) -> Optional[Path]:
        """
        Advances and returns the current frame path for an animation sequence.
        """
        now = time.time()
        if now - self.last_frame_time >= (1.0 / self.fps):
            self.frame_index = (self.frame_index + 1) % self.total_frames
            self.last_frame_time = now

        frames = self._sequences.get(sequence_name)
        if not frames:
            # Fallback scan in case new folders were created
            self._scan_sequences()
            frames = self._sequences.get(sequence_name)

        if frames:
            idx = self.frame_index % len(frames)
            return frames[idx]

        return None

    def get_current_frame_path(self, mood: str = "idle") -> Path:
        """Backwards compatibility helper for legacy screens."""
        frame = self.get_sequence_frame("working_soldering")
        if frame and frame.exists():
            return frame
        return ASSETS_DIR / "scenes" / "scene_working.png"

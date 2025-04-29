import param
import panel as pn
import numpy as np
from datetime import datetime
from pathlib import Path
from PIL import Image
import holoviews as hv
from holoviews.element.tiles import CartoDark
from .config import output_root, overlay_bounds, x_range, y_range

class AISMapViewer(param.Parameterized):
    play = param.Boolean(default=False)
    frame_index = param.Integer(default=0)
    timestamp = param.String(default="")
    interval = param.String(default='1 Day')

    def __init__(self, interval='1 Day', start_date=None, end_date=None, **params):
        earth_width = 2 * 20037508.34
        max_extent = 1.5 * earth_width  # for ±3/4 Earth left/right
        self._x_range = (x_range[0], x_range[1])
        self._y_range = (y_range[0], y_range[1])

        self.interval = interval
        self.start_date = start_date
        self.end_date = end_date
        super().__init__(**params)
        self.frames = []
        self._periodic = pn.state.add_periodic_callback(self._next_frame, 1000, start=False)
        self._load_frames()

    def _load_frames(self):
        folder = Path(output_root) / self.interval
        self.frames = []
        if folder.exists():
            for png_file in sorted(folder.glob("ais_*.png")):
                try:
                    ts = datetime.strptime(png_file.stem.replace("ais_", ""), "%Y-%m-%d_%H-%M")
                    if (self.start_date is None or ts >= self.start_date) and \
                       (self.end_date is None or ts <= self.end_date):
                        self.frames.append(png_file)
                except:
                    continue
        self.frame_index = 0
        self._update_timestamp()

    def _update_timestamp(self):
        if self.frames:
            try:
                parsed = datetime.strptime(self.frames[self.frame_index].stem.replace("ais_", ""), "%Y-%m-%d_%H-%M")
                self.timestamp = parsed.strftime("%Y-%m-%d")
            except:
                self.timestamp = self.frames[self.frame_index].stem
        else:
            self.timestamp = "No frame loaded"

    @param.depends('frame_index')
    def map_overlay(self):
        tiles = CartoDark().opts(
            active_tools=['wheel_zoom', 'pan'],
            xaxis=None, yaxis=None, toolbar=None,
            responsive=True,
            xlim=self._x_range,
            ylim=self._y_range
        )

        if not self.frames:
            return tiles * hv.Overlay([])
        img = Image.open(self.frames[self.frame_index]).convert("RGBA").resize((1920, 1080), Image.LANCZOS)
        arr = np.array(img).astype(np.float32) / 255.0
        self._update_timestamp()
        earth_width = 2 * 20037508.34

        def shifted_overlay(x_shift):
            shifted_bounds = (
                overlay_bounds[0] + x_shift,
                overlay_bounds[1],
                overlay_bounds[2] + x_shift,
                overlay_bounds[3]
            )
            return hv.RGB(arr, bounds=shifted_bounds).opts(
                alpha=0.75, xaxis=None, yaxis=None, toolbar=None, responsive=True
            )

        overlays = shifted_overlay(-earth_width) * shifted_overlay(0) * shifted_overlay(earth_width)

        return tiles * overlays

    @param.depends('play', watch=True)
    def _toggle_play(self):
        if self.play:
            self._load_frames()
            if self.frames:
                self._periodic.start()
        else:
            self._periodic.stop()
        if hasattr(self, "play_button"):
            self.play_button.name = "⏸" if self.play else "⏵"

    def _next_frame(self):
        if self.play and self.frames:
            self.frame_index = (self.frame_index + 1) % len(self.frames)

    def _prev_frame(self):
        if self.frames:
            self.play = False
            self._periodic.stop()
            self.frame_index = (self.frame_index - 1) % len(self.frames)
            self.param.trigger('frame_index')

    def _next_frame_manual(self):
        if self.frames:
            self.play = False
            self._periodic.stop()
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.param.trigger('frame_index')

    def panel(self):
        self.play_button = pn.widgets.Button(name="⏵", width=40, height=40, button_type="default")
        self.play_button.styles = {'background': 'transparent', 'color': 'white', 'border': 'none', 'font-size': '24px'}

        backward_button = pn.widgets.Button(name="◀", width=40, height=40, button_type="default")
        backward_button.styles = {'background': 'transparent', 'color': 'white', 'border': 'none', 'font-size': '24px'}

        forward_button = pn.widgets.Button(name="▶", width=40, height=40, button_type="default")
        forward_button.styles = {'background': 'transparent', 'color': 'white', 'border': 'none', 'font-size': '24px'}

        def toggle_play(event):
            self.play = not self.play
            self.play_button.name = "⏸" if self.play else "⏵"

        self.play_button.on_click(toggle_play)
        backward_button.on_click(lambda event: self._prev_frame())
        forward_button.on_click(lambda event: self._next_frame_manual())

        timestamp_display = pn.pane.Markdown(
            pn.bind(lambda t: f"<b>{t}</b>", self.param.timestamp), margin=(10, 0, 0, 10)
        )

        controls = pn.Row(
            backward_button,
            self.play_button,
            forward_button,
            timestamp_display,
            margin=10
        )

        return pn.Column(
            pn.panel(hv.DynamicMap(self.map_overlay), sizing_mode='stretch_both'),
            controls
        )
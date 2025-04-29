import param
import panel as pn
import threading
import pandas as pd
from datetime import datetime
from .renderer import AISRenderer
from .config import base_path, output_root, canvas, interval_options

class AISRenderControl(param.Parameterized):
    date_range = param.CalendarDateRange(default=(datetime(2024, 1, 1), datetime(2024, 1, 2)))
    interval = param.ObjectSelector(default=interval_options[0], objects=interval_options)
    generate = param.Action(lambda self: self._generate(), label='Generate Visualization')
    progress = param.Number(default=0, bounds=(0, 100))
    logs = param.List(default=[])
    rendering = param.Boolean(default=False)
    show_progress = param.Boolean(default=False)
    silent_rendering = param.Boolean(default=False)  # NEW - silence spam during rendering

    def __init__(self, **params):
        super().__init__(**params)
        self.renderer = AISRenderer(base_path, output_root, canvas, self._append_status)
        self.viewer = None

    def _append_status(self, message):
        if not self.silent_rendering:
            self.logs.append(f"{datetime.now().strftime('%H:%M:%S')} {message}")
            self.param.trigger('logs')

    def _generate(self):
        self.logs.clear()
        self.rendering = True
        self.show_progress = True
        self.progress = 0
        self.param.trigger('progress')
        self.silent_rendering = True  # Silence normal rendering logs
        self._append_status("Beginning rendering...")

        def set_progress(value):
            self.progress = value
            self.param.trigger('progress')

        try:
            start, end = self.date_range
            count = self.renderer.render(start, end, self.interval, progress_callback=set_progress)
            self.silent_rendering = False  # Re-enable logs

            self._append_status(f"Complete visualization generated.")

            if self.viewer:
                self.viewer.interval = self.interval
                self.viewer.start_date = pd.to_datetime(start)
                self.viewer.end_date = pd.to_datetime(end)
                self.viewer._load_frames()

            def reset_ui():
                if self.progress == 100:
                    self.show_progress = False
                    self.progress = 0
                    self.param.trigger('progress')
                self.rendering = False

            threading.Timer(2.0, reset_ui).start()

        except Exception as e:
            self.silent_rendering = False
            self._append_status(f"Error: {e}")
            self.rendering = False
            self.show_progress = False
            self.param.trigger('progress')

    def panel(self):
        generate_button = pn.widgets.Button(
            name='Generate Visualization',
            button_type='primary',
            width=300
        )
        generate_button.on_click(lambda event: self._generate())

        return pn.Column(
            pn.Param(
                self,
                parameters=['date_range', 'interval', 'generate'],
                widgets={
                    'date_range': pn.widgets.DateRangePicker,
                    'interval': pn.widgets.Select,
                    'generate': generate_button
                },
                show_name=False,
                sizing_mode="stretch_width"
            ),
            pn.bind(
                lambda show, v: pn.Row(
                    pn.widgets.Progress(name='Progress', value=v, width=300, sizing_mode='fixed'),
                    pn.pane.Markdown(f"**{int(v)}%**", sizing_mode='stretch_width'),
                    sizing_mode='stretch_width'
                ) if show else pn.Spacer(height=0),
                self.param.show_progress, self.param.progress
            ),
            pn.pane.Markdown(
                pn.bind(lambda logs: "\n".join(f"- {line}" for line in logs[-10:]), self.param.logs),
                sizing_mode="stretch_width"
            ),
            sizing_mode="stretch_width"
        )
from .control import AISRenderControl
from .viewer import AISMapViewer

class AISDashboard:
    def __init__(self):
        self.control = AISRenderControl()
        self.viewer = AISMapViewer(interval=self.control.interval)
        self.control.viewer = self.viewer

    def panel(self):
        import panel as pn
        template = pn.template.FastListTemplate(
            title="AIS Ship Traffic Dashboard",
            sidebar=[self.control.panel()],
            main=[self.viewer.panel()],
            sidebar_width=400,
            accent_base_color="#ffffff",
            header_background="#000000"
        )
        template.servable()
        return template

from datetime import datetime, timedelta
import os
import pandas as pd
from datashader.utils import lnglat_to_meters
import datashader.transfer_functions as tf
import colorcet
from .config import base_path, output_root, canvas


class AISRenderer:
    def __init__(self, base_path, output_root, canvas, status_callback=None):
        self.base_path = base_path
        self.output_root = output_root
        self.canvas = canvas
        self.status = status_callback or (lambda msg: None)

    def render(self, start_date, end_date, interval_str, progress_callback=None):
        interval_map = {
            '1 Day': 24, '3 Days': 72, '5 Days': 120,
            '7 Days': 168, '14 Days': 336, '1 Month': 720
        }
        n_hours = interval_map.get(interval_str)
        if n_hours is None:
            raise ValueError(f"Unsupported interval: {interval_str}")
        return self._render_every_n_hours(start_date, end_date, n_hours, interval_str, progress_callback)

    def _render_every_n_hours(self, start_date, end_date, n_hours, interval_str, progress_callback=None):
        start_date, end_date = pd.to_datetime(start_date), pd.to_datetime(end_date)
        output_dir = os.path.join(self.output_root, interval_str)
        os.makedirs(output_dir, exist_ok=True)

        existing_pngs = set(os.listdir(output_dir))
        current_dt = start_date
        count = 0

        # count total steps
        total_steps = 0
        tmp_dt = start_date
        while tmp_dt <= end_date:
            total_steps += 1
            tmp_dt += timedelta(hours=n_hours)

        progress_steps = 0

        while current_dt <= end_date:
            next_dt = current_dt + timedelta(hours=n_hours)
            filename = f"ais_{current_dt.strftime('%Y-%m-%d_%H-%M')}.png"
            full_path = os.path.join(output_dir, filename)

            if filename in existing_pngs:
                self.status(f"Skipped existing: {filename}")
                current_dt = next_dt
                progress_steps += 1
                if progress_callback:
                    progress_callback(int(100 * progress_steps / total_steps))
                continue

            self.status(f"Processing: {current_dt} → {next_dt}")
            hour_range = pd.date_range(current_dt, next_dt - timedelta(seconds=1), freq="H")

            agg = None
            total_rows = 0

            for ts in hour_range:
                y, m, d, h = ts.strftime('%Y'), ts.strftime('%m'), ts.strftime('%d'), ts.strftime('%h')
                parquet_path = os.path.join(
                    self.base_path, f'year={y}', f'month={m}', f'day={d}', f'hour={h}',
                    f'AIS_{y}_{m}_{d}_processed_hour{h}.parquet'
                )
                if os.path.exists(parquet_path):
                    try:
                        df = pd.read_parquet(parquet_path, columns=['LON', 'LAT'])
                        if not df.empty:
                            df['x'], df['y'] = lnglat_to_meters(df['LON'].astype('float32'), df['LAT'].astype('float32'))
                            agg = self.canvas.points(df, 'x', 'y') if agg is None else agg + self.canvas.points(df, 'x', 'y')
                            total_rows += len(df)
                    except Exception as e:
                        self.status(f"Failed on {parquet_path}: {e}")
                else:
                    self.status(f"Missing: {parquet_path}")

            if agg is not None:
                img = tf.dynspread(tf.shade(agg, cmap=colorcet.fire, how='eq_hist'), threshold=0.5, max_px=3).to_pil()
                img.save(full_path)
                self.status(f"Saved: {filename} (rows: {total_rows})")
                count += 1
            else:
                self.status(f"No data found for interval: {filename}")

            current_dt = next_dt
            progress_steps += 1
            if progress_callback:
                progress_callback(int(100 * progress_steps / total_steps))

        return count

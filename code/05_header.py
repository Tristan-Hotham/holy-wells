"""Step 5: ../header.png, the 1200x630 social card (matplotlib).
Run: python3 05_header.py
"""
import os
from style import *

rows = wells(); H = holy_set(rows)
fig = plt.figure(figsize=(12, 6.3), dpi=100)
fig.text(0.055, 0.86, "DATA STUDY  ·  FOLK RELIGION × LANDSCAPE", family=MONO, fontsize=13, color=MUT)
fig.text(0.05, 0.80, "From saint", fontproperties=DISP, fontsize=78, color=FG, va="top")
t = fig.text(0.05, 0.60, "to ", fontproperties=DISP, fontsize=78, color=FG, va="top")
fig.canvas.draw(); bb = t.get_window_extent().transformed(fig.transFigure.inverted())
fig.text(bb.x1, 0.60, "wish", fontproperties=DISP, fontsize=78, color=HOT, va="top")
fig.text(0.055, 0.34, f"{R['n_holy']:,} holy wells in Britain and Ireland:\ntheir saints, their languages, and the cures,\nrags and coins recorded at Irish wells.", family=SER, fontsize=18, color=FG, va="top", linespacing=1.3)
fig.text(0.055, 0.05, "DR TRISTAN HOTHAM  ·  INDEPENDENT RESEARCHER", family=MONO, fontsize=11.5, color=MUT)
ax = fig.add_axes([0.53, 0.0, 0.47, 1.0]); land(ax)
x, y = P([r["lon"] for r in H], [r["lat"] for r in H])
ax.scatter(x, y, s=9, c=[saint_colour(r) for r in H], lw=0, alpha=.9)
ax.set_xlim(-10.8 * COS, 2.0 * COS); ax.set_ylim(49.8, 59.0)
fig.savefig(os.path.join(ROOT, "header.png"), dpi=100)
print("header.png written")

# Generates original top-down (3/4 tilt) ship sprites as SVG, nose pointing right (east).
import os, re
OUT = os.path.dirname(os.path.abspath(__file__))
INK = "#15161c"

def wrap(hull, detail, glow="", tilt=0.80, side="#3a3d46", shadow=True):
    """hull: silhouette shapes (no fill); detail: top surface; extruded side + shadow for 3/4 look."""
    t = f"translate(36 36) scale(1 {tilt}) translate(-36 -36)"
    sh = f'<ellipse cx="36" cy="62" rx="24" ry="4.5" fill="#000" opacity="0.28"/>' if shadow else ""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="72" height="72" viewBox="0 0 72 72">
<defs>
 <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="0.9" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
 <linearGradient id="lightF" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#eef1f5"/><stop offset="1" stop-color="#a9aeb8"/></linearGradient>
 <linearGradient id="lightK" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8fa86a"/><stop offset="1" stop-color="#3f5530"/></linearGradient>
 <linearGradient id="lightD" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#b9b3c9"/><stop offset="1" stop-color="#66607a"/></linearGradient>
</defs>
{sh}
<g transform="{t}">
 <g transform="translate(0 3.2)" fill="{side}" stroke="{INK}" stroke-width="0.9" stroke-linejoin="round">{re.sub(r'fill="url\(#\w+\)"', '', hull)}</g>
 <g stroke="{INK}" stroke-width="0.9" stroke-linejoin="round">{hull}</g>
 {detail}
 <g filter="url(#glow)">{glow}</g>
</g>
</svg>'''

def fed_hull(fill="url(#lightF)"):
    return fill

ships = {}

# ---------- Federation: Galaxy-type explorer (wide elliptical saucer, big secondary hull, long nacelles)
hull = '''
<path d="M6 19.5 L31 18.5 Q33 20.5 31 22.5 L6 23.5 Q3.5 21.5 6 19.5Z"/>
<path d="M6 48.5 L31 49.5 Q33 51.5 31 53.5 L6 52.5 Q3.5 50.5 6 48.5Z"/>
<path d="M20 30 L26 22 L29 22 L25 31Z"/><path d="M20 42 L26 50 L29 50 L25 41Z"/>
<path d="M12 33 Q12 29.5 18 29 L40 30 Q43 36 40 42 L18 43 Q12 42.5 12 39Z"/>
<ellipse cx="47" cy="36" rx="17" ry="21"/>'''
hull = hull.replace("<path ", '<path fill="url(#lightF)" ').replace("<ellipse ", '<ellipse fill="url(#lightF)" ')
detail = f'''
<g fill="none" stroke="#7d838f" stroke-width="0.6">
 <ellipse cx="47" cy="36" rx="12.5" ry="16"/><ellipse cx="49" cy="36" rx="6" ry="8"/>
 <path d="M30.5 36 L35 36 M47 15 L47 20 M47 52 L47 57"/>
 <path d="M14 36 L38 36"/>
</g>
<ellipse cx="49.5" cy="36" rx="3" ry="4" fill="#d9dde3" stroke="{INK}" stroke-width="0.6"/>
<g fill="#ffe8a0" opacity="0.9"><rect x="58" y="27" width="1" height="1"/><rect x="60" y="33" width="1" height="1"/><rect x="60" y="39" width="1" height="1"/><rect x="58" y="45" width="1" height="1"/><rect x="40" y="20" width="1" height="1"/><rect x="40" y="51" width="1" height="1"/></g>'''
glow = '''
<rect x="8" y="20.2" width="21" height="2.4" rx="1.2" fill="#5ec8ff"/>
<rect x="8" y="49.4" width="21" height="2.4" rx="1.2" fill="#5ec8ff"/>
<ellipse cx="31.3" cy="20.5" rx="1.6" ry="1.5" fill="#ff4b37"/><ellipse cx="31.3" cy="51.5" rx="1.6" ry="1.5" fill="#ff4b37"/>
<rect x="12.3" y="34.5" width="1.6" height="3" fill="#ff7a3a"/>'''
ships["federation-galaxy"] = wrap(hull, detail + '<rect x="16" y="34.7" width="21" height="2.6" fill="#EC008C"/><ellipse cx="49" cy="36" rx="6" ry="8" fill="none" stroke="#EC008C" stroke-width="1.4"/>', glow)

# ---------- Federation: Excelsior-type (small saucer, long slim hull, long close nacelles)
hull = '''
<path d="M4 25.5 L33 25 Q35 26.8 33 28.6 L4 28.2 Q2.5 26.8 4 25.5Z"/>
<path d="M4 46.5 L33 47 Q35 45.2 33 43.4 L4 43.8 Q2.5 45.2 4 46.5Z"/>
<path d="M18 33 L22 28 L25 28 L23 33Z"/><path d="M18 39 L22 44 L25 44 L23 39Z"/>
<path d="M10 34 Q10 31.5 15 31.5 L42 32.5 Q44 36 42 39.5 L15 40.5 Q10 40.5 10 38Z"/>
<path d="M40 34.5 L46 34 L46 38 L40 37.5Z"/>
<ellipse cx="54" cy="36" rx="12" ry="14"/>'''
hull = hull.replace("<path ", '<path fill="url(#lightF)" ').replace("<ellipse ", '<ellipse fill="url(#lightF)" ')
detail = f'''
<g fill="none" stroke="#7d838f" stroke-width="0.6">
 <ellipse cx="54" cy="36" rx="8" ry="9.5"/><path d="M12 36 L40 36 M54 22 L54 26.5 M54 45.5 L54 50"/>
</g>
<ellipse cx="55" cy="36" rx="2.6" ry="3" fill="#d9dde3" stroke="{INK}" stroke-width="0.6"/>
<g fill="#ffe8a0" opacity="0.9"><rect x="62" y="31" width="1" height="1"/><rect x="62" y="40" width="1" height="1"/><rect x="28" y="33" width="1" height="1"/><rect x="32" y="38" width="1" height="1"/></g>'''
glow = '''
<rect x="6" y="26" width="25" height="1.8" rx="0.9" fill="#5ec8ff"/>
<rect x="6" y="44.2" width="25" height="1.8" rx="0.9" fill="#5ec8ff"/>
<ellipse cx="33.4" cy="26.8" rx="1.3" ry="1.2" fill="#ff4b37"/><ellipse cx="33.4" cy="45.2" rx="1.3" ry="1.2" fill="#ff4b37"/>
<ellipse cx="42.6" cy="36" rx="1" ry="2" fill="#7fd4ff"/>'''
ships["federation-excelsior"] = wrap(hull, detail + '<rect x="14" y="34.9" width="24" height="2.2" fill="#EC008C"/><ellipse cx="54" cy="36" rx="8" ry="9.5" fill="none" stroke="#EC008C" stroke-width="1.2"/>', glow)

# ---------- Federation: Defiant-type escort (compact arrowhead, integrated nacelle pods)
hull = '''
<path d="M15 21 L33 21 Q46 22 56 28 Q62 32 62 36 Q62 40 56 44 Q46 50 33 51 L15 51 Q12 49 14 46 L20 44 L20 28 L14 26 Q12 23 15 21Z"/>'''
hull = hull.replace("<path ", '<path fill="url(#lightF)" ')
detail = f'''
<g fill="none" stroke="#7d838f" stroke-width="0.6">
 <path d="M24 29 Q40 28 52 33 M24 43 Q40 44 52 39 M38 26 L38 46"/>
</g>
<path d="M42 33 Q50 34 52 36 Q50 38 42 39Z" fill="#c3c8d0" stroke="{INK}" stroke-width="0.6"/>
<path d="M22 31 L30 31 L30 41 L22 41Z" fill="#9aa0ab" stroke="{INK}" stroke-width="0.5"/>
<g fill="#ffe8a0"><rect x="46" y="31" width="1" height="1"/><rect x="46" y="40" width="1" height="1"/></g>'''
glow = '''
<rect x="15" y="22.5" width="17" height="2.2" rx="1" fill="#5ec8ff"/>
<rect x="15" y="47.3" width="17" height="2.2" rx="1" fill="#5ec8ff"/>
<rect x="14.6" y="33" width="1.6" height="6" fill="#ff7a3a"/>
<ellipse cx="59" cy="31" rx="1" ry="0.8" fill="#ff4b37"/><ellipse cx="59" cy="41" rx="1" ry="0.8" fill="#ff4b37"/>
<ellipse cx="60.5" cy="36" rx="1" ry="1.6" fill="#ffb347"/>'''
ships["federation-defiant"] = wrap(hull, detail + '<path d="M24 29 Q40 28 52 33 M24 43 Q40 44 52 39" fill="none" stroke="#EC008C" stroke-width="1.5"/>', glow)

# ---------- Klingon: Bird-of-Prey-type raider (forward head on neck, swept wings, wingtip cannons)
hull = '''
<path d="M14 30 Q22 27 34 31 L34 41 Q22 45 14 42 Q11 36 14 30Z"/>
<path d="M26 31 Q26 17 38 6 L44 6 Q36 18 37 32Z"/>
<path d="M26 41 Q26 55 38 66 L44 66 Q36 54 37 40Z"/>
<path d="M33 33.5 L52 34.5 L52 37.5 L33 38.5Z"/>
<path d="M50 30 Q60 29 64 34 Q65 36 64 38 Q60 43 50 42 Q48 36 50 30Z"/>'''
hull = hull.replace("<path ", '<path fill="url(#lightK)" ')
detail = f'''
<g fill="none" stroke="#2d3d22" stroke-width="0.6">
 <path d="M31 27 Q31 17 39 8.5 M31 45 Q31 55 39 63.5 M18 33 Q25 31 32 34 M18 39 Q25 41 32 38"/>
 <path d="M30 22 L35 21 M30 50 L35 51 M33 14 L38 14 M33 58 L38 58"/>
 <path d="M54 33 Q59 33 62 36 Q59 39 54 39"/>
</g>
<path d="M43 4.6 L51 5.2 L51 6.8 L43 7.4Z" fill="#5a6a48" stroke="{INK}" stroke-width="0.6"/>
<path d="M43 64.6 L51 65.2 L51 66.8 L43 67.4Z" fill="#5a6a48" stroke="{INK}" stroke-width="0.6"/>'''
glow = '''
<ellipse cx="51.4" cy="6" rx="1.2" ry="1" fill="#7cff6a"/><ellipse cx="51.4" cy="66" rx="1.2" ry="1" fill="#7cff6a"/>
<ellipse cx="63" cy="36" rx="1" ry="1.4" fill="#ff5a2a"/>
<rect x="13" y="33.5" width="1.6" height="5" fill="#ff5a2a"/>
<rect x="56" y="34.5" width="1" height="1" fill="#ffd27a"/><rect x="56" y="36.5" width="1" height="1" fill="#ffd27a"/>'''
ships["klingon-bird-of-prey"] = wrap(hull, detail + '<path d="M31 27 Q31 17 39 8.5 M31 45 Q31 55 39 63.5" fill="none" stroke="#EC008C" stroke-width="1.5"/>', glow, side="#223018")

# ---------- Dominion: Jem'Hadar-type attack ship (beetle body, forward prongs, violet emitter)
hull = '''
<path d="M14 31 Q24 24 40 25 L54 22 Q62 24 64 30 L52 31 Q54 36 52 41 L64 42 Q62 48 54 50 L40 47 Q24 48 14 41 Q11 36 14 31Z"/>
<path d="M22 25 Q30 16 42 16 L44 19 Q34 21 30 27Z"/>
<path d="M22 47 Q30 56 42 56 L44 53 Q34 51 30 45Z"/>'''
hull = hull.replace("<path ", '<path fill="url(#lightD)" ')
detail = f'''
<g fill="none" stroke="#4c4760" stroke-width="0.6">
 <path d="M18 36 L50 36 M24 30 Q36 28 48 29 M24 42 Q36 44 48 43 M40 26 L40 46"/>
</g>
<path d="M30 32.5 L46 33.5 L46 38.5 L30 39.5Z" fill="#8a84a0" stroke="{INK}" stroke-width="0.5"/>'''
glow = '''
<path d="M31 34.5 L45 35 L45 37 L31 37.5Z" fill="#c779ff"/>
<rect x="12.8" y="33" width="1.6" height="6" fill="#c779ff"/>
<ellipse cx="63" cy="30.5" rx="1" ry="0.8" fill="#e6a6ff"/><ellipse cx="63" cy="41.5" rx="1" ry="0.8" fill="#e6a6ff"/>'''
ships["dominion-attack-ship"] = wrap(hull, detail + '<path d="M24 30 Q36 28 48 29 M24 42 Q36 44 48 43" fill="none" stroke="#EC008C" stroke-width="1.5"/>', glow, side="#2e2a3c")

# ---------- Dominion: battle cruiser (long heavy hull, layered side fins, multiple emitters)
hull = '''
<path d="M4 32 Q8 27 20 26 L50 27 Q62 29 67 34 Q68 36 67 38 Q62 43 50 45 L20 46 Q8 45 4 40 Q2.5 36 4 32Z"/>
<path d="M12 27 Q16 13 28 10 L36 10 Q30 16 28 27Z"/>
<path d="M12 45 Q16 59 28 62 L36 62 Q30 56 28 45Z"/>
<path d="M30 27 Q36 17 48 15 L52 17 Q44 20 42 27Z"/>
<path d="M30 45 Q36 55 48 57 L52 55 Q44 52 42 45Z"/>'''
hull = hull.replace("<path ", '<path fill="url(#lightD)" ')
detail = f'''
<g fill="none" stroke="#4c4760" stroke-width="0.6">
 <path d="M8 36 L62 36 M14 31 L56 31.5 M14 41 L56 40.5 M24 26 L24 46 M38 27 L38 45 M52 28 L52 44"/>
 <path d="M18 22 Q22 16 30 13 M18 50 Q22 56 30 59 M36 22 Q40 19 46 17 M36 50 Q40 53 46 55"/>
</g>
<path d="M54 33 Q62 34 64 36 Q62 38 54 39Z" fill="#8a84a0" stroke="{INK}" stroke-width="0.5"/>'''
glow = '''
<path d="M10 34.8 L50 35.2 L50 36.8 L10 37.2Z" fill="#c779ff"/>
<rect x="2.8" y="33" width="1.6" height="6" fill="#c779ff"/>
<ellipse cx="34.5" cy="10.5" rx="1.1" ry="0.8" fill="#e6a6ff"/><ellipse cx="34.5" cy="61.5" rx="1.1" ry="0.8" fill="#e6a6ff"/>
<ellipse cx="51" cy="16.2" rx="1" ry="0.7" fill="#e6a6ff"/><ellipse cx="51" cy="55.8" rx="1" ry="0.7" fill="#e6a6ff"/>
<ellipse cx="65.6" cy="36" rx="0.9" ry="1.3" fill="#e6a6ff"/>'''
ships["dominion-battle-cruiser"] = wrap(hull, detail + '<path d="M18 22 Q22 16 30 13 M18 50 Q22 56 30 59 M36 22 Q40 19 46 17 M36 50 Q40 53 46 55" fill="none" stroke="#EC008C" stroke-width="1.5"/>', glow, side="#2e2a3c")

for k, v in ships.items():
    open(os.path.join(OUT, k + ".svg"), "w").write(v)
print(list(ships))

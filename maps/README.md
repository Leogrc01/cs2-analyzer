# Maps Folder - Radar Images

Place your CS2 radar overview images here for better heatmap visualization.

## 📁 File naming

Files should be named exactly as they appear in CS2:
- `de_dust2.png`
- `de_mirage.png`
- `de_inferno.png`
- `de_nuke.png`
- `de_anubis.png`
- `de_vertigo.png`
- `de_ancient.png`

## 🔍 Where to find radar images

### Option 1: Extract from CS2 game files
1. Navigate to your CS2 installation folder
2. Go to `csgo/resource/overviews/`
3. Find the `.dds` files (e.g., `de_dust2_radar.dds`)
4. Convert `.dds` to `.png` using an image converter

### Option 2: Download from online sources
- **CS2 Map Overviews**: https://readtldr.gg/simpleradar
- **SimpleRadar**: Pre-made clean radar images
- **Reddit/Steam Guides**: Search for "CS2 radar images"

### Option 3: Use screenshot from CS2
1. Open CS2
2. Type `sv_cheats 1` in console
3. Type `cl_leveloverview 1` to see the radar overview
4. Take a screenshot
5. Crop and save as PNG

## 📐 Image requirements

- **Format**: PNG (preferred) or JPG
- **Size**: 1024x1024 pixels minimum (higher is better)
- **Quality**: Clear, high-contrast radar view
- **Orientation**: Top-down view matching game radar

## 🎨 Usage

Once you have the map images in this folder, use the overlay script:

```bash
venv/bin/python generate_heatmap_overlay.py demos/match.dem "PlayerName"
```

The script will automatically detect and use the map image if available!

## 💡 Tips

- Use clean, minimal radar images for best results
- Avoid images with too much detail (just show paths and key areas)
- Make sure the image is properly aligned (north facing up)
- Higher resolution = better quality heatmap

## Example structure:
```
maps/
├── README.md (this file)
├── de_dust2.png
├── de_mirage.png
└── de_inferno.png
```

#!/usr/bin/env bash
set -euo pipefail

DEST="$HOME/Documents/bgo_fs_media_archive"
SOURCE_BASE="/media/andy"

mkdir -p "$DEST"/{maps,mods,lua,xml_i3d,images,manifests}

echo "Destination: $DEST"
echo "Scanning: $SOURCE_BASE"

# Find Farming Simulator folders on mounted media.
find "$SOURCE_BASE" -maxdepth 2 -type d \
  \( -iname "*Farming Simulator*" -o -iname "*FarmingSimulator*" \) \
  > "$DEST/manifests/farming_simulator_roots.txt"

echo "Found roots:"
cat "$DEST/manifests/farming_simulator_roots.txt"

# Save all folder paths.
while IFS= read -r root; do
  safe_root_name="$(basename "$root" | tr ' ' '_' | tr -cd 'A-Za-z0-9_-.')"

  echo "Indexing folders in: $root"
  find "$root" -type d >> "$DEST/manifests/all_folder_paths.txt"

  echo "Copying map folders from: $root"
  find "$root" -type d \( -iname "maps" -o -iname "map" \) -print0 |
  while IFS= read -r -d '' mapdir; do
    mkdir -p "$DEST/maps/$safe_root_name"
    rsync -a --info=progress2 "$mapdir" "$DEST/maps/$safe_root_name/"
  done

  echo "Copying mod folders and mod zip files from: $root"
  find "$root" -type d \( -iname "mods" -o -iname "mod" \) -print0 |
  while IFS= read -r -d '' moddir; do
    mkdir -p "$DEST/mods/$safe_root_name"
    rsync -a --info=progress2 "$moddir" "$DEST/mods/$safe_root_name/"
  done

  find "$root" -type f \( -iname "*.zip" -o -iname "modDesc.xml" \) -print0 |
  while IFS= read -r -d '' file; do
    rel="${file#$root/}"
    mkdir -p "$DEST/mods/$safe_root_name/$(dirname "$rel")"
    cp -n "$file" "$DEST/mods/$safe_root_name/$rel" || true
  done

  echo "Copying Lua files from: $root"
  find "$root" -type f -iname "*.lua" -print0 |
  while IFS= read -r -d '' file; do
    rel="${file#$root/}"
    mkdir -p "$DEST/lua/$safe_root_name/$(dirname "$rel")"
    cp -n "$file" "$DEST/lua/$safe_root_name/$rel" || true
  done

  echo "Copying XML/I3D files from: $root"
  find "$root" -type f \( -iname "*.xml" -o -iname "*.i3d" \) -print0 |
  while IFS= read -r -d '' file; do
    rel="${file#$root/}"
    mkdir -p "$DEST/xml_i3d/$safe_root_name/$(dirname "$rel")"
    cp -n "$file" "$DEST/xml_i3d/$safe_root_name/$rel" || true
  done

  echo "Copying images/textures from: $root"
  find "$root" -type f \( \
    -iname "*.png" -o \
    -iname "*.jpg" -o \
    -iname "*.jpeg" -o \
    -iname "*.dds" -o \
    -iname "*.tga" -o \
    -iname "*.bmp" \
  \) -print0 |
  while IFS= read -r -d '' file; do
    rel="${file#$root/}"
    mkdir -p "$DEST/images/$safe_root_name/$(dirname "$rel")"
    cp -n "$file" "$DEST/images/$safe_root_name/$rel" || true
  done

done < "$DEST/manifests/farming_simulator_roots.txt"

# Create useful manifests.
find "$DEST" -type f > "$DEST/manifests/copied_files_manifest.txt"
find "$DEST" -type f -iname "*.i3d" > "$DEST/manifests/i3d_files.txt"
find "$DEST" -type f -iname "*.xml" > "$DEST/manifests/xml_files.txt"
find "$DEST" -type f -iname "*.lua" > "$DEST/manifests/lua_files.txt"
find "$DEST" -type f \( -iname "*.png" -o -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.dds" -o -iname "*.tga" -o -iname "*.bmp" \) > "$DEST/manifests/image_files.txt"

echo ""
echo "Done."
echo "Archive created at:"
echo "$DEST"
echo ""
echo "Manifests:"
echo "$DEST/manifests/farming_simulator_roots.txt"
echo "$DEST/manifests/all_folder_paths.txt"
echo "$DEST/manifests/copied_files_manifest.txt"
echo "$DEST/manifests/i3d_files.txt"
echo "$DEST/manifests/xml_files.txt"
echo "$DEST/manifests/lua_files.txt"
echo "$DEST/manifests/image_files.txt"

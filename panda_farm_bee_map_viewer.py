from __future__ import annotations

import argparse
import importlib.util
import math
import os
import subprocess
import sys
import textwrap
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


FS_ROOTS = [
    Path("/media/andy/Farming Simulator 17"),
    Path("/media/andy/Farming Simulator 15 Gold"),
    Path("/media/andy/Farming Simulator 2013"),
]


def ensure_package(import_name: str, pip_name: str) -> None:
    if importlib.util.find_spec(import_name) is not None:
        return

    print(f"[setup] missing {import_name}. attempting pip install {pip_name}")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
    except subprocess.CalledProcessError:
        print("")
        print("[error] automatic install failed.")
        print("On Debian 13 use a venv:")
        print("  python3 -m venv .venv")
        print("  source .venv/bin/activate")
        print("  python -m pip install --upgrade pip")
        print("  python -m pip install panda3d")
        raise SystemExit(1)

    print("[setup] installed package. restarting script.")
    os.execv(sys.executable, [sys.executable] + sys.argv)


ensure_package("panda3d", "panda3d")


from direct.gui.DirectGui import DirectEntry
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    AmbientLight,
    CardMaker,
    DirectionalLight,
    Geom,
    GeomNode,
    GeomTriangles,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
    LineSegs,
    NodePath,
    TextNode,
    Vec3,
    WindowProperties,
)


@dataclass(slots=True)
class MapFeature:
    name: str
    kind: str
    x: float
    y: float
    z: float
    scale_x: float
    scale_y: float
    scale_z: float


def parse_vec3(value: str | None, default: tuple[float, float, float]) -> tuple[float, float, float]:
    if not value:
        return default

    parts = value.replace(",", " ").split()
    if len(parts) < 3:
        return default

    try:
        return float(parts[0]), float(parts[1]), float(parts[2])
    except ValueError:
        return default


def classify_feature(name: str) -> str:
    n = name.lower()

    if "field" in n or "farmland" in n:
        return "field"
    if "tree" in n or "forest" in n:
        return "tree"
    if "water" in n or "river" in n or "pond" in n:
        return "water"
    if "barn" in n or "shed" in n or "building" in n or "house" in n:
        return "building"
    if "road" in n or "street" in n:
        return "road"
    if "cow" in n or "sheep" in n or "chicken" in n or "animal" in n:
        return "animal_area"
    if "bee" in n or "hive" in n:
        return "bee_asset"
    if "flower" in n or "crop" in n or "orchard" in n:
        return "crop_or_flower"

    return "object"


def strip_namespace(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def load_i3d_features(path: Path, limit: int = 3000) -> list[MapFeature]:
    features: list[MapFeature] = []

    if not path.exists():
        raise FileNotFoundError(path)

    print(f"[load] reading i3d/xml: {path}")

    try:
        context = ET.iterparse(path, events=("start",))
        for _, elem in context:
            attrs = elem.attrib
            name = attrs.get("name") or attrs.get("id") or attrs.get("nodeId")
            if not name:
                continue

            translation = parse_vec3(attrs.get("translation"), (0.0, 0.0, 0.0))
            scale = parse_vec3(attrs.get("scale"), (1.0, 1.0, 1.0))

            if translation == (0.0, 0.0, 0.0) and name.lower() in {"transform", "shape"}:
                continue

            features.append(
                MapFeature(
                    name=str(name),
                    kind=classify_feature(str(name)),
                    x=translation[0],
                    y=translation[1],
                    z=translation[2],
                    scale_x=scale[0],
                    scale_y=scale[1],
                    scale_z=scale[2],
                )
            )

            if len(features) >= limit:
                break

            elem.clear()
    except ET.ParseError as exc:
        print(f"[warn] XML parse error: {exc}")

    print(f"[load] features: {len(features)}")
    return features


def find_candidate_i3d() -> Path | None:
    candidates: list[Path] = []

    for root in FS_ROOTS:
        if not root.exists():
            continue

        print(f"[scan] {root}")
        for pattern in ("map01.i3d", "map.i3d", "*.i3d"):
            try:
                for path in root.rglob(pattern):
                    lowered = str(path).lower()
                    if "/data/maps/" in lowered or "map" in path.name.lower():
                        candidates.append(path)
                        if len(candidates) >= 20:
                            break
            except PermissionError:
                pass

            if candidates:
                break

    if not candidates:
        return None

    candidates.sort(key=lambda p: (0 if "farming simulator 17" in str(p).lower() else 1, len(str(p))))
    return candidates[0]


def make_box(name: str, sx: float, sy: float, sz: float, colour: tuple[float, float, float, float]) -> NodePath:
    fmt = GeomVertexFormat.getV3n3c4()
    vdata = GeomVertexData(name, fmt, Geom.UHStatic)

    vertex = GeomVertexWriter(vdata, "vertex")
    normal = GeomVertexWriter(vdata, "normal")
    color = GeomVertexWriter(vdata, "color")

    x = sx / 2
    y = sy / 2
    z = sz / 2

    verts = [
        (-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
        (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z),
    ]

    for vx, vy, vz in verts:
        vertex.addData3(vx, vy, vz)
        normal.addData3(0, 0, 1)
        color.addData4(*colour)

    faces = [
        (0, 1, 2), (0, 2, 3),
        (4, 6, 5), (4, 7, 6),
        (0, 4, 5), (0, 5, 1),
        (1, 5, 6), (1, 6, 2),
        (2, 6, 7), (2, 7, 3),
        (3, 7, 4), (3, 4, 0),
    ]

    tris = GeomTriangles(Geom.UHStatic)
    for a, b, c in faces:
        tris.addVertices(a, b, c)

    geom = Geom(vdata)
    geom.addPrimitive(tris)

    node = GeomNode(name)
    node.addGeom(geom)
    return NodePath(node)


def make_ground(size: float = 4096.0) -> NodePath:
    card = CardMaker("farm_ground")
    card.setFrame(-size / 2, size / 2, -size / 2, size / 2)
    node = NodePath(card.generate())
    node.setP(-90)
    node.setColor(0.18, 0.42, 0.18, 1.0)
    return node


def make_axes(size: float = 500.0) -> NodePath:
    lines = LineSegs()
    lines.setThickness(2.0)

    lines.setColor(1, 0, 0, 1)
    lines.moveTo(0, 0, 0)
    lines.drawTo(size, 0, 0)

    lines.setColor(0, 1, 0, 1)
    lines.moveTo(0, 0, 0)
    lines.drawTo(0, size, 0)

    lines.setColor(0, 0, 1, 1)
    lines.moveTo(0, 0, 0)
    lines.drawTo(0, 0, size)

    return NodePath(lines.create())


def colour_for_kind(kind: str) -> tuple[float, float, float, float]:
    return {
        "field": (0.50, 0.35, 0.12, 1.0),
        "tree": (0.05, 0.45, 0.10, 1.0),
        "water": (0.10, 0.35, 0.90, 0.85),
        "building": (0.55, 0.55, 0.55, 1.0),
        "road": (0.12, 0.12, 0.12, 1.0),
        "animal_area": (0.90, 0.70, 0.35, 1.0),
        "bee_asset": (0.95, 0.75, 0.10, 1.0),
        "crop_or_flower": (0.90, 0.30, 0.70, 1.0),
        "object": (0.65, 0.65, 0.75, 1.0),
    }.get(kind, (0.75, 0.75, 0.75, 1.0))


class FarmMapViewer(ShowBase):
    def __init__(self, i3d_path: Path | None, start_x: float, start_y: float, start_z: float) -> None:
        super().__init__()

        self.disableMouse()
        self.setBackgroundColor(0.08, 0.11, 0.16, 1.0)

        props = WindowProperties()
        props.setTitle("BGO Panda3D Farming Simulator Map Viewer")
        props.setSize(1400, 900)
        self.win.requestProperties(props)

        self.camera.setPos(start_x, start_y, start_z)
        self.camera.setHpr(0, -35, 0)

        self.move_speed = 40.0
        self.turn_speed = 60.0
        self.keys: dict[str, bool] = {}

        self.features: list[MapFeature] = []
        self.i3d_path = i3d_path

        self.setup_scene()
        self.setup_controls()
        self.setup_ui()
        self.taskMgr.add(self.update_camera, "update_camera")

    def setup_scene(self) -> None:
        ground = make_ground(4096)
        ground.reparentTo(self.render)

        axes = make_axes(400)
        axes.reparentTo(self.render)

        ambient = AmbientLight("ambient")
        ambient.setColor((0.35, 0.35, 0.35, 1))
        self.render.setLight(self.render.attachNewNode(ambient))

        sun = DirectionalLight("sun")
        sun.setColor((0.95, 0.92, 0.85, 1))
        sun_np = self.render.attachNewNode(sun)
        sun_np.setHpr(-40, -60, 0)
        self.render.setLight(sun_np)

        if self.i3d_path:
            self.features = load_i3d_features(self.i3d_path)
            self.draw_features(self.features)
        else:
            self.draw_demo_area()

    def draw_features(self, features: list[MapFeature]) -> None:
        for index, feature in enumerate(features):
            if index > 1200:
                break

            sx, sy, sz = self.size_for_feature(feature)
            box = make_box(feature.name[:40], sx, sy, sz, colour_for_kind(feature.kind))
            box.reparentTo(self.render)

            # GIANTS is commonly Y-up, ground plane X/Z. Panda here uses X/Y as ground and Z up.
            box.setPos(feature.x, feature.z, max(0.5, feature.y + sz / 2))

        print("[viewer] drew proxy geometry. I3D models are represented as simple classified boxes.")

    def draw_demo_area(self) -> None:
        demo = [
            MapFeature("field_01", "field", -150, 0, -80, 1, 1, 1),
            MapFeature("field_02", "field", 150, 0, -80, 1, 1, 1),
            MapFeature("bee_bio_cosphere_unit", "bee_asset", 0, 0, 0, 1, 1, 1),
            MapFeature("wildflower_zone", "crop_or_flower", 0, 0, 150, 1, 1, 1),
            MapFeature("farm_building", "building", -220, 0, 120, 1, 1, 1),
            MapFeature("pond", "water", 240, 0, 130, 1, 1, 1),
        ]
        self.draw_features(demo)

    @staticmethod
    def size_for_feature(feature: MapFeature) -> tuple[float, float, float]:
        if feature.kind == "field":
            return 80.0, 80.0, 2.0
        if feature.kind == "tree":
            return 8.0, 8.0, 30.0
        if feature.kind == "water":
            return 60.0, 60.0, 1.0
        if feature.kind == "building":
            return 35.0, 35.0, 22.0
        if feature.kind == "road":
            return 80.0, 8.0, 1.0
        if feature.kind == "bee_asset":
            return 18.0, 18.0, 12.0
        if feature.kind == "crop_or_flower":
            return 45.0, 45.0, 3.0
        return 10.0, 10.0, 8.0

    def setup_controls(self) -> None:
        for key in [
            "w", "a", "s", "d", "q", "e",
            "arrow_left", "arrow_right", "arrow_up", "arrow_down",
            "shift", "control",
        ]:
            self.accept(key, self.set_key, [key, True])
            self.accept(f"{key}-up", self.set_key, [key, False])

        self.accept("wheel_up", self.adjust_speed, [1.20])
        self.accept("wheel_down", self.adjust_speed, [0.82])
        self.accept("g", self.show_goto_entry)
        self.accept("escape", sys.exit)

    def setup_ui(self) -> None:
        self.help_text = OnscreenText(
            text=(
                "WASD move | Q/E up/down | arrows turn/look | mouse wheel speed | "
                "G go to coordinates | ESC quit"
            ),
            pos=(-1.32, 0.94),
            scale=0.045,
            align=TextNode.ALeft,
            fg=(0.9, 0.95, 1.0, 1.0),
        )

        source = str(self.i3d_path) if self.i3d_path else "demo generated area"
        self.status_text = OnscreenText(
            text=f"source: {source}",
            pos=(-1.32, 0.88),
            scale=0.038,
            align=TextNode.ALeft,
            fg=(0.75, 0.85, 1.0, 1.0),
        )

        self.coord_text = OnscreenText(
            text="",
            pos=(-1.32, -0.94),
            scale=0.04,
            align=TextNode.ALeft,
            fg=(0.95, 0.95, 0.80, 1.0),
        )

        self.goto_entry: DirectEntry | None = None

    def set_key(self, key: str, value: bool) -> None:
        self.keys[key] = value

    def adjust_speed(self, factor: float) -> None:
        self.move_speed = max(2.0, min(800.0, self.move_speed * factor))

    def show_goto_entry(self) -> None:
        if self.goto_entry is not None:
            self.goto_entry.destroy()

        self.goto_entry = DirectEntry(
            text="",
            scale=0.05,
            pos=(-1.0, 0, -0.82),
            width=25,
            command=self.goto_coordinates,
            initialText="0 0 120",
            numLines=1,
            focus=1,
        )

    def goto_coordinates(self, text: str) -> None:
        parts = text.replace(",", " ").split()

        try:
            if len(parts) == 2:
                x = float(parts[0])
                y = float(parts[1])
                z = 120.0
            elif len(parts) >= 3:
                x = float(parts[0])
                y = float(parts[1])
                z = float(parts[2])
            else:
                return

            self.camera.setPos(x, y, z)
            self.status_text.setText(f"jumped to coordinates: {x:.2f} {y:.2f} {z:.2f}")
        except ValueError:
            self.status_text.setText("bad coordinate entry. use: x y z")

        if self.goto_entry is not None:
            self.goto_entry.destroy()
            self.goto_entry = None

    def update_camera(self, task):
        dt = globalClock.getDt()
        speed = self.move_speed * dt

        if self.keys.get("shift"):
            speed *= 3.0
        if self.keys.get("control"):
            speed *= 0.25

        h = math.radians(self.camera.getH())
        forward = Vec3(math.sin(h), math.cos(h), 0)
        right = Vec3(math.cos(h), -math.sin(h), 0)

        pos = self.camera.getPos()

        if self.keys.get("w"):
            pos += forward * speed
        if self.keys.get("s"):
            pos -= forward * speed
        if self.keys.get("d"):
            pos += right * speed
        if self.keys.get("a"):
            pos -= right * speed
        if self.keys.get("e"):
            pos.z += speed
        if self.keys.get("q"):
            pos.z -= speed

        self.camera.setPos(pos)

        hpr = self.camera.getHpr()
        turn = self.turn_speed * dt

        if self.keys.get("arrow_left"):
            hpr.x += turn
        if self.keys.get("arrow_right"):
            hpr.x -= turn
        if self.keys.get("arrow_up"):
            hpr.y = min(85, hpr.y + turn)
        if self.keys.get("arrow_down"):
            hpr.y = max(-85, hpr.y - turn)

        self.camera.setHpr(hpr)

        c = self.camera.getPos()
        self.coord_text.setText(
            f"camera x={c.x:.2f} y={c.y:.2f} z={c.z:.2f} speed={self.move_speed:.1f}"
        )

        return task.cont


def write_lua_mod(output_dir: Path) -> None:
    scripts = output_dir / "scripts"
    placeables = output_dir / "placeables"
    scripts.mkdir(parents=True, exist_ok=True)
    placeables.mkdir(parents=True, exist_ok=True)

    mod_desc = """<?xml version="1.0" encoding="utf-8" standalone="no"?>
<modDesc descVersion="32">
  <author>BGO</author>
  <version>0.1.0</version>

  <title>
    <en>BGO Bee Pollination Prototype</en>
  </title>

  <description>
    <en>Starter bee colony and pollination concept for Farming Simulator mod testing.</en>
  </description>

  <iconFilename>modIcon.dds</iconFilename>
  <multiplayer supported="false"/>

  <extraSourceFiles>
    <sourceFile filename="scripts/BeePollination.lua"/>
  </extraSourceFiles>
</modDesc>
"""

    lua = """BeePollination = {}

function BeePollination:loadMap(name)
    print("BGO BeePollination loadMap: " .. tostring(name))
    self.bgo_beeTimer = 0
    self.bgo_pollinationScore = 0
end

function BeePollination:deleteMap()
    print("BGO BeePollination deleteMap")
end

function BeePollination:keyEvent(unicode, sym, modifier, isDown)
end

function BeePollination:mouseEvent(posX, posY, isDown, isUp, button)
end

function BeePollination:update(dt)
    if self.bgo_beeTimer == nil then
        self.bgo_beeTimer = 0
    end

    self.bgo_beeTimer = self.bgo_beeTimer + dt

    if self.bgo_beeTimer > 5000 then
        self.bgo_beeTimer = 0
        self.bgo_pollinationScore = (self.bgo_pollinationScore or 0) + 1
        print("BGO BeePollination tick. score=" .. tostring(self.bgo_pollinationScore))
    end
end

function BeePollination:draw()
end

addModEventListener(BeePollination)
"""

    placeable = """<?xml version="1.0" encoding="utf-8"?>
<placeable>
  <bgoBeeMetadata
    id="bee_bio_cosphere_unit"
    species="honey_bee"
    sociality="eusocial"
    colony_strength="0.800"
    pollination_radius="150.000"
    display_label="Bee Bio-Cosphere Unit"/>
</placeable>
"""

    (output_dir / "modDesc.xml").write_text(mod_desc, encoding="utf-8")
    (scripts / "BeePollination.lua").write_text(lua, encoding="utf-8")
    (placeables / "bee_bio_cosphere_unit.xml").write_text(placeable, encoding="utf-8")

    print(f"[write] Lua/XML starter mod written to: {output_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--i3d", default=None, help="Path to map .i3d file")
    parser.add_argument("--goto", nargs=3, type=float, default=[0.0, -260.0, 180.0])
    parser.add_argument("--write-lua", action="store_true")
    parser.add_argument("--lua-out", default="exports/bgo_bee_pollination_mod")
    args = parser.parse_args()

    if args.write_lua:
        write_lua_mod(Path(args.lua_out))
        return

    i3d_path = Path(args.i3d) if args.i3d else find_candidate_i3d()

    if i3d_path is None:
        print("[warn] no Farming Simulator .i3d found. loading generated demo area.")
    else:
        print(f"[start] using map: {i3d_path}")

    app = FarmMapViewer(
        i3d_path=i3d_path,
        start_x=float(args.goto[0]),
        start_y=float(args.goto[1]),
        start_z=float(args.goto[2]),
    )
    app.run()


if __name__ == "__main__":
    main()

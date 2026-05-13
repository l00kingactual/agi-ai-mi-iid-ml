from __future__ import annotations

import hashlib
import json
import math
import random
import statistics
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import pygame


# ============================================================
# Janus CoRT60 Bee Colony Optimisation Pygame Prototype
# ============================================================
#
# Purpose:
# - Bee Colony Optimisation as a strategic simulation.
# - Scouts discover resources.
# - Workers exploit best known sources.
# - Guards respond to threats.
# - Reserve bees preserve resilience.
# - Resources model flowers/crops.
# - Pollination and cross-pollination are tracked.
# - CoRT60 explains the behaviour.
# - Janus encodes the simulation state into 13 axes + 64-bit signature.
# - Strategy Cube presets alter colony doctrine.
#
# Controls:
# - SPACE: pause/resume
# - R: reset simulation
# - 1: Explorer strategy
# - 2: Exploiter strategy
# - 3: Balanced strategy
# - 4: Pollination strategy
# - E: export current run state to JSON
# - H: hide/show help overlay
# - UP/DOWN: increase/decrease simulation speed
#
# ============================================================


# ============================================================
# Utility
# ============================================================

def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def distance(a: pygame.Vector2, b: pygame.Vector2) -> float:
    return (a - b).length()


def safe_mean(values: list[float], default: float = 0.0) -> float:
    if not values:
        return default
    return statistics.mean(values)


def normalise(value: float, maximum: float) -> float:
    if maximum <= 0:
        return 0.0
    return clamp(value / maximum)


def vector_to_dict(v: pygame.Vector2) -> dict[str, float]:
    return {"x": float(v.x), "y": float(v.y)}


def dict_to_vector(data: dict[str, float]) -> pygame.Vector2:
    return pygame.Vector2(float(data["x"]), float(data["y"]))


# ============================================================
# Metadata Layer
# ============================================================

class BeeSociality(str, Enum):
    EUSOCIAL = "eusocial"
    PRIMITIVELY_SOCIAL = "primitively_social"
    SOLITARY = "solitary"


class NestingType(str, Enum):
    HIVE = "hive"
    GROUND = "ground"
    CAVITY = "cavity"
    STEM = "stem"
    WOOD = "wood"
    MANAGED_BOX = "managed_box"


@dataclass(slots=True)
class BeeSpeciesMetadata:
    common_name: str
    scientific_name: str
    sociality: BeeSociality
    nesting_type: NestingType
    managed: bool
    pollination_style: str
    typical_roles: list[str]
    notes: str
    source_tier: str = "starter_seed_metadata"


@dataclass(slots=True)
class CropProfile:
    name: str
    flowering_season: str
    insect_pollination_dependency: float
    cross_pollination_need: float
    environmental_value: float
    human_food_value: float
    notes: str


BEE_METADATA: dict[str, BeeSpeciesMetadata] = {
    "honey_bee": BeeSpeciesMetadata(
        common_name="Honey bee",
        scientific_name="Apis mellifera",
        sociality=BeeSociality.EUSOCIAL,
        nesting_type=NestingType.HIVE,
        managed=True,
        pollination_style="generalist colony forager",
        typical_roles=["queen", "drone", "nurse", "builder", "guard", "scout", "forager", "reserve"],
        notes="Strong colony model; useful for managed pollination but not a substitute for wild bee diversity.",
    ),
    "bumblebee": BeeSpeciesMetadata(
        common_name="Bumblebee",
        scientific_name="Bombus spp.",
        sociality=BeeSociality.PRIMITIVELY_SOCIAL,
        nesting_type=NestingType.CAVITY,
        managed=True,
        pollination_style="buzz pollination and greenhouse-capable pollination",
        typical_roles=["queen", "worker", "forager", "guard"],
        notes="Useful conceptual model for greenhouse and controlled pollination.",
    ),
    "mason_bee": BeeSpeciesMetadata(
        common_name="Mason bee",
        scientific_name="Osmia spp.",
        sociality=BeeSociality.SOLITARY,
        nesting_type=NestingType.CAVITY,
        managed=True,
        pollination_style="solitary cavity-nesting orchard pollinator",
        typical_roles=["solitary_female_forager", "nest_builder"],
        notes="Solitary bee; should not be forced into honey-bee colony role logic.",
    ),
    "leafcutter_bee": BeeSpeciesMetadata(
        common_name="Leafcutter bee",
        scientific_name="Megachile spp.",
        sociality=BeeSociality.SOLITARY,
        nesting_type=NestingType.CAVITY,
        managed=True,
        pollination_style="solitary crop pollinator",
        typical_roles=["solitary_female_forager", "nest_builder"],
        notes="Useful for crop pollination and nest-block modelling.",
    ),
}


CROP_PROFILES: dict[str, CropProfile] = {
    "apple": CropProfile(
        name="Apple",
        flowering_season="spring",
        insect_pollination_dependency=0.85,
        cross_pollination_need=0.90,
        environmental_value=0.65,
        human_food_value=0.90,
        notes="Good model crop for cross-pollination and orchard simulation.",
    ),
    "almond": CropProfile(
        name="Almond",
        flowering_season="spring",
        insect_pollination_dependency=0.95,
        cross_pollination_need=0.90,
        environmental_value=0.55,
        human_food_value=0.85,
        notes="High managed-pollination dependency.",
    ),
    "clover": CropProfile(
        name="Clover",
        flowering_season="summer",
        insect_pollination_dependency=0.70,
        cross_pollination_need=0.55,
        environmental_value=0.85,
        human_food_value=0.45,
        notes="Strong forage and soil/ecology value.",
    ),
    "wildflower": CropProfile(
        name="Wildflower",
        flowering_season="mixed",
        insect_pollination_dependency=0.80,
        cross_pollination_need=0.70,
        environmental_value=0.95,
        human_food_value=0.25,
        notes="High biodiversity support.",
    ),
    "tomato": CropProfile(
        name="Tomato",
        flowering_season="greenhouse_or_summer",
        insect_pollination_dependency=0.45,
        cross_pollination_need=0.35,
        environmental_value=0.45,
        human_food_value=0.80,
        notes="Useful greenhouse/buzz-pollination concept.",
    ),
}


# ============================================================
# Strategy Cube + CoRT60 + Janus
# ============================================================

@dataclass(slots=True)
class CoRT60Weights:
    pmi: float = 0.55
    caf: float = 0.60
    ago: float = 0.75
    fip: float = 0.65
    apc: float = 0.75
    opv: float = 0.60
    consequences: float = 0.70
    planning: float = 0.65
    challenge: float = 0.45

    def as_dict(self) -> dict[str, float]:
        return asdict(self)


@dataclass(slots=True)
class BeeSocietalControls:
    scout_ratio: float = 0.30
    worker_ratio: float = 0.50
    guard_ratio: float = 0.10
    reserve_ratio: float = 0.10
    colony_cohesion: float = 0.60
    individual_variance: float = 0.55
    recruitment_pressure: float = 0.65
    social_signal_strength: float = 0.65
    risk_tolerance: float = 0.50
    pollination_bias: float = 0.55

    def normalised(self) -> "BeeSocietalControls":
        total = max(0.001, self.scout_ratio + self.worker_ratio + self.guard_ratio + self.reserve_ratio)
        return BeeSocietalControls(
            scout_ratio=self.scout_ratio / total,
            worker_ratio=self.worker_ratio / total,
            guard_ratio=self.guard_ratio / total,
            reserve_ratio=self.reserve_ratio / total,
            colony_cohesion=clamp(self.colony_cohesion),
            individual_variance=clamp(self.individual_variance),
            recruitment_pressure=clamp(self.recruitment_pressure),
            social_signal_strength=clamp(self.social_signal_strength),
            risk_tolerance=clamp(self.risk_tolerance),
            pollination_bias=clamp(self.pollination_bias),
        )

    def as_dict(self) -> dict[str, float]:
        return asdict(self.normalised())


@dataclass(slots=True)
class JanusControls:
    left_exploration_bias: float = 0.70
    right_exploitation_bias: float = 0.65
    memory_trust: float = 0.65
    signal_strength: float = 0.65
    balance_pressure: float = 0.60

    def as_dict(self) -> dict[str, float]:
        return asdict(self)


@dataclass(slots=True)
class StrategyDoctrine:
    name: str
    label: str
    description: str
    cort60: CoRT60Weights
    societal: BeeSocietalControls
    janus: JanusControls


class StrategyCube:
    """A small strategic doctrine engine.

    It maps a strategic doctrine into behaviour pressure:
    - exploration
    - exploitation
    - social memory
    - guard/risk response
    - pollination emphasis
    """

    def __init__(self) -> None:
        self.presets: dict[str, StrategyDoctrine] = {
            "explorer": StrategyDoctrine(
                name="explorer",
                label="Explorer Colony",
                description="High scout variance, high alternative search, slower convergence.",
                cort60=CoRT60Weights(apc=0.95, challenge=0.80, fip=0.35, ago=0.55, consequences=0.65),
                societal=BeeSocietalControls(
                    scout_ratio=0.52,
                    worker_ratio=0.28,
                    guard_ratio=0.07,
                    reserve_ratio=0.13,
                    colony_cohesion=0.35,
                    individual_variance=0.90,
                    recruitment_pressure=0.35,
                    social_signal_strength=0.35,
                    risk_tolerance=0.80,
                    pollination_bias=0.60,
                ),
                janus=JanusControls(
                    left_exploration_bias=0.95,
                    right_exploitation_bias=0.35,
                    memory_trust=0.35,
                    signal_strength=0.35,
                    balance_pressure=0.50,
                ),
            ),
            "exploiter": StrategyDoctrine(
                name="exploiter",
                label="Exploiter Colony",
                description="High worker exploitation, strong colony memory, fast convergence.",
                cort60=CoRT60Weights(apc=0.35, challenge=0.25, fip=0.95, ago=0.95, planning=0.80),
                societal=BeeSocietalControls(
                    scout_ratio=0.15,
                    worker_ratio=0.72,
                    guard_ratio=0.06,
                    reserve_ratio=0.07,
                    colony_cohesion=0.90,
                    individual_variance=0.25,
                    recruitment_pressure=0.95,
                    social_signal_strength=0.95,
                    risk_tolerance=0.35,
                    pollination_bias=0.45,
                ),
                janus=JanusControls(
                    left_exploration_bias=0.35,
                    right_exploitation_bias=0.95,
                    memory_trust=0.90,
                    signal_strength=0.90,
                    balance_pressure=0.55,
                ),
            ),
            "balanced": StrategyDoctrine(
                name="balanced",
                label="Balanced Society",
                description="Balanced scout/worker/reserve model with stable convergence.",
                cort60=CoRT60Weights(apc=0.75, fip=0.75, ago=0.75, consequences=0.75, planning=0.70),
                societal=BeeSocietalControls(
                    scout_ratio=0.30,
                    worker_ratio=0.50,
                    guard_ratio=0.10,
                    reserve_ratio=0.10,
                    colony_cohesion=0.65,
                    individual_variance=0.55,
                    recruitment_pressure=0.65,
                    social_signal_strength=0.65,
                    risk_tolerance=0.55,
                    pollination_bias=0.60,
                ),
                janus=JanusControls(
                    left_exploration_bias=0.70,
                    right_exploitation_bias=0.70,
                    memory_trust=0.65,
                    signal_strength=0.65,
                    balance_pressure=0.75,
                ),
            ),
            "pollination": StrategyDoctrine(
                name="pollination",
                label="Pollination / Cross-Pollination Colony",
                description="Optimises movement between compatible crops and ecological benefit.",
                cort60=CoRT60Weights(apc=0.80, fip=0.60, ago=0.80, caf=0.80, consequences=0.95, opv=0.75),
                societal=BeeSocietalControls(
                    scout_ratio=0.34,
                    worker_ratio=0.46,
                    guard_ratio=0.08,
                    reserve_ratio=0.12,
                    colony_cohesion=0.58,
                    individual_variance=0.70,
                    recruitment_pressure=0.55,
                    social_signal_strength=0.60,
                    risk_tolerance=0.58,
                    pollination_bias=0.95,
                ),
                janus=JanusControls(
                    left_exploration_bias=0.78,
                    right_exploitation_bias=0.62,
                    memory_trust=0.58,
                    signal_strength=0.60,
                    balance_pressure=0.82,
                ),
            ),
        }
        self.current = self.presets["balanced"]

    def set_preset(self, name: str) -> None:
        if name not in self.presets:
            raise KeyError(f"Unknown strategy preset: {name}")
        self.current = self.presets[name]

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.current.name,
            "label": self.current.label,
            "description": self.current.description,
            "cort60": self.current.cort60.as_dict(),
            "societal": self.current.societal.as_dict(),
            "janus": self.current.janus.as_dict(),
        }


class JanusEncoder:
    """13-axis state radar + 64-bit symbolic signature."""

    AXES = [
        "exploration",
        "exploitation",
        "convergence",
        "diversity",
        "social_memory",
        "reserve_resilience",
        "pollination",
        "cross_pollination",
        "environmental_benefit",
        "human_benefit",
        "threat_pressure",
        "energy_health",
        "strategic_balance",
    ]

    def encode(self, metrics: dict[str, float]) -> dict[str, Any]:
        axes = {
            "exploration": clamp(metrics.get("exploration_score", 0.0)),
            "exploitation": clamp(metrics.get("exploitation_score", 0.0)),
            "convergence": clamp(metrics.get("convergence_score", 0.0)),
            "diversity": clamp(metrics.get("diversity_score", 0.0)),
            "social_memory": clamp(metrics.get("social_memory_score", 0.0)),
            "reserve_resilience": clamp(metrics.get("reserve_resilience", 0.0)),
            "pollination": clamp(metrics.get("pollination_score", 0.0)),
            "cross_pollination": clamp(metrics.get("cross_pollination_score", 0.0)),
            "environmental_benefit": clamp(metrics.get("environmental_benefit", 0.0)),
            "human_benefit": clamp(metrics.get("human_benefit", 0.0)),
            "threat_pressure": clamp(metrics.get("threat_pressure", 0.0)),
            "energy_health": clamp(metrics.get("energy_health", 0.0)),
            "strategic_balance": clamp(metrics.get("strategic_balance", 0.0)),
        }

        exploration = axes["exploration"]
        exploitation = axes["exploitation"]

        if exploration > exploitation + 0.20:
            mode = "left_exploration_heavy"
        elif exploitation > exploration + 0.20:
            mode = "right_exploitation_heavy"
        else:
            mode = "janus_balanced"

        quantised = "|".join(f"{name}:{axes[name]:.3f}" for name in self.AXES)
        digest = hashlib.sha256(quantised.encode("utf-8")).hexdigest()
        signature64 = bin(int(digest[:16], 16))[2:].zfill(64)

        return {
            "axes": axes,
            "mode": mode,
            "signature64": signature64,
            "quantised": quantised,
        }


class CoRT60Explainer:
    """Live strategy explanation from the current metrics."""

    def explain(self, metrics: dict[str, float], doctrine: StrategyDoctrine) -> dict[str, Any]:
        risk = metrics.get("premature_convergence_risk", 0.0)
        threat = metrics.get("threat_pressure", 0.0)
        pollination = metrics.get("pollination_score", 0.0)
        cross = metrics.get("cross_pollination_score", 0.0)
        exploration = metrics.get("exploration_score", 0.0)
        exploitation = metrics.get("exploitation_score", 0.0)

        if risk > 0.70:
            challenge = "High premature convergence risk. Increase scouts, variance, or Challenge weight."
        elif threat > 0.65:
            challenge = "Threat pressure high. Increase guard ratio or reduce risky foraging."
        elif pollination < 0.25 and doctrine.current_name if False else False:
            challenge = "Pollination low. Increase pollination bias and cross-patch movement."
        elif exploration < 0.25 and exploitation > 0.70:
            challenge = "The colony is over-exploiting. Inject scouts or random resets."
        elif cross < 0.20:
            challenge = "Cross-pollination is weak. Encourage movement between crop patches."
        else:
            challenge = "Current colony balance is usable. Continue measurement and comparison."

        return {
            "PMI": {
                "plus": "Specialist roles allow scouts, workers, guards, and reserve bees to contribute differently.",
                "minus": "Strong social memory may over-focus the colony on one source.",
                "interesting": "Pollination value emerges from movement between resources, not only harvesting.",
            },
            "CAF": [
                "resource quality",
                "crop dependency",
                "cross-pollination need",
                "threat pressure",
                "role balance",
                "social signal",
                "energy health",
                "reserve resilience",
            ],
            "AGO": "Maximise resource discovery, pollination value, colony health, and strategic adaptability.",
            "FIP": "Prioritise high-value resources while preserving cross-pollination and role diversity.",
            "APC": "Scouts and individual variance create alternative routes and candidate resource patches.",
            "OPV": {
                "scout": "Find possibilities.",
                "worker": "Exploit known value.",
                "guard": "Reduce predation risk.",
                "reserve": "Preserve resilience.",
                "crop": "Needs visits and cross-pollen movement.",
                "environment": "Benefits from biodiversity and pollination support.",
                "human": "Benefits from food, yield stability, and ecological literacy.",
            },
            "C&S": "Early discoveries shape colony memory; over-commitment can reduce later adaptability.",
            "Planning": "Explore → identify → recruit → forage → pollinate → defend → measure → adapt.",
            "Challenge": challenge,
            "doctrine": doctrine.label,
        }


# ============================================================
# Simulation Objects
# ============================================================

class BeeRole(str, Enum):
    SCOUT = "scout"
    WORKER = "worker"
    GUARD = "guard"
    RESERVE = "reserve"


@dataclass(slots=True)
class ResourcePatch:
    id: str
    position: pygame.Vector2
    crop: str
    nectar: float
    pollen: float
    quality: float
    radius: float
    bloom_strength: float
    visits: int = 0
    cross_pollination_visits: int = 0
    depleted: bool = False

    def harvest(self, amount: float) -> float:
        if self.depleted:
            return 0.0

        taken = min(self.nectar, amount)
        self.nectar -= taken
        self.visits += 1

        if self.nectar <= 0.01:
            self.depleted = True

        crop_profile = CROP_PROFILES.get(self.crop)
        dependency = crop_profile.insect_pollination_dependency if crop_profile else 0.5

        return taken * self.quality * dependency

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "position": vector_to_dict(self.position),
            "crop": self.crop,
            "nectar": self.nectar,
            "pollen": self.pollen,
            "quality": self.quality,
            "radius": self.radius,
            "bloom_strength": self.bloom_strength,
            "visits": self.visits,
            "cross_pollination_visits": self.cross_pollination_visits,
            "depleted": self.depleted,
        }


@dataclass(slots=True)
class Threat:
    id: str
    position: pygame.Vector2
    velocity: pygame.Vector2
    radius: float
    pressure: float
    label: str = "wasp"

    def step(self, bounds: pygame.Rect) -> None:
        self.position += self.velocity

        if self.position.x < bounds.left or self.position.x > bounds.right:
            self.velocity.x *= -1
        if self.position.y < bounds.top or self.position.y > bounds.bottom:
            self.velocity.y *= -1

        self.position.x = max(bounds.left, min(bounds.right, self.position.x))
        self.position.y = max(bounds.top, min(bounds.bottom, self.position.y))

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "position": vector_to_dict(self.position),
            "velocity": vector_to_dict(self.velocity),
            "radius": self.radius,
            "pressure": self.pressure,
            "label": self.label,
        }


@dataclass(slots=True)
class Bee:
    id: str
    role: BeeRole
    position: pygame.Vector2
    velocity: pygame.Vector2
    energy: float = 1.0
    score: float = 0.0
    target_patch_id: str | None = None
    last_patch_id: str | None = None
    memory: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "role": self.role.value,
            "position": vector_to_dict(self.position),
            "velocity": vector_to_dict(self.velocity),
            "energy": self.energy,
            "score": self.score,
            "target_patch_id": self.target_patch_id,
            "last_patch_id": self.last_patch_id,
            "memory": self.memory,
        }


# ============================================================
# Bee Colony Optimisation Simulation
# ============================================================

@dataclass(slots=True)
class SimulationConfig:
    width: int = 920
    height: int = 720
    panel_width: int = 380
    bee_count: int = 70
    resource_count: int = 12
    threat_count: int = 3
    seed: int | None = 7
    species_key: str = "honey_bee"
    export_dir: str = "exports"


class BeeColonyOptimisation:
    def __init__(self, config: SimulationConfig, strategy_cube: StrategyCube) -> None:
        self.config = config
        self.strategy_cube = strategy_cube
        self.janus_encoder = JanusEncoder()
        self.cort60 = CoRT60Explainer()

        if config.seed is not None:
            random.seed(config.seed)

        self.field_rect = pygame.Rect(0, 0, config.width, config.height)
        self.hive_position = pygame.Vector2(config.width * 0.50, config.height * 0.50)
        self.iteration = 0

        self.bees: list[Bee] = []
        self.resources: list[ResourcePatch] = []
        self.threats: list[Threat] = []

        self.colony_memory: dict[str, Any] = {
            "best_patch_id": None,
            "best_patch_quality": 0.0,
            "known_patches": {},
            "social_signal": 0.0,
        }

        self.total_collected = 0.0
        self.pollination_events = 0
        self.cross_pollination_events = 0
        self.threat_hits = 0

        self.reset()

    @property
    def species(self) -> BeeSpeciesMetadata:
        return BEE_METADATA[self.config.species_key]

    def reset(self) -> None:
        if self.config.seed is not None:
            random.seed(self.config.seed)

        self.iteration = 0
        self.total_collected = 0.0
        self.pollination_events = 0
        self.cross_pollination_events = 0
        self.threat_hits = 0

        self.colony_memory = {
            "best_patch_id": None,
            "best_patch_quality": 0.0,
            "known_patches": {},
            "social_signal": 0.0,
        }

        self.resources = self._create_resources()
        self.threats = self._create_threats()
        self.bees = self._create_bees()

    def _create_resources(self) -> list[ResourcePatch]:
        crops = list(CROP_PROFILES.keys())
        resources: list[ResourcePatch] = []

        for i in range(self.config.resource_count):
            crop = random.choice(crops)
            crop_profile = CROP_PROFILES[crop]

            quality = random.uniform(0.35, 1.0)
            bloom = random.uniform(0.45, 1.0)
            nectar = random.uniform(50, 180) * bloom
            pollen = random.uniform(20, 100) * crop_profile.cross_pollination_need

            resources.append(
                ResourcePatch(
                    id=f"patch-{i}",
                    position=pygame.Vector2(
                        random.uniform(60, self.config.width - 60),
                        random.uniform(60, self.config.height - 60),
                    ),
                    crop=crop,
                    nectar=nectar,
                    pollen=pollen,
                    quality=quality,
                    radius=random.uniform(22, 48),
                    bloom_strength=bloom,
                )
            )

        return resources

    def _create_threats(self) -> list[Threat]:
        threats: list[Threat] = []

        for i in range(self.config.threat_count):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(0.4, 1.6)

            threats.append(
                Threat(
                    id=f"threat-{i}",
                    position=pygame.Vector2(
                        random.uniform(80, self.config.width - 80),
                        random.uniform(80, self.config.height - 80),
                    ),
                    velocity=pygame.Vector2(math.cos(angle) * speed, math.sin(angle) * speed),
                    radius=random.uniform(28, 48),
                    pressure=random.uniform(0.25, 0.75),
                    label=random.choice(["wasp", "hornet", "bird"]),
                )
            )

        return threats

    def _create_bees(self) -> list[Bee]:
        controls = self.strategy_cube.current.societal.normalised()
        bee_count = self.config.bee_count

        scout_count = int(bee_count * controls.scout_ratio)
        worker_count = int(bee_count * controls.worker_ratio)
        guard_count = int(bee_count * controls.guard_ratio)
        reserve_count = max(0, bee_count - scout_count - worker_count - guard_count)

        roles: list[BeeRole] = (
            [BeeRole.SCOUT] * scout_count
            + [BeeRole.WORKER] * worker_count
            + [BeeRole.GUARD] * guard_count
            + [BeeRole.RESERVE] * reserve_count
        )

        random.shuffle(roles)

        bees: list[Bee] = []

        for i, role in enumerate(roles):
            offset = pygame.Vector2(random.uniform(-18, 18), random.uniform(-18, 18))
            bees.append(
                Bee(
                    id=f"bee-{i}",
                    role=role,
                    position=self.hive_position + offset,
                    velocity=pygame.Vector2(0, 0),
                    energy=random.uniform(0.72, 1.0),
                    memory={
                        "visits": 0,
                        "pollination_events": 0,
                        "cross_pollination_events": 0,
                    },
                )
            )

        return bees

    def step(self) -> None:
        self.iteration += 1

        for threat in self.threats:
            threat.step(self.field_rect)

        for bee in self.bees:
            self._step_bee(bee)

        self._decay_memory()

    def _step_bee(self, bee: Bee) -> None:
        if bee.energy <= 0.08:
            self._move_towards(bee, self.hive_position, speed=1.2)
            bee.energy = clamp(bee.energy + 0.010)
            return

        if bee.role == BeeRole.SCOUT:
            self._scout_behaviour(bee)
        elif bee.role == BeeRole.WORKER:
            self._worker_behaviour(bee)
        elif bee.role == BeeRole.GUARD:
            self._guard_behaviour(bee)
        elif bee.role == BeeRole.RESERVE:
            self._reserve_behaviour(bee)

        self._apply_threat_pressure(bee)
        self._apply_bounds(bee)
        self._try_harvest_and_pollinate(bee)

        movement_cost = bee.velocity.length() * 0.0006
        bee.energy = clamp(bee.energy - movement_cost + 0.0004)

    def _scout_behaviour(self, bee: Bee) -> None:
        doctrine = self.strategy_cube.current
        controls = doctrine.societal
        janus = doctrine.janus

        if random.random() < 0.015 * doctrine.cort60.challenge:
            bee.target_patch_id = None

        nearby = self._nearest_resource(bee.position, include_depleted=False)

        if nearby and distance(bee.position, nearby.position) < nearby.radius * 2.0:
            self._register_patch_discovery(nearby)
            if random.random() < 0.65:
                bee.target_patch_id = nearby.id

        if bee.target_patch_id:
            patch = self._patch_by_id(bee.target_patch_id)
            if patch and not patch.depleted:
                self._move_towards(
                    bee,
                    patch.position,
                    speed=2.2 + 2.0 * janus.left_exploration_bias,
                    noise=controls.individual_variance,
                )
                return

        if random.random() < 0.05 * controls.pollination_bias:
            cross_patch = self._select_cross_pollination_candidate(bee)
            if cross_patch:
                bee.target_patch_id = cross_patch.id
                self._move_towards(bee, cross_patch.position, speed=2.4, noise=controls.individual_variance)
                return

        self._wander(bee, speed=1.7 + 2.4 * janus.left_exploration_bias, noise=controls.individual_variance)

    def _worker_behaviour(self, bee: Bee) -> None:
        doctrine = self.strategy_cube.current
        controls = doctrine.societal
        janus = doctrine.janus

        best_patch_id = self.colony_memory.get("best_patch_id")
        social_signal = self.colony_memory.get("social_signal", 0.0)

        if best_patch_id and random.random() < controls.recruitment_pressure + social_signal * 0.25:
            patch = self._patch_by_id(best_patch_id)
            if patch and not patch.depleted:
                bee.target_patch_id = patch.id
                self._move_towards(
                    bee,
                    patch.position,
                    speed=2.0 + 3.0 * janus.right_exploitation_bias,
                    noise=0.2 + controls.individual_variance * 0.25,
                )
                return

        known = list(self.colony_memory["known_patches"].keys())
        if known and random.random() < controls.social_signal_strength:
            patch_id = random.choice(known)
            patch = self._patch_by_id(patch_id)
            if patch and not patch.depleted:
                bee.target_patch_id = patch.id
                self._move_towards(bee, patch.position, speed=2.0, noise=controls.individual_variance * 0.5)
                return

        self._wander(bee, speed=1.2, noise=controls.individual_variance * 0.6)

    def _guard_behaviour(self, bee: Bee) -> None:
        threat = self._nearest_threat(bee.position)

        if threat and distance(bee.position, threat.position) < 180:
            self._move_towards(bee, threat.position, speed=2.4, noise=0.20)

            if distance(bee.position, threat.position) < threat.radius + 8:
                threat.velocity.rotate_ip(random.uniform(90, 180))
                threat.position += threat.velocity * 8
                bee.score += 0.25
            return

        patrol_target = self.hive_position + pygame.Vector2(
            math.cos(self.iteration * 0.018 + hash(bee.id) % 10) * 80,
            math.sin(self.iteration * 0.018 + hash(bee.id) % 10) * 80,
        )
        self._move_towards(bee, patrol_target, speed=1.6, noise=0.25)

    def _reserve_behaviour(self, bee: Bee) -> None:
        doctrine = self.strategy_cube.current
        controls = doctrine.societal

        threat = self._nearest_threat(self.hive_position)
        high_threat = threat is not None and distance(threat.position, self.hive_position) < 160

        if high_threat and random.random() < 0.6:
            self._guard_behaviour(bee)
            return

        if self.colony_memory.get("social_signal", 0.0) > 0.65 and random.random() < controls.recruitment_pressure:
            self._worker_behaviour(bee)
            return

        rest_target = self.hive_position + pygame.Vector2(random.uniform(-35, 35), random.uniform(-35, 35))
        self._move_towards(bee, rest_target, speed=0.7, noise=0.1)
        bee.energy = clamp(bee.energy + 0.0025)

    def _register_patch_discovery(self, patch: ResourcePatch) -> None:
        value = self._patch_value(patch)
        known = self.colony_memory["known_patches"]
        known[patch.id] = {
            "value": value,
            "crop": patch.crop,
            "last_seen": self.iteration,
        }

        if value > self.colony_memory["best_patch_quality"]:
            self.colony_memory["best_patch_quality"] = value
            self.colony_memory["best_patch_id"] = patch.id
            self.colony_memory["social_signal"] = clamp(self.colony_memory["social_signal"] + 0.25)

    def _patch_value(self, patch: ResourcePatch) -> float:
        crop_profile = CROP_PROFILES[patch.crop]
        return (
            0.35 * patch.quality
            + 0.20 * normalise(patch.nectar, 180)
            + 0.15 * patch.bloom_strength
            + 0.15 * crop_profile.insect_pollination_dependency
            + 0.15 * crop_profile.cross_pollination_need
        )

    def _try_harvest_and_pollinate(self, bee: Bee) -> None:
        for patch in self.resources:
            if patch.depleted:
                continue

            if distance(bee.position, patch.position) <= patch.radius:
                harvest_amount = 0.15 if bee.role == BeeRole.SCOUT else 0.55
                if bee.role == BeeRole.WORKER:
                    harvest_amount += 0.35 * self.strategy_cube.current.societal.recruitment_pressure

                collected = patch.harvest(harvest_amount)
                if collected > 0:
                    bee.score += collected
                    self.total_collected += collected
                    bee.memory["visits"] = bee.memory.get("visits", 0) + 1
                    self.pollination_events += 1
                    bee.memory["pollination_events"] = bee.memory.get("pollination_events", 0) + 1
                    self._register_patch_discovery(patch)

                    if bee.last_patch_id and bee.last_patch_id != patch.id:
                        previous = self._patch_by_id(bee.last_patch_id)
                        if previous and previous.crop != patch.crop:
                            crop_profile = CROP_PROFILES[patch.crop]
                            previous_profile = CROP_PROFILES[previous.crop]
                            cross_value = (
                                crop_profile.cross_pollination_need
                                + previous_profile.cross_pollination_need
                            ) * 0.5

                            if random.random() < cross_value:
                                patch.cross_pollination_visits += 1
                                self.cross_pollination_events += 1
                                bee.memory["cross_pollination_events"] = (
                                    bee.memory.get("cross_pollination_events", 0) + 1
                                )
                                bee.score += 0.40 * cross_value

                    bee.last_patch_id = patch.id
                return

    def _apply_threat_pressure(self, bee: Bee) -> None:
        doctrine = self.strategy_cube.current
        nearest = self._nearest_threat(bee.position)

        if nearest is None:
            return

        d = distance(bee.position, nearest.position)

        if d < nearest.radius:
            damage = nearest.pressure * (1.0 - doctrine.societal.risk_tolerance) * 0.025
            bee.energy = clamp(bee.energy - damage)
            bee.score -= damage * 4
            self.threat_hits += 1

            if bee.role not in {BeeRole.GUARD, BeeRole.RESERVE}:
                flee = bee.position - nearest.position
                if flee.length_squared() > 0:
                    flee = flee.normalize()
                    bee.velocity += flee * 3.0

    def _decay_memory(self) -> None:
        doctrine = self.strategy_cube.current
        memory_trust = doctrine.janus.memory_trust
        self.colony_memory["social_signal"] *= 0.995 + 0.004 * memory_trust

        known = self.colony_memory["known_patches"]
        for patch_id in list(known.keys()):
            age = self.iteration - known[patch_id]["last_seen"]
            if age > 900:
                del known[patch_id]

    def _select_cross_pollination_candidate(self, bee: Bee) -> ResourcePatch | None:
        if not bee.last_patch_id:
            return None

        previous = self._patch_by_id(bee.last_patch_id)
        if previous is None:
            return None

        candidates = [
            patch
            for patch in self.resources
            if not patch.depleted
            and patch.id != previous.id
            and patch.crop != previous.crop
        ]

        if not candidates:
            return None

        candidates.sort(
            key=lambda patch: CROP_PROFILES[patch.crop].cross_pollination_need * patch.bloom_strength,
            reverse=True,
        )
        return candidates[0]

    def _nearest_resource(self, pos: pygame.Vector2, include_depleted: bool = False) -> ResourcePatch | None:
        candidates = [r for r in self.resources if include_depleted or not r.depleted]
        if not candidates:
            return None
        return min(candidates, key=lambda r: distance(pos, r.position))

    def _nearest_threat(self, pos: pygame.Vector2) -> Threat | None:
        if not self.threats:
            return None
        return min(self.threats, key=lambda t: distance(pos, t.position))

    def _patch_by_id(self, patch_id: str | None) -> ResourcePatch | None:
        if not patch_id:
            return None
        for patch in self.resources:
            if patch.id == patch_id:
                return patch
        return None

    def _move_towards(self, bee: Bee, target: pygame.Vector2, speed: float, noise: float = 0.0) -> None:
        direction = target - bee.position

        if direction.length_squared() > 0:
            direction = direction.normalize()
        else:
            direction = pygame.Vector2(0, 0)

        if noise > 0:
            direction += pygame.Vector2(random.uniform(-noise, noise), random.uniform(-noise, noise))
            if direction.length_squared() > 0:
                direction = direction.normalize()

        bee.velocity = bee.velocity.lerp(direction * speed, 0.35)
        bee.position += bee.velocity

    def _wander(self, bee: Bee, speed: float, noise: float = 0.5) -> None:
        if random.random() < 0.10 + noise * 0.08 or bee.velocity.length_squared() < 0.01:
            angle = random.uniform(0, math.tau)
            bee.velocity += pygame.Vector2(math.cos(angle), math.sin(angle)) * speed

        if bee.velocity.length() > speed:
            bee.velocity.scale_to_length(speed)

        bee.position += bee.velocity

    def _apply_bounds(self, bee: Bee) -> None:
        margin = 10
        if bee.position.x < margin or bee.position.x > self.config.width - margin:
            bee.velocity.x *= -0.8
        if bee.position.y < margin or bee.position.y > self.config.height - margin:
            bee.velocity.y *= -0.8

        bee.position.x = max(margin, min(self.config.width - margin, bee.position.x))
        bee.position.y = max(margin, min(self.config.height - margin, bee.position.y))

    def metrics(self) -> dict[str, float]:
        scores = [bee.score for bee in self.bees]
        energies = [bee.energy for bee in self.bees]
        positions = [bee.position for bee in self.bees]

        scout_count = sum(1 for b in self.bees if b.role == BeeRole.SCOUT)
        worker_count = sum(1 for b in self.bees if b.role == BeeRole.WORKER)
        guard_count = sum(1 for b in self.bees if b.role == BeeRole.GUARD)
        reserve_count = sum(1 for b in self.bees if b.role == BeeRole.RESERVE)

        known_patch_ratio = normalise(len(self.colony_memory["known_patches"]), max(1, len(self.resources)))

        if positions:
            xs = [p.x for p in positions]
            ys = [p.y for p in positions]
            diversity = clamp(((max(xs) - min(xs)) + (max(ys) - min(ys))) / (self.config.width + self.config.height))
        else:
            diversity = 0.0

        total_nectar_possible = self.config.resource_count * 180
        exploitation_score = clamp(self.total_collected / max(1.0, total_nectar_possible * 0.35))
        exploration_score = clamp(0.45 * known_patch_ratio + 0.35 * diversity + 0.20 * (scout_count / len(self.bees)))

        social_memory_score = clamp(self.colony_memory["social_signal"])
        convergence_score = clamp(0.55 * exploitation_score + 0.45 * (1.0 - diversity))
        reserve_resilience = reserve_count / max(1, len(self.bees))
        pollination_score = clamp(self.pollination_events / max(1, self.iteration * len(self.bees) * 0.08))
        cross_pollination_score = clamp(self.cross_pollination_events / max(1, self.pollination_events * 0.25))

        environmental_benefit = self._environmental_benefit_score()
        human_benefit = self._human_benefit_score()

        threat_pressure = clamp(self.threat_hits / max(1, self.iteration * len(self.bees) * 0.03))
        energy_health = safe_mean(energies)

        strategic_balance = 1.0 - clamp(abs(exploration_score - exploitation_score))
        premature_convergence_risk = clamp(convergence_score * (1.0 - diversity) * (1.0 - reserve_resilience * 0.5))

        return {
            "iteration": float(self.iteration),
            "bee_count": float(len(self.bees)),
            "scout_count": float(scout_count),
            "worker_count": float(worker_count),
            "guard_count": float(guard_count),
            "reserve_count": float(reserve_count),
            "best_score": max(scores) if scores else 0.0,
            "average_score": safe_mean(scores),
            "total_collected": self.total_collected,
            "known_patch_ratio": known_patch_ratio,
            "diversity_score": diversity,
            "exploration_score": exploration_score,
            "exploitation_score": exploitation_score,
            "convergence_score": convergence_score,
            "social_memory_score": social_memory_score,
            "reserve_resilience": reserve_resilience,
            "pollination_score": pollination_score,
            "cross_pollination_score": cross_pollination_score,
            "environmental_benefit": environmental_benefit,
            "human_benefit": human_benefit,
            "threat_pressure": threat_pressure,
            "energy_health": energy_health,
            "strategic_balance": strategic_balance,
            "premature_convergence_risk": premature_convergence_risk,
            "pollination_events": float(self.pollination_events),
            "cross_pollination_events": float(self.cross_pollination_events),
            "threat_hits": float(self.threat_hits),
        }

    def _environmental_benefit_score(self) -> float:
        if not self.resources:
            return 0.0

        total = 0.0
        for patch in self.resources:
            crop = CROP_PROFILES[patch.crop]
            visit_factor = normalise(patch.visits, 30)
            cross_factor = normalise(patch.cross_pollination_visits, 10)
            total += crop.environmental_value * (0.6 * visit_factor + 0.4 * cross_factor)

        return clamp(total / len(self.resources))

    def _human_benefit_score(self) -> float:
        if not self.resources:
            return 0.0

        total = 0.0
        for patch in self.resources:
            crop = CROP_PROFILES[patch.crop]
            visit_factor = normalise(patch.visits, 30)
            total += crop.human_food_value * crop.insect_pollination_dependency * visit_factor

        return clamp(total / len(self.resources))

    def frame(self) -> dict[str, Any]:
        metrics = self.metrics()
        janus = self.janus_encoder.encode(metrics)
        cort60 = self.cort60.explain(metrics, self.strategy_cube.current)

        return {
            "simulation": {
                "name": "Janus CoRT60 Bee Colony Optimisation",
                "iteration": self.iteration,
                "species": asdict(self.species),
                "strategy": self.strategy_cube.as_dict(),
            },
            "metrics": metrics,
            "janus": janus,
            "cort60": cort60,
            "colony_memory": self.colony_memory,
            "bees": [bee.as_dict() for bee in self.bees],
            "resources": [patch.as_dict() for patch in self.resources],
            "threats": [threat.as_dict() for threat in self.threats],
            "metadata": {
                "bee_species": {key: asdict(value) for key, value in BEE_METADATA.items()},
                "crop_profiles": {key: asdict(value) for key, value in CROP_PROFILES.items()},
            },
        }

    def export_state(self) -> Path:
        export_dir = Path(self.config.export_dir)
        export_dir.mkdir(parents=True, exist_ok=True)

        filename = f"bco_janus_state_{int(time.time())}.json"
        path = export_dir / filename

        with path.open("w", encoding="utf-8") as f:
            json.dump(self.frame(), f, indent=2)

        return path


# ============================================================
# Pygame Dashboard
# ============================================================

class Dashboard:
    ROLE_COLOURS = {
        BeeRole.SCOUT: (242, 201, 76),
        BeeRole.WORKER: (47, 128, 237),
        BeeRole.GUARD: (235, 87, 87),
        BeeRole.RESERVE: (130, 130, 130),
    }

    CROP_COLOURS = {
        "apple": (255, 120, 140),
        "almond": (240, 210, 165),
        "clover": (110, 210, 130),
        "wildflower": (250, 210, 80),
        "tomato": (230, 80, 60),
    }

    def __init__(self, simulation: BeeColonyOptimisation) -> None:
        self.sim = simulation
        self.config = simulation.config

        pygame.init()
        pygame.display.set_caption("Janus CoRT60 Bee Colony Optimisation")

        self.screen = pygame.display.set_mode(
            (self.config.width + self.config.panel_width, self.config.height)
        )
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("consolas", 15)
        self.small = pygame.font.SysFont("consolas", 12)
        self.large = pygame.font.SysFont("consolas", 21, bold=True)

        self.running = True
        self.paused = False
        self.show_help = True
        self.steps_per_frame = 1
        self.last_export_message = ""

    def run(self) -> None:
        while self.running:
            self._handle_events()

            if not self.paused:
                for _ in range(self.steps_per_frame):
                    self.sim.step()

            self._draw()
            self.clock.tick(60)

        pygame.quit()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self.sim.reset()
                elif event.key == pygame.K_1:
                    self.sim.strategy_cube.set_preset("explorer")
                    self.sim.reset()
                elif event.key == pygame.K_2:
                    self.sim.strategy_cube.set_preset("exploiter")
                    self.sim.reset()
                elif event.key == pygame.K_3:
                    self.sim.strategy_cube.set_preset("balanced")
                    self.sim.reset()
                elif event.key == pygame.K_4:
                    self.sim.strategy_cube.set_preset("pollination")
                    self.sim.reset()
                elif event.key == pygame.K_e:
                    path = self.sim.export_state()
                    self.last_export_message = f"Exported: {path}"
                elif event.key == pygame.K_h:
                    self.show_help = not self.show_help
                elif event.key == pygame.K_UP:
                    self.steps_per_frame = min(30, self.steps_per_frame + 1)
                elif event.key == pygame.K_DOWN:
                    self.steps_per_frame = max(1, self.steps_per_frame - 1)

    def _draw(self) -> None:
        self.screen.fill((244, 247, 250))
        self._draw_field()
        self._draw_resources()
        self._draw_threats()
        self._draw_hive()
        self._draw_bees()
        self._draw_panel()

        if self.show_help:
            self._draw_help()

        pygame.display.flip()

    def _draw_field(self) -> None:
        field = pygame.Rect(0, 0, self.config.width, self.config.height)
        pygame.draw.rect(self.screen, (238, 252, 236), field)
        pygame.draw.rect(self.screen, (180, 205, 185), field, 2)

        for x in range(0, self.config.width, 60):
            pygame.draw.line(self.screen, (225, 240, 225), (x, 0), (x, self.config.height), 1)
        for y in range(0, self.config.height, 60):
            pygame.draw.line(self.screen, (225, 240, 225), (0, y), (self.config.width, y), 1)

    def _draw_resources(self) -> None:
        best_patch_id = self.sim.colony_memory.get("best_patch_id")

        for patch in self.sim.resources:
            colour = self.CROP_COLOURS.get(patch.crop, (80, 180, 90))
            alpha_factor = 0.35 if patch.depleted else 1.0

            base = tuple(int(c * alpha_factor) for c in colour)
            radius = int(patch.radius)

            pygame.draw.circle(self.screen, base, patch.position, radius)
            pygame.draw.circle(self.screen, (40, 90, 50), patch.position, radius, 2)

            label = f"{patch.crop[:3]} {patch.quality:.2f}"
            self._text(label, patch.position.x - radius, patch.position.y - radius - 14, self.small, (30, 60, 40))

            if patch.id == best_patch_id:
                pygame.draw.circle(self.screen, (235, 87, 87), patch.position, radius + 8, 3)
                self._text("★", patch.position.x - 6, patch.position.y - 10, self.large, (235, 87, 87))

            if patch.cross_pollination_visits > 0:
                self._text(
                    f"x{patch.cross_pollination_visits}",
                    patch.position.x + radius - 10,
                    patch.position.y + radius - 8,
                    self.small,
                    (80, 40, 120),
                )

    def _draw_threats(self) -> None:
        for threat in self.sim.threats:
            pygame.draw.circle(self.screen, (190, 40, 40), threat.position, int(threat.radius), 2)
            pygame.draw.circle(self.screen, (230, 90, 90), threat.position, 8)
            self._text(threat.label[:3], threat.position.x + 10, threat.position.y - 8, self.small, (100, 20, 20))

    def _draw_hive(self) -> None:
        pos = self.sim.hive_position
        pygame.draw.circle(self.screen, (180, 120, 30), pos, 34)
        pygame.draw.circle(self.screen, (90, 60, 20), pos, 34, 3)
        self._text("HIVE", pos.x - 21, pos.y - 8, self.font, (255, 245, 210))

    def _draw_bees(self) -> None:
        for bee in self.sim.bees:
            colour = self.ROLE_COLOURS[bee.role]
            pos = bee.position

            if bee.velocity.length_squared() > 0.01:
                direction = bee.velocity.normalize()
            else:
                direction = pygame.Vector2(1, 0)

            angle = math.atan2(direction.y, direction.x)

            self._draw_bee_body(pos, angle, colour, bee.role)

    def _draw_bee_body(self, pos: pygame.Vector2, angle: float, colour: tuple[int, int, int], role: BeeRole) -> None:
        wing_colour = (255, 255, 255)
        dark = (25, 25, 25)

        wing_offset_left = pygame.Vector2(-3, -7).rotate_rad(angle)
        wing_offset_right = pygame.Vector2(3, -7).rotate_rad(angle)

        pygame.draw.ellipse(
            self.screen,
            wing_colour,
            pygame.Rect(pos.x + wing_offset_left.x - 5, pos.y + wing_offset_left.y - 3, 10, 6),
        )
        pygame.draw.ellipse(
            self.screen,
            wing_colour,
            pygame.Rect(pos.x + wing_offset_right.x - 5, pos.y + wing_offset_right.y - 3, 10, 6),
        )

        pygame.draw.circle(self.screen, colour, pos, 6)
        pygame.draw.circle(self.screen, dark, pos, 6, 1)

        stripe_a = pos + pygame.Vector2(-2, 0).rotate_rad(angle)
        stripe_b = pos + pygame.Vector2(2, 0).rotate_rad(angle)
        pygame.draw.line(self.screen, dark, (stripe_a.x, stripe_a.y - 4), (stripe_a.x, stripe_a.y + 4), 1)
        pygame.draw.line(self.screen, dark, (stripe_b.x, stripe_b.y - 4), (stripe_b.x, stripe_b.y + 4), 1)

        if role == BeeRole.GUARD:
            pygame.draw.circle(self.screen, (255, 255, 255), pos, 9, 1)
        elif role == BeeRole.RESERVE:
            pygame.draw.circle(self.screen, (70, 70, 70), pos, 8, 1)

    def _draw_panel(self) -> None:
        panel_x = self.config.width
        panel = pygame.Rect(panel_x, 0, self.config.panel_width, self.config.height)
        pygame.draw.rect(self.screen, (23, 32, 51), panel)

        frame = self.sim.frame()
        metrics = frame["metrics"]
        janus = frame["janus"]
        cort60 = frame["cort60"]
        strategy = frame["simulation"]["strategy"]

        y = 16
        y = self._panel_title("Janus CoRT60 BCO", y)
        y = self._panel_line(f"Doctrine: {strategy['label']}", y)
        y = self._panel_line(f"Species: {frame['simulation']['species']['common_name']}", y)
        y = self._panel_line(f"Iter: {int(metrics['iteration'])} | Speed: {self.steps_per_frame}", y)
        y += 8

        y = self._panel_title("Core Metrics", y)
        metric_keys = [
            ("Best", "best_score"),
            ("Avg", "average_score"),
            ("Collected", "total_collected"),
            ("Explore", "exploration_score"),
            ("Exploit", "exploitation_score"),
            ("Converge", "convergence_score"),
            ("Diversity", "diversity_score"),
            ("Pollination", "pollination_score"),
            ("Cross-Poll", "cross_pollination_score"),
            ("Env Benefit", "environmental_benefit"),
            ("Human Benefit", "human_benefit"),
            ("Threat", "threat_pressure"),
            ("Energy", "energy_health"),
            ("Risk", "premature_convergence_risk"),
        ]

        for label, key in metric_keys:
            y = self._panel_bar(label, metrics[key], y)

        y += 8
        y = self._panel_title("Janus State", y)
        y = self._panel_line(f"Mode: {janus['mode']}", y)
        y = self._panel_line(f"64-bit: {janus['signature64'][:24]}...", y)
        y += 8

        y = self._panel_title("Roles", y)
        y = self._panel_line(
            f"S:{int(metrics['scout_count'])} "
            f"W:{int(metrics['worker_count'])} "
            f"G:{int(metrics['guard_count'])} "
            f"R:{int(metrics['reserve_count'])}",
            y,
        )
        y += 8

        y = self._panel_title("CoRT60 Challenge", y)
        y = self._panel_wrap(cort60["Challenge"], y, width=42)

        if self.last_export_message:
            y += 8
            y = self._panel_wrap(self.last_export_message, y, width=42, colour=(170, 230, 170))

    def _draw_help(self) -> None:
        lines = [
            "SPACE pause/resume | R reset | 1 Explorer | 2 Exploiter | 3 Balanced | 4 Pollination",
            "E export JSON | H hide help | UP/DOWN sim speed",
        ]

        rect = pygame.Rect(16, self.config.height - 58, self.config.width - 32, 44)
        pygame.draw.rect(self.screen, (255, 255, 255), rect)
        pygame.draw.rect(self.screen, (120, 140, 160), rect, 1)

        y = rect.y + 8
        for line in lines:
            self._text(line, rect.x + 10, y, self.small, (20, 30, 45))
            y += 17

    def _panel_title(self, text: str, y: int) -> int:
        self._text(text, self.config.width + 16, y, self.large, (255, 255, 255))
        return y + 28

    def _panel_line(self, text: str, y: int, colour: tuple[int, int, int] = (220, 230, 245)) -> int:
        self._text(text, self.config.width + 16, y, self.font, colour)
        return y + 20

    def _panel_wrap(
        self,
        text: str,
        y: int,
        width: int = 40,
        colour: tuple[int, int, int] = (220, 230, 245),
    ) -> int:
        words = text.split()
        line = ""

        for word in words:
            candidate = f"{line} {word}".strip()
            if len(candidate) > width:
                y = self._panel_line(line, y, colour)
                line = word
            else:
                line = candidate

        if line:
            y = self._panel_line(line, y, colour)

        return y

    def _panel_bar(self, label: str, value: float, y: int) -> int:
        x = self.config.width + 16
        bar_x = self.config.width + 128
        bar_y = y + 4
        bar_w = 220
        bar_h = 10

        self._text(label, x, y, self.small, (220, 230, 245))

        pygame.draw.rect(self.screen, (55, 65, 85), pygame.Rect(bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(
            self.screen,
            (90, 180, 255),
            pygame.Rect(bar_x, bar_y, int(bar_w * clamp(value)), bar_h),
        )
        pygame.draw.rect(self.screen, (120, 140, 160), pygame.Rect(bar_x, bar_y, bar_w, bar_h), 1)

        self._text(f"{value:.2f}", bar_x + bar_w + 8, y, self.small, (220, 230, 245))
        return y + 18

    def _text(
        self,
        text: str,
        x: float,
        y: float,
        font: pygame.font.Font,
        colour: tuple[int, int, int],
    ) -> None:
        surface = font.render(str(text), True, colour)
        self.screen.blit(surface, (int(x), int(y)))


# ============================================================
# Entry Point
# ============================================================

def main() -> None:
    config = SimulationConfig()
    strategy_cube = StrategyCube()
    simulation = BeeColonyOptimisation(config=config, strategy_cube=strategy_cube)
    dashboard = Dashboard(simulation)
    dashboard.run()


if __name__ == "__main__":
    main()

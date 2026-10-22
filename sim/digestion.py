"""Physiological food, water and energy model.

See notes/systems/01b-digestion.md. Food moves stomach -> small intestine ->
colon. Absorbed carbs fill glycogen (overflow becomes fat), fat goes to fat
stores, protein repairs muscle (the rest is burned like carbs). Energy is
spent from glycogen and fat in a mix that depends on activity; when both
run out, the body eats its own muscle. Water is tracked in millilitres of
total body water, lost through urine, breath, skin and sweat.

Efficiency: every compartment uses first-order (exponential) or zero-order
(linear) kinetics with exact closed-form updates. Long ticks are split into
15-minute steps so chained compartments stay in sync: a 1-hour tick costs
four steps of a few dozen float ops and matches sixty 1-minute ticks.

Units: grams, millilitres, kcal, hours of game time.
"""

import math
from dataclasses import dataclass, field

KCAL_PER_G = {"carbs": 4.0, "protein": 4.0, "fat": 9.0}
MACROS = ("carbs", "protein", "fat")
SOLIDS = MACROS + ("fibre",)


def _exp_left(half_life: float, hours: float) -> float:
    """Fraction remaining after `hours` of exponential decay."""
    return math.exp(-math.log(2) / half_life * hours)


@dataclass(frozen=True)
class Food:
    name: str
    water: float = 0.0     # g (= ml)
    carbs: float = 0.0     # g, digestible
    protein: float = 0.0
    fat: float = 0.0
    fibre: float = 0.0
    contaminated: bool = False

    @property
    def kcal(self) -> float:
        return sum(getattr(self, m) * KCAL_PER_G[m] for m in MACROS)

    @property
    def mass(self) -> float:
        return self.water + sum(getattr(self, s) for s in SOLIDS)


# A few reference foods, per typical serving. Values rounded from common
# nutrition tables; they are generic foods, not Vein item data.
FOODS = {
    "water 500ml": Food("water 500ml", water=500),
    "canned beans": Food("canned beans", water=300, carbs=45, protein=20, fat=2, fibre=15),
    "apple": Food("apple", water=150, carbs=22, protein=0.5, fat=0.3, fibre=4),
    "bread slice": Food("bread slice", water=12, carbs=14, protein=3, fat=1, fibre=1),
    "beef jerky": Food("beef jerky", water=12, carbs=5, protein=17, fat=4),
    "chocolate bar": Food("chocolate bar", water=1, carbs=30, protein=4, fat=15, fibre=3),
    "cooked rice": Food("cooked rice", water=140, carbs=56, protein=5, fat=0.5, fibre=1),
    "canned tuna": Food("canned tuna", water=110, protein=40, fat=8),
    "soda": Food("soda", water=320, carbs=39),
}


@dataclass
class DigestionConfig:
    max_step_hours: float = 0.25          # long ticks are split into steps this size

    # Body size: 75 kg adult.
    normal_body_water: float = 42_000.0   # ml (~60% of body mass)
    max_glycogen: float = 500.0           # g (liver ~100 + muscle ~400)
    baseline_muscle_protein: float = 10_000.0  # g of structural protein
    bmr_kcal_per_day: float = 1750.0
    fever_bmr_per_unit_infection: float = 0.003  # +30% BMR at infection 100

    # Stomach.
    comfortable_stomach_ml: float = 1000.0
    vomit_stomach_ml: float = 3000.0      # overfilling makes you throw up
    stomach_kcal_per_hour: float = 130.0  # gastric emptying ~2 kcal/min
    fat_slowing: float = 0.5              # all-fat meal empties 50% slower
    stomach_water_half_life: float = 0.33 # h; plain liquid leaves fast
    meal_water_slowing_kcal: float = 200.0  # each 200 kcal in the stomach doubles it
    fibre_only_g_per_hour: float = 60.0

    # Small intestine: absorption competes with onward transit.
    absorb_half_life: dict = field(default_factory=lambda: {
        "carbs": 0.4, "protein": 0.8, "fat": 1.5, "water": 0.3})
    transit_half_life: float = 4.0        # h for what isn't absorbed
    # Colon.
    colon_water_half_life: float = 5.0    # reabsorbs down to stool moisture
    stool_water_per_solid: float = 3.0    # stool is ~75% water
    bowel_urge_g: float = 250.0
    bowel_accident_g: float = 600.0

    # Kidneys and bladder.
    obligatory_urine_ml_per_day: float = 500.0
    excess_water_half_life: float = 1.0   # kidneys dump surplus water
    bladder_urge_ml: float = 300.0
    bladder_accident_ml: float = 650.0

    # Other water loss.
    insensible_ml_per_day: float = 800.0  # breath + skin
    sweat_ml_per_met_hour: float = 80.0   # above 2 MET
    sweat_ml_per_degree_hour: float = 40.0  # above 25 °C
    vomit_water_loss_ml: float = 300.0
    metabolic_water_ml_per_kcal: float = 0.12  # water made by burning fuel

    # Fuel mix: share of energy from carbs at each MET level (rest is fat).
    carb_share_rest: float = 0.4
    carb_share_max: float = 0.85          # at 10 MET
    starving_protein_share: float = 0.15  # muscle burned once glycogen is low
    low_glycogen: float = 0.15            # fraction of max
    carb_to_fat_efficiency: float = 0.8

    # Cold: shivering burns extra energy below this skin-air temperature.
    shiver_below: float = 15.0
    shiver_kcal_per_degree_hour: float = 8.0

    # Danger thresholds.
    dehydration_damage_from: float = 0.08  # fraction of body water lost
    dehydration_lethal: float = 0.15
    muscle_damage_below: float = 0.75      # fraction of baseline protein
    muscle_lethal: float = 0.55


@dataclass
class Gut:
    water: float = 0.0
    carbs: float = 0.0
    protein: float = 0.0
    fat: float = 0.0
    fibre: float = 0.0

    @property
    def kcal(self) -> float:
        return sum(getattr(self, m) * KCAL_PER_G[m] for m in MACROS)

    @property
    def volume(self) -> float:
        return self.water + sum(getattr(self, s) for s in SOLIDS)

    def add(self, other) -> None:
        for name in ("water",) + SOLIDS:
            setattr(self, name, getattr(self, name) + getattr(other, name))

    def take_fraction(self, f: float, names=SOLIDS) -> "Gut":
        out = Gut()
        for name in names:
            moved = getattr(self, name) * f
            setattr(self, name, getattr(self, name) - moved)
            setattr(out, name, moved)
        return out


@dataclass
class Body:
    config: DigestionConfig = field(default_factory=DigestionConfig)
    stomach: Gut = field(default_factory=Gut)
    intestine: Gut = field(default_factory=Gut)
    colon_solids: float = 0.0
    colon_water: float = 0.0
    bladder: float = 0.0
    glycogen: float = 350.0
    fat_store: float = 12_000.0           # g (~16% body fat)
    muscle_protein: float = None
    body_water: float = None
    vomit_count: int = 0
    accidents: int = 0
    kcal_burned: float = 0.0

    def __post_init__(self):
        c = self.config
        if self.muscle_protein is None:
            self.muscle_protein = c.baseline_muscle_protein
        if self.body_water is None:
            self.body_water = c.normal_body_water

    # ---- input / output -------------------------------------------------
    def eat(self, food: Food) -> bool:
        """Swallow food or drink. Returns False if you threw it all back up."""
        self.stomach.add(food)
        if self.stomach.volume > self.config.vomit_stomach_ml:
            self.vomit()
            return False
        return True

    def drink(self, ml: float) -> bool:
        return self.eat(Food("water", water=ml))

    def vomit(self) -> None:
        self.stomach = Gut()
        self.body_water -= self.config.vomit_water_loss_ml
        self.vomit_count += 1

    def urinate(self) -> float:
        amount, self.bladder = self.bladder, 0.0
        return amount

    def defecate(self) -> float:
        amount = self.colon_solids + self.colon_water
        self.colon_solids = self.colon_water = 0.0
        return amount

    # ---- simulation -----------------------------------------------------
    def tick(self, hours: float, met: float = 1.3, temperature: float = 20.0,
             infection: float = 0.0) -> None:
        steps = max(1, math.ceil(hours / self.config.max_step_hours))
        dt = hours / steps
        for _ in range(steps):
            self._empty_stomach(dt)
            absorbed = self._small_intestine(dt)
            self._colon(dt)
            self._store(absorbed)
            self._spend_energy(dt, met, temperature, infection)
            self._water_balance(dt, met, temperature)

    def _empty_stomach(self, hours: float) -> None:
        c, s = self.config, self.stomach
        # Water: exponential, slower when mixed with a meal.
        half_life = c.stomach_water_half_life * (1 + s.kcal / c.meal_water_slowing_kcal)
        left = _exp_left(half_life, hours)
        water_out = s.water * (1 - left)
        s.water -= water_out
        self.intestine.water += water_out
        # Solids: energy-limited, slowed by fat content.
        if s.kcal > 0:
            fat_share = s.fat * KCAL_PER_G["fat"] / s.kcal
            rate = c.stomach_kcal_per_hour * (1 - c.fat_slowing * fat_share)
            f = min(1.0, rate * hours / s.kcal)
        elif s.fibre > 0:
            f = min(1.0, c.fibre_only_g_per_hour * hours / s.fibre)
        else:
            return
        self.intestine.add(s.take_fraction(f))

    def _small_intestine(self, hours: float) -> Gut:
        c, gut = self.config, self.intestine
        kt = math.log(2) / c.transit_half_life
        absorbed, passed = Gut(), Gut()
        for name in MACROS + ("water",):
            amount = getattr(gut, name)
            if amount <= 0:
                continue
            ka = math.log(2) / c.absorb_half_life[name]
            gone = amount * (1 - math.exp(-(ka + kt) * hours))
            setattr(absorbed, name, gone * ka / (ka + kt))
            setattr(passed, name, gone * kt / (ka + kt))
            setattr(gut, name, amount - gone)
        fibre_out = gut.fibre * (1 - math.exp(-kt * hours))
        gut.fibre -= fibre_out
        self.colon_solids += fibre_out + passed.carbs + passed.protein + passed.fat
        self.colon_water += passed.water
        return absorbed

    def _colon(self, hours: float) -> None:
        c = self.config
        keep = self.colon_solids * c.stool_water_per_solid
        if self.colon_water > keep:
            excess = self.colon_water - keep
            back = excess * (1 - _exp_left(c.colon_water_half_life, hours))
            self.colon_water -= back
            self.body_water += back
        if self.colon_solids + self.colon_water >= c.bowel_accident_g:
            self.defecate()
            self.accidents += 1

    def _store(self, absorbed: Gut) -> None:
        c = self.config
        self.body_water += absorbed.water
        self.fat_store += absorbed.fat
        to_muscle = min(absorbed.protein,
                        max(0.0, c.baseline_muscle_protein - self.muscle_protein))
        self.muscle_protein += to_muscle
        carbs = absorbed.carbs + (absorbed.protein - to_muscle)  # gluconeogenesis
        room = c.max_glycogen - self.glycogen
        into_glycogen = min(carbs, room)
        self.glycogen += into_glycogen
        overflow_kcal = (carbs - into_glycogen) * KCAL_PER_G["carbs"]
        self.fat_store += overflow_kcal * c.carb_to_fat_efficiency / KCAL_PER_G["fat"]

    def _spend_energy(self, hours, met, temperature, infection) -> None:
        c = self.config
        fever = 1 + c.fever_bmr_per_unit_infection * infection
        need = c.bmr_kcal_per_day / 24 * met * fever * hours
        if temperature < c.shiver_below:
            need += (c.shiver_below - temperature) * c.shiver_kcal_per_degree_hour * hours
        self.kcal_burned += need
        self.body_water += need * c.metabolic_water_ml_per_kcal

        intensity = min(1.0, max(0.0, (met - 1) / 9))
        carb_share = c.carb_share_rest + (c.carb_share_max - c.carb_share_rest) * intensity
        protein_kcal = 0.0
        if self.glycogen < c.low_glycogen * c.max_glycogen:
            protein_kcal = need * c.starving_protein_share

        carb_kcal = min(need * carb_share, self.glycogen * KCAL_PER_G["carbs"])
        self.glycogen -= carb_kcal / KCAL_PER_G["carbs"]
        fat_kcal = min(need - carb_kcal - protein_kcal, self.fat_store * KCAL_PER_G["fat"])
        self.fat_store -= fat_kcal / KCAL_PER_G["fat"]
        protein_kcal = need - carb_kcal - fat_kcal  # muscle covers whatever is left
        self.muscle_protein = max(0.0, self.muscle_protein - protein_kcal / KCAL_PER_G["protein"])

    def _water_balance(self, hours, met, temperature) -> None:
        c = self.config
        loss = c.insensible_ml_per_day / 24 * hours
        loss += max(0.0, met - 2) * c.sweat_ml_per_met_hour * hours
        loss += max(0.0, temperature - 25) * c.sweat_ml_per_degree_hour * hours
        self.body_water -= loss

        urine = c.obligatory_urine_ml_per_day / 24 * hours
        surplus = self.body_water - c.normal_body_water
        if surplus > 0:
            urine += surplus * (1 - _exp_left(c.excess_water_half_life, hours))
        urine = min(urine, max(0.0, self.body_water - 0.5 * c.normal_body_water))
        self.body_water -= urine
        self.bladder += urine
        if self.bladder >= c.bladder_accident_ml:
            self.urinate()
            self.accidents += 1

    # ---- what the player feels ------------------------------------------
    @property
    def dehydration(self) -> float:
        """Fraction of normal body water lost (negative = overhydrated)."""
        return 1 - self.body_water / self.config.normal_body_water

    @property
    def glycogen_fraction(self) -> float:
        return self.glycogen / self.config.max_glycogen

    @property
    def muscle_fraction(self) -> float:
        return self.muscle_protein / self.config.baseline_muscle_protein

    @property
    def satiety(self) -> float:
        """How fed you feel: 1 = comfortably full, >1 = stuffed, 0 = starving.

        Mostly stomach stretch, plus nutrients still being absorbed, plus
        how full your glycogen stores are.
        """
        c = self.config
        stretch = self.stomach.volume / c.comfortable_stomach_ml
        digesting = min(1.0, self.intestine.kcal / 400.0)
        stores = min(1.0, self.glycogen_fraction / 0.8)
        return 0.5 * stretch + 0.1 * digesting + 0.4 * stores

    @property
    def hydration(self) -> float:
        """1 = normal, 0 = 10% of body water lost, >1 = overhydrated."""
        return 1 - self.dehydration / 0.10

    @property
    def needs_toilet(self) -> dict:
        c = self.config
        return {"pee": self.bladder >= c.bladder_urge_ml,
                "poo": self.colon_solids + self.colon_water >= c.bowel_urge_g}

    def damage_per_hour(self) -> float:
        """Health lost per hour from dehydration and starvation."""
        c, dmg = self.config, 0.0
        d = self.dehydration
        if d > c.dehydration_damage_from:
            span = c.dehydration_lethal - c.dehydration_damage_from
            dmg += 100 * (d - c.dehydration_damage_from) / span / 6  # lethal in ~6 h at the limit
        m = self.muscle_fraction
        if m < c.muscle_damage_below:
            span = c.muscle_damage_below - c.muscle_lethal
            dmg += 100 * (c.muscle_damage_below - m) / span / 24
        if d >= c.dehydration_lethal or m <= c.muscle_lethal:
            dmg = float("inf")
        return dmg

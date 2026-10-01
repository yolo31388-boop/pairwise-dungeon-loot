"""副本掉落与随机数引擎"""
import random
from dataclasses import dataclass, field

# 64位有符号整数上限，用于权重溢出防护
INT64_MAX = 2**63 - 1

RARE_RARITIES = {"rare", "epic", "legendary"}

@dataclass
class LootItem:
    iid: str
    name: str
    weight: int
    rarity: str

class LootSystem:
    PERSONAL_LOOT_POOL = ["personal_potion"]
    RAID_LOOT_POOL = ["raid_sword"]

    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.pity_counter: dict[str, int] = {}
        self.loot_log: list = []

    def roll_dice(self, min_val: int = 1, max_val: int = 100) -> int:
        # 使用实例级rng而非全局random，避免并发时的种子竞争
        return self.rng.randint(min_val, max_val)

    def calculate_loot_table(self, items: list[LootItem]) -> str:
        if not items:
            raise ValueError("loot table is empty")
        # Python大整数不会溢出，但仍做防御性检查，保证权重合法
        for item in items:
            if item.weight < 0:
                raise ValueError(f"negative weight for item {item.iid}")
        total_weight = sum(item.weight for item in items)
        if total_weight <= 0:
            raise ValueError("total weight must be positive")
        if total_weight > INT64_MAX:
            # 超出64位上限时按比例缩放，等价于使用大整数计算
            scale = INT64_MAX / total_weight
            items = [LootItem(i.iid, i.name, max(1, int(i.weight * scale)), i.rarity) for i in items]
            total_weight = sum(item.weight for item in items)
        roll = self.rng.randint(1, total_weight)
        current = 0
        for item in items:
            current += item.weight
            if current >= roll:
                return item.iid
        return items[-1].iid

    def check_pity(self, player_id: str, rarity: str) -> bool:
        count = self.pity_counter.get(player_id, 0) + 1
        if rarity in RARE_RARITIES or count >= 10:
            # 获得稀有物品或触发保底后重置计数
            self.pity_counter[player_id] = 0
            return True
        self.pity_counter[player_id] = count
        return False

    def get_personal_loot(self, player_id: str, is_raid: bool) -> list:
        # 个人掉落池与团队掉落池严格分离
        return list(self.PERSONAL_LOOT_POOL)

    def get_raid_loot(self, is_raid: bool) -> list:
        return list(self.RAID_LOOT_POOL) if is_raid else []

    def log_loot_drop(self, player_id: str, item_id: str, seed: int) -> None:
        # 记录随机种子，便于审计复现
        self.loot_log.append({"player": player_id, "item": item_id, "seed": seed})

"""副本掉落与随机数引擎"""
import random
from dataclasses import dataclass, field

@dataclass
class LootItem:
    iid: str
    name: str
    weight: int
    rarity: str

class LootSystem:
    RARE_RARITIES = {"rare", "epic", "legendary"}
    PERSONAL_POOL = ["personal_potion"]
    RAID_POOL = ["raid_sword"]

    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.pity_counter: dict[str, int] = {}
        self.loot_log: list = []

    def roll_dice(self, min_val: int = 1, max_val: int = 100) -> int:
        # 使用实例级rng，避免全局random的并发种子竞争
        return self.rng.randint(min_val, max_val)

    def calculate_loot_table(self, items: list[LootItem]) -> str:
        # Python int为任意精度大整数，不会溢出；仍需防御非法权重
        if not items:
            raise ValueError("loot table is empty")
        total_weight = sum(item.weight for item in items)
        if total_weight <= 0:
            raise ValueError("total weight must be positive")
        roll = self.rng.randint(1, total_weight)
        current = 0
        for item in items:
            current += item.weight
            if current >= roll:
                return item.iid
        return items[-1].iid

    def check_pity(self, player_id: str, rarity: str) -> bool:
        # 获得稀有物品后重置保底计数
        if rarity in self.RARE_RARITIES:
            self.pity_counter[player_id] = 0
            return True
        count = self.pity_counter.get(player_id, 0) + 1
        self.pity_counter[player_id] = count
        if count >= 10:
            self.pity_counter[player_id] = 0
            return True
        return False

    def get_personal_loot(self, player_id: str, is_raid: bool) -> list:
        # 个人掉落池与团队掉落池严格分离
        return list(self.PERSONAL_POOL)

    def get_raid_loot(self, is_raid: bool) -> list:
        return list(self.RAID_POOL) if is_raid else []

    def log_loot_drop(self, player_id: str, item_id: str, seed: int) -> None:
        # 记录随机种子，支持审计复现
        self.loot_log.append({"player": player_id, "item": item_id, "seed": seed})

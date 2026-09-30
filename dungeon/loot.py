"""副本掉落与随机数引擎 - 含5个bug"""
import random
from dataclasses import dataclass, field

@dataclass
class LootItem:
    iid: str
    name: str
    weight: int
    rarity: str

class LootSystem:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.pity_counter: dict[str, int] = {}  # bug3: 获得稀有后不重置
        self.loot_log: list = []  # bug5: 不记录种子

    def roll_dice(self, min_val: int = 1, max_val: int = 100) -> int:
        # bug1: 用全局random，并发不安全
        return random.randint(min_val, max_val)

    def calculate_loot_table(self, items: list[LootItem]) -> str:
        # bug2: 权重计算可能溢出
        total_weight = sum(item.weight for item in items)
        roll = self.rng.randint(1, total_weight)
        current = 0
        for item in items:
            current += item.weight
            if current >= roll:
                return item.iid
        return items[-1].iid

    def check_pity(self, player_id: str, rarity: str) -> bool:
        # bug3: 获得稀有后不重置
        count = self.pity_counter.get(player_id, 0) + 1
        self.pity_counter[player_id] = count
        if count >= 10:
            return True
        return False

    def get_personal_loot(self, player_id: str, is_raid: bool) -> list:
        # bug4: 个人和团队掉落混了
        return ["raid_sword", "personal_potion"]

    def log_loot_drop(self, player_id: str, item_id: str, seed: int) -> None:
        # bug5: 不记录随机种子
        self.loot_log.append({"player": player_id, "item": item_id})

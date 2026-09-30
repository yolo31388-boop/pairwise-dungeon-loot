"""副本掉落与随机数引擎 - 红态测试"""
import pytest, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dungeon.loot import LootSystem, LootItem

class TestThreadSafeRandom:
    def test_roll_dice_uses_instance_rng(self):
        ls = LootSystem(seed=42)
        # 应该用实例的rng而不是全局random
        r1 = ls.roll_dice()
        assert 1 <= r1 <= 100

class TestWeightOverflow:
    def test_large_weights_do_not_overflow(self):
        ls = LootSystem(seed=42)
        items = [LootItem(f"i{i}", f"item{i}", 1000000, "common") for i in range(100)]
        result = ls.calculate_loot_table(items)
        assert result is not None

class TestPityReset:
    def test_pity_resets_after_rare_drop(self):
        ls = LootSystem(seed=42)
        ls.pity_counter["p1"] = 10
        ls.check_pity("p1", "legendary")
        # 获得稀有后应该重置
        assert ls.pity_counter["p1"] == 0

class TestPersonalVsRaidLoot:
    def test_personal_loot_does_not_include_raid_items(self):
        ls = LootSystem(seed=42)
        personal = ls.get_personal_loot("p1", is_raid=False)
        assert "raid_sword" not in personal

class TestLootLogRecordsSeed:
    def test_log_records_random_seed(self):
        ls = LootSystem(seed=42)
        ls.log_loot_drop("p1", "sword", 12345)
        assert "seed" in ls.loot_log[0]

import json
import pprint
from dataclasses import dataclass
from awpy import Demo
import polars as pl
from pathlib import Path
from typing import Optional
@dataclass
class Parser:
    filename: Path
    dem = Demo
    map_name: Optional[str]= None


    def parse_dem(self):
        self.dem = Demo(self.filename)
        self.dem.parse(player_props=[
            "X", "Y",
        "balance", "inventory", "total_cash_spent",
        "cash_spent_this_round", "ct_losing_streak", "t_losing_streak",
        "current_equip_value",
        "inventory"]
        )

        header = self.dem.parse_header()
        self.map_name = header.get("map_name", "Unknown Map")


    def print_dem(self):
        print(self.dem.rounds.head(n=5))

    def rounds(self):
        round_ids = (
            self.dem.rounds
            .select("round_num")
            .unique()
            .sort("round_num")
            ["round_num"]
            .to_list()
        )
        return round_ids

    def get_times(self):
        pass

    def get_dataFrames(self, r):
        kills = self.get_kills(r)
        smokes = self.get_smokes(r)
        infer = self.get_infernos(r)
        he = self.get_nades(r)
        flash = self.get_flash(r)
        pl_hurt = self.get_playerHurt(r)
        pl_fired = self.get_playerFired(r)
        econ_round = self.econ(r)

        self.format_Rounds(kills, smokes, infer, he, flash, pl_hurt, pl_fired, econ_round,r)

    def format_Rounds(self, k, sm, infer, he, fl, pl_h, pl_fired, econ,r):
        m = {
            "match_id": 13,
            "map_name": self.map_name,
            "date": "2025-06-18",
            "rounds": {}
        }

        for i in r:
            round = {
                f"round_{i}":
                    {
                        "econ_freeze_start": econ[i]["start"].to_dicts(),
                        "econ_freeze_end": econ[i]["end"].to_dicts(),
                        "kills": k[i].to_dicts(),
                        "smokes": sm[i].to_dicts(),
                        "infernos": infer[i].to_dicts(),
                        "he": he[i].to_dicts(),
                        "flash": fl[i].to_dicts(),
                        "pl_h": pl_h[i].to_dicts(),
                        "pl_fired": pl_fired[i].to_dicts(),
                    }
            }

            m["rounds"].update(round)

        with open("other_thing.json", "w") as f:
            json.dump(m, f, indent=2)

    def get_kills(self, round_id):
        #Gets Kill from whatever round it need s to get them from

        roundK = {}
        for i in round_id:
            round_kills = self.dem.kills.filter(
                pl.col("round_num") == i
            ).select(["attacker_X", "attacker_Y", "attacker_name", "attacker_steamid", "attacker_side", "victim_X", "victim_Y", "victim_name", "victim_steamid", "victim_side"])

            roundK[i] = round_kills

        return roundK
    def get_smokes(self, round_id):
        sm = {}
        for i in round_id:
            rround_met = self.dem.rounds.filter(
                pl.col("round_num") == i
            ).select("freeze_end", 'official_end').row(0)

            s = self.dem.events["smokegrenade_detonate"].filter(
                (pl.col("tick") >= rround_met[0]) & (pl.col("tick") <= rround_met[1])
            ).select(["x", "y", "user_steamid", "user_name", "user_side"])

            sm[i] = s

        return sm
    def get_infernos(self, round_id):
        fern = {}

        for i in round_id:
            round_met = self.dem.rounds.filter(
                pl.col("round_num") == i

            ).select("freeze_end", 'official_end').row(0)

            inf = self.dem.events["inferno_startburn"].filter(
                (pl.col("tick") >= round_met[0]) & (pl.col("tick") <= round_met[1])
            ).select(["x", "y", "user_steamid", "user_name", "user_side"])

            fern[i] = inf

        return fern

    def get_nades(self, round_id):
        he_det = {}

        for i in round_id:
            round_met = self.dem.rounds.filter(
                pl.col("round_num") == i
            ).select("freeze_end", 'official_end').row(0)

            he = self.dem.events["hegrenade_detonate"].filter(
                (pl.col("tick") >= round_met[0]) & (pl.col("tick") <= round_met[1])
            ).select(["x", "y", "user_steamid", "user_name", "user_side"])

            he_det[i] = he

        return he_det
    def get_flash(self, round_id):
        fl_det = {}

        for i in round_id:
            round_met = self.dem.rounds.filter(
                pl.col("round_num") == i
            ).select("freeze_end", 'official_end').row(0)

            fl = self.dem.events["flashbang_detonate"].filter(
                (pl.col("tick") >= round_met[0]) & (pl.col("tick") <= round_met[1])
            ).select(["x", "y", "user_steamid", "user_name", "user_side"])

            fl_det[i] = fl

        return fl_det

    def get_playerHurt(self, round_id):
        pl_hurt = {}

        for i in round_id:
            round_met = self.dem.rounds.filter(
                pl.col("round_num") == i
            ).select("freeze_end", 'official_end').row(0)

            hurt = self.dem.events["player_hurt"].filter(
                (pl.col("tick") >= round_met[0]) & (pl.col("tick") <= round_met[1])
            ).select(["user_X", "user_Y", "user_steamid", "user_name", "user_side"])

            pl_hurt[i] = hurt

        return pl_hurt

    def get_playerFired(self, round_id):
        pl_fired = {}

        for i in round_id:
            round_met = self.dem.rounds.filter(
                pl.col("round_num") == i
            ).select("freeze_end", 'official_end').row(0)

            fired = self.dem.events["weapon_fire"].filter(
                (pl.col("tick") >= round_met[0]) & (pl.col("tick") <= round_met[1])
            ).select(["user_X", "user_Y", "user_steamid", "user_name", "user_side"])

            pl_fired[i] = fired

        return pl_fired

    def econ(self, round_id):
        econ = {}

        for i in round_id:
            round_met = self.dem.rounds.filter(
                pl.col("round_num") == i
            ).select("start", "freeze_end").row(0)


            freeze_start = self.dem.ticks.filter(
                (pl.col("round_num") == i) & (pl.col("tick") == round_met[0]) & (pl.col("side").is_not_null())
            ).unique().select(["name", "steamid", "side", "total_cash_spent", "cash_spent_this_round", "balance", "ct_losing_streak", "t_losing_streak", "current_equip_value"])

            freeze_end = self.dem.ticks.filter(
                (pl.col("round_num") == i) & (pl.col("tick") == round_met[1]) & (pl.col("side").is_not_null())
            ).unique().select(["name", "steamid", "side", "total_cash_spent", "cash_spent_this_round", "balance", "ct_losing_streak", "t_losing_streak", "current_equip_value"])

            econ[i] = {
                "start": freeze_start,
                "end": freeze_end
            }
        
        return econ

@dataclass
class RoundState:
    startTick: int
    endTick: int
    kills_df: pl.DataFrame
    smokes_df: pl.DataFrame
    infernos_df: pl.DataFrame
    nades_df: pl.DataFrame
    flash_df: pl.DataFrame
    playerHurt_df: pl.DataFrame
    playerFired_df: pl.DataFrame

import json
from database.tables import Match, Round, Player, Event, EconSnapshot, KillEvent
from datetime import datetime
from sqlalchemy.orm import sessionmaker

def insert_data(session, json_path="other_thing.json"):
    
    with open(json_path, "r") as f:
        data = json.load(f)

    match = Match(
        match_id=int(data["match_id"]),
        map_name=data["map_name"],
        date=datetime.fromisoformat(data["date"])
    )
    session.add(match)
    session.commit() 

    for round_str, r in data["rounds"].items():
        rnd = Round(
            match_id=match.match_id,
            round_number=round_str.split("_")[1]
        )
        session.add(rnd)
        session.flush()  

        for econ in r["econ_freeze_start"]:
            sid = int(econ["steamid"])
            sname = econ["name"]
            
            if not session.get(Player, sid):
                session.add(Player(steamid=sid, name=sname))
                session.flush()

            session.add(EconSnapshot(
                round_id=rnd.round_id,
                event_type="freeze_start",
                steamid=sid,
                side=econ["side"],
                total_cash_spent=econ["total_cash_spent"],
                cash_this_round=econ["cash_spent_this_round"],
                balance=econ["balance"],
                ct_losing_streak=econ["ct_losing_streak"],
                t_losing_streak=econ["t_losing_streak"],
                equip_value=econ["current_equip_value"]
            ))

        for econ in r["econ_freeze_end"]:
            sid = int(econ["steamid"])
            sname = econ["name"]
            if not session.get(Player, sid):
                session.add(Player(steamid=sid, name=sname))
                session.flush()

            session.add(EconSnapshot(
                round_id=rnd.round_id,
                event_type="freeze_end",
                steamid=sid,
                side=econ["side"],
                total_cash_spent=econ["total_cash_spent"],
                cash_this_round=econ["cash_spent_this_round"],
                balance=econ["balance"],
                ct_losing_streak=econ["ct_losing_streak"],
                t_losing_streak=econ["t_losing_streak"],
                equip_value=econ["current_equip_value"]
            ))
        for k in r["kills"]:
            for sid in (k["attacker_steamid"], k["victim_steamid"]):
                if not session.get(Player, sid):
                    session.add(Player(steamid=sid))
            session.flush()

            if k["attacker_X"] is None or k["attacker_Y"] is None or k["attacker_steamid"] is None or k["attacker_name"] is None or k["attacker_side"] is None:
                print(f"Skipping kill with missing coords: {k}")
                continue

            kill = KillEvent(
                round_id=rnd.round_id,
                attacker_id=k["attacker_steamid"],
                victim_id=k["victim_steamid"],
                attacker_side=k["attacker_side"],
                attacker_x=k["attacker_X"],
                attacker_y=k["attacker_Y"],
                victim_x=k["victim_X"],
                victim_y=k["victim_Y"],
                victim_side=k["victim_side"]
            )
            session.add(kill)

        for arr_key, evt_type in [
            ("smokes",  "smoke"),
            ("infernos","inferno"),
            ("he",     "he"),
            ("flash",  "flash"),
            ("pl_h",   "pl_h"),
            ("pl_fired","pl_fired")
        ]:
            for e in r.get(arr_key, []):
                sid = e["user_steamid"]
                if not session.get(Player, sid):
                    session.add(Player(steamid=sid))
                session.flush()

                x = e.get("x", e.get("user_X"))
                y = e.get("y", e.get("user_Y"))

                if x is None or y is None:
                    print(f"Skipping event without coords: {e}")
                    continue

                ev = Event(
                    round_id=rnd.round_id,
                    steamid=sid,
                    event_type=evt_type,
                    x=x,
                    y=y
                )
                session.add(ev)

    session.commit()

            
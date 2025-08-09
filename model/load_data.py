from database.tables import KillEvent, Event, Match, Round
from sqlalchemy import select
import os
from pathlib import Path
import json
from model.t_scale import translate_scale
import numpy as np

def load_map_data(dir_path):
    m_d = {}
    for i in os.listdir(dir_path):
        with open(os.path.join(dir_path, i), "r") as f:
            data = json.load(f)
            
            temp = i.split(".")[0]
            m_d[temp] = data
    return m_d


def query_data(session, m_d):
    players = [76561198837117408, 76561198839305865, 76561198889240025, 76561198951467648, 76561199034495166]
    map_need = "de_mirage"
    stmt_kill = (
        select(KillEvent)
        .join(KillEvent.round)         
        .join(Round.match)            
        .where(
            Match.map_name == map_need,
            KillEvent.attacker_id.in_(players)
        )
    )

    stmt_plH = (
        select(Event)
        .join(Event.round)
        .join(Round.match)
        .where(
            Match.map_name == map_need,
            Event.event_type == "pl_h",
            Event.steamid.in_(players)
        )
    )

    stmt_smoke = (
        select(Event)
        .join(Event.round)
        .join(Round.match)
        .where(
            Match.map_name == map_need,
            Event.event_type.in_(["smoke"]),
            Event.steamid.in_(players)
        )
    )

    stmt_he = (
        select(Event)
        .join(Event.round)
        .join(Round.match)
        .where(
            Match.map_name == map_need,
            Event.event_type.in_(["he"]),
            Event.steamid.in_(players)
        )
    )

    stmt_inferno = (
        select(Event)
        .join(Event.round)
        .join(Round.match)
        .where(
            Match.map_name == map_need,
            Event.event_type.in_(["inferno"]),
            Event.steamid.in_(players)
        )
    )

    stmt_plFired = (
        select(Event)
        .join(Event.round)
        .join(Round.match)
        .where(
            Match.map_name == map_need,
            Event.event_type.in_(["pl_fired"]),
            Event.steamid.in_(players)
        )
    )

    kills = session.execute(stmt_kill).scalars().all()
    ev_plHit = session.execute(stmt_plH).scalars().all()
    ev_smoke = session.execute(stmt_smoke).scalars().all()
    ev_he = session.execute(stmt_he).scalars().all()
    ev_inferno = session.execute(stmt_inferno).scalars().all()
    ev_plFired = session.execute(stmt_plFired).scalars().all()

    kill_p = kills_query(kills, m_d[map_need])
    ev_he = he_query(ev_he, m_d[map_need])
    ev_smoke = smoke_query(ev_smoke, m_d[map_need])
    ev_inferno = inferno_query(ev_inferno, m_d[map_need])
    ev_plHit = player_hit_query(ev_plHit, m_d[map_need])
    ev_plFired = player_fired_query(ev_plFired, m_d[map_need])

    return kill_p, ev_plHit, ev_smoke, ev_he, ev_inferno, ev_plFired

def kills_query(kills, m_d):
    kill_p = np.empty((0, 2), dtype=float)
    for kill in kills:
        if kill.victim_side == "t":
            continue
        
        x, y = kill.victim_x, kill.victim_y

        x, y = translate_scale(x, y, m_d)

        new = np.array([x, y], dtype=float).reshape(1, 2)
        kill_p = np.append(kill_p, new, axis=0)

    return kill_p


def smoke_query(events, m_d):
    smoke_data = np.empty((0, 2), dtype=float)
    for event in events:
        x, y = event.x, event.y

        x, y = translate_scale(x, y, m_d)

        new = np.array([x, y], dtype=float).reshape(1, 2)
        smoke_data = np.append(smoke_data, new, axis=0)
    return smoke_data

def he_query(events, m_d):
    he_data = np.empty((0, 2), dtype=float)
    for event in events:
        x, y = event.x, event.y

        x, y = translate_scale(x, y, m_d)

        new = np.array([x, y], dtype=float).reshape(1, 2)
        he_data = np.append(he_data, new, axis=0)
    return he_data
    

def inferno_query(events, m_d):
    inferno_data = np.empty((0, 2), dtype=float)
    for event in events:
        x, y = event.x, event.y

        x, y = translate_scale(x, y, m_d)

        new = np.array([x, y], dtype=float).reshape(1, 2)
        inferno_data = np.append(inferno_data, new, axis=0)
    return inferno_data

def player_hit_query(events, m_d):
    player_hit_data = np.empty((0, 2), dtype=float)
    for event in events:
        x, y = event.x, event.y

        x, y = translate_scale(x, y, m_d)

        new = np.array([x, y], dtype=float).reshape(1, 2)
        player_hit_data = np.append(player_hit_data, new, axis=0)
    return player_hit_data

def player_fired_query(events, m_d):
    player_fired_data = np.empty((0, 2), dtype=float)
    for event in events:
        x, y = event.x, event.y

        x, y = translate_scale(x, y, m_d)

        new = np.array([x, y], dtype=float).reshape(1, 2)
        player_fired_data = np.append(player_fired_data, new, axis=0)
    return player_fired_data
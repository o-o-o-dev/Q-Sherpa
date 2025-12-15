from typing import List

from src.models import Equipment, EquipmentList, Member, MemberList


def load_equipments() -> List[Equipment]:
    filepath = "data/equipments.json"

    with open(filepath, "rt", encoding="utf-8") as f:
        equipments = EquipmentList.validate_json(f.read())
    return equipments


equipments = load_equipments()


def load_members() -> List[Member]:
    filepath = "data/members.json"

    with open(filepath, "rt", encoding="utf-8") as f:
        members = MemberList.validate_json(f.read())
    return members


members = load_members()

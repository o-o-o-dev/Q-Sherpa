from typing import List
from fastapi import HTTPException
import jijmodeling as jm
from ommx.v1 import Instance
from ommx_openjij_adapter import OMMXOpenJijSAAdapter
from src.models import Equipment, EquipmentAssignment, EquipmentSettings, Member


def equipment_problem():
    # --- 変数設定 ---
    Experience = jm.Placeholder("experience", ndim=1, description="メンバーの経験年数")
    M = Experience.len_at(0, latex="M", description="メンバー数")
    m = jm.Element("m", belong_to=(0, M), description="メンバーインデックス")
    m_inner = jm.Element(
        "m_inner", belong_to=(0, M), description="平均計算用メンバーインデックス"
    )

    # Teams = jm.Placeholder("teams", ndim=2, description="チーム割り")
    # T = Teams.len_at(0, latex="T", description="チーム数")
    # t = jm.Element("t", belong_to=(0, T), description="チームインデックス")

    Weight = jm.Placeholder("equipment", ndim=1, description="装備の重量")
    E = Weight.len_at(0, latex="E", description="装備数")
    e = jm.Element("e", belong_to=(0, E), description="装備インデックス")

    # Capacity = jm.Placeholder("capacity", shape=(E,), description="装備の体積")

    # --- 決定変数 ---
    x = jm.BinaryVar("x", shape=(M, E), description="メンバーmに装備eを割り当てる変数")

    # --- 問題の構築 ---
    problem = jm.Problem("Equipment Assignment for Team members")

    # --- すべての装備を誰か1人が持つ制約 ---
    problem += jm.Constraint(
        "all_equipment_assigned",
        jm.sum(m, x[m, e]) == 1,
        forall=[e],
    )

    # --- 装備重量がメンバー間で均等になるようにする
    ## 経年数`Experience`が高いメンバーほど多くの装備を持てるようにする
    P = jm.Placeholder("P", description="経験による装備量の調整パラメータ")
    weight_weight = jm.Placeholder(
        "weightWeight", description="重量均等化の重み付けパラメータ"
    )
    avg_weight = jm.sum([m_inner, e], Weight[e] * x[m_inner, e]) / M
    avg_experience = jm.sum(m_inner, Experience[m_inner]) / M
    adjusted_avg_weight = avg_weight * ((Experience[m] / avg_experience) ** P)
    problem += (
        jm.sum(
            m,
            (jm.sum(e, Weight[e] * x[m, e]) - adjusted_avg_weight) ** 2,
        )
        * weight_weight
    )

    return problem


def equipment_solver(
    teams: List[List[Member]],
    equipment: List[Equipment],
    settings: EquipmentSettings,
) -> List[EquipmentAssignment]:
    if not teams or not equipment:
        raise HTTPException(
            status_code=400, detail="チームまたは装備が指定されていません。"
        )

    # --- 問題定義 ---
    instance_data = {
        "experience": [member.exp_years for team in teams for member in team],
        # "teams": [[member.id for member in team] for team in teams],
        "equipment": [eq.weight for eq in equipment],
        # "capacity": [eq.capacity for eq in equipment],
        "P": settings.P,
        "weightWeight": settings.weightWeight,
    }
    interpreter = jm.Interpreter(instance_data)
    instance: Instance = interpreter.eval_problem(equipment_problem())

    # --- ソルバーによる解法 ---
    # num_reads は試行回数。多いほど安定する。
    result = OMMXOpenJijSAAdapter.sample(instance, num_reads=settings.num_reads)

    # --- 結果の取得 ---
    # 最良の解を取得
    try:
        # Dict[Tuple[Member.id, Equipment.id], 0 | 1]
        best_sample = result.best_feasible_unrelaxed.extract_decision_variables("x")
    except RuntimeError:
        raise HTTPException(
            status_code=500,
            detail="有効な解が見つかりませんでした。制約条件が厳しすぎるか、試行回数が不足している可能性があります。",
        )

    # x_ij = 1 となった装備を抽出
    assigned_equipment: List[EquipmentAssignment] = []
    for team in teams:
        for member in team:
            member_equipment: List[Equipment] = []
            for eq in equipment:
                if best_sample.get((member.id, eq.id), 0) == 1:
                    member_equipment.append(eq)
            assigned_equipment.append(
                EquipmentAssignment(member=member, equipment=member_equipment)
            )

    return assigned_equipment

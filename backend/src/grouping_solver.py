from typing import List
from fastapi import HTTPException
import jijmodeling as jm
from ommx.v1 import Instance
from src.models import GroupingSettings, Member, RoleAuthoritative, RoleFixed
from ommx_openjij_adapter import OMMXOpenJijSAAdapter


def grouping_problem():
    # --- 定数設定 ---
    K = jm.Placeholder("K", dtype=jm.DataType.INTEGER, description="チーム数")
    k = jm.Element("k", belong_to=(0, K), description="チームインデックス")

    # --- 変数定義 ---
    Grade = jm.Placeholder("grade", ndim=2, description="メンバーの学年")
    G = Grade.len_at(0, latex="G", description="学年の種類数")
    g = jm.Element("g", belong_to=(0, G), description="学年インデックス")

    M = Grade.len_at(1, latex="M", description="メンバーの数")
    m = jm.Element("m", belong_to=(0, M), description="メンバーインデックス")
    m2 = jm.Element("m2", belong_to=(0, M), description="メンバーインデックス2")

    Sex = jm.Placeholder("sex", shape=(None, M), description="メンバーの性別")
    S = Sex.len_at(0, latex="S", description="性別の種類数")
    s = jm.Element("s", belong_to=(0, S), description="性別インデックス")

    Role = jm.Placeholder("role", shape=(None, M), description="メンバーの係")
    R = Role.len_at(0, latex="R", description="係の種類数")
    r = jm.Element("r", belong_to=(0, R), description="係インデックス")

    Can_CL = jm.Placeholder("cancl", shape=(M,), description="メンバーのCL資格フラグ")
    Can_SL = jm.Placeholder("cansl", shape=(M,), description="メンバーのSL資格フラグ")

    Driver = jm.Placeholder("driver", shape=(M,), description="メンバーの運転手フラグ")

    Carrier = jm.Placeholder(
        "carrier", shape=(None, M), description="メンバーの通信キャリア"
    )
    C = Carrier.len_at(0, latex="C", description="キャリアの種類数")
    c = jm.Element("c", belong_to=(0, C), description="キャリアインデックス")

    Experience = jm.Placeholder(
        "experience", shape=(M,), description="メンバーの経験年数"
    )

    # --- 決定変数定義 ---
    x = jm.BinaryVar("x", shape=(K, M), description="チーム割当変数")
    cl = jm.BinaryVar("cl", shape=(K, M), description="CL割当変数")
    sl = jm.BinaryVar("sl", shape=(K, M), description="SL割当変数")

    # --- 問題の構築 ---
    problem = jm.Problem("Grouping Members into Teams")

    # 全員必ずどこか1つのチームに所属する
    # sum_j x[i, j] == 1
    problem += jm.Constraint(
        "one_group_per_member", jm.sum(k, x[k, m]) == 1, forall=[m]
    )

    # 各チームにCLとSLが必ず1人ずついる
    problem += jm.Constraint("one_cl_per_team", jm.sum(m, cl[k, m]) == 1, forall=[k])
    problem += jm.Constraint("one_sl_per_team", jm.sum(m, sl[k, m]) == 1, forall=[k])

    # 資格がない人はSL/CLになれない
    problem += jm.Constraint("qualification_CL", cl[k, m] <= Can_CL[m], forall=[k, m])
    problem += jm.Constraint("qualification_SL", sl[k, m] <= Can_SL[m], forall=[k, m])

    # 整合性: SL/CLはそのグループのメンバーでなければならない
    # cl[i, j] <= x[i, j] (担当なら、所属も1でなければならない)
    problem += jm.Constraint("consistency_CL", cl[k, m] <= x[k, m], forall=[k, m])
    problem += jm.Constraint("consistency_SL", sl[k, m] <= x[k, m], forall=[k, m])

    # 【重要】CLとSLは別人でなければならない
    # 同一メンバー i が、同じグループ j で両方の担当にはなれない
    # cl[i, j] + sl[i, j] <= 1
    problem += jm.Constraint("distinct_roles", cl[k, m] + sl[k, m] <= 1, forall=[k, m])

    # グループ人数の均等化
    # 各グループの人数と、理想人数(N/M)の差の二乗和を最小化
    group_size_weight = jm.Placeholder(
        "groupSizeWeight", description="グループ人数均等化の重み"
    )
    group_size = jm.sum(m, x[k, m])
    ideal_size = M / K
    problem += jm.sum(k, (group_size - ideal_size) ** 2) * group_size_weight

    # 学年の均等化
    grade_population_weight = jm.Placeholder(
        "gradePopulationWeight", description="学年均等化の重み"
    )
    grade_population_per_team = jm.sum(m, Grade[g, m] * x[k, m])
    grade_total_population = jm.sum(m, Grade[g, m])
    grade_ideal_population = grade_total_population / K
    problem += (
        jm.sum([k, g], (grade_population_per_team - grade_ideal_population) ** 2)
        * grade_population_weight
    )

    # 同じ性別の人が一人にならないようにする
    # 0人または2人以上にする
    ## 線形ペナルティ
    gender_should_be_zero_weight = jm.Placeholder(
        "genderShouldBeZeroWeight", description="同じ性別が0人であるべきという重み"
    )
    linear_penalty = (
        jm.sum([m, s, k], Sex[s, m] * x[k, m]) * gender_should_be_zero_weight
    )
    ## 複数人時のボーナス
    gender_pair_bonus_weight = jm.Placeholder(
        "genderPairBonusWeight",
        description="同じ性別は多いほうがいいという重み",
    )
    pair_bonus = (
        jm.sum([m, (m2, m != m2), s, k], Sex[s, m] * Sex[s, m2] * x[k, m] * x[k, m2])
        * gender_pair_bonus_weight
    )
    problem += linear_penalty - pair_bonus

    # 係の均等化
    role_population_weight = jm.Placeholder(
        "rolePopulationWeight", description="係の均等化の重み"
    )
    role_population_per_team = jm.sum(m, Role[r, m] * x[k, m])
    role_total_population = jm.sum(m, Role[r, m])
    role_ideal_population = role_total_population / K
    problem += (
        jm.sum([k, r], (role_population_per_team - role_ideal_population) ** 2)
        * role_population_weight
    )

    # 運転手の均等化
    driver_population_weight = jm.Placeholder(
        "driverPopulationWeight", description="運転手の均等化の重み"
    )
    driver_population_per_team = jm.sum(m, Driver[m] * x[k, m])
    driver_total_population = jm.sum(m, Driver[m])
    driver_ideal_population = driver_total_population / K
    problem += (
        jm.sum(k, (driver_population_per_team - driver_ideal_population) ** 2)
        * driver_population_weight
    )

    # 通信キャリアの均等化
    carrier_population_weight = jm.Placeholder(
        "carrierPopulationWeight", description="通信キャリアの均等化の重み"
    )
    carrier_population_per_team = jm.sum(m, Carrier[c, m] * x[k, m])
    carrier_total_population = jm.sum(m, Carrier[c, m])
    carrier_ideal_population = carrier_total_population / K
    problem += (
        jm.sum([k, c], (carrier_population_per_team - carrier_ideal_population) ** 2)
        * carrier_population_weight
    )

    # 経験年数の均等化 (Total Experience Balancing)
    # (チームの合計経験値 - 理想)の二乗和を最小化
    inter_team_experience_similarity_weight = jm.Placeholder(
        "interTeamExperienceSimilarityWeight",
        description="経験年数の和のチーム間での均等化の重み",
    )
    group_exp_sum = jm.sum(m, Experience[m] * x[k, m])
    ideal_exp_sum = jm.sum(m, Experience[m]) / K
    problem += jm.sum(k, (group_exp_sum - ideal_exp_sum) ** 2) * inter_team_experience_similarity_weight

    # 似た経験年数の人を集める（内部分散の最小化）
    # グループ内のメンバー同士の経験年数の差の二乗を最小化する
    # (mとm2が同じグループにいる時だけ、(Experience[m] - Experience[m2])^2 のコストがかかる)
    intra_team_experience_similarity_weight = jm.Placeholder(
        "intraTeamExperienceSimilarityWeight",
        description="班ごとの経験年数の類似化の重み",
    )
    problem += (
        jm.sum([k, m, m2], (Experience[m] - Experience[m2]) ** 2 * x[k, m] * x[k, m2])
        * intra_team_experience_similarity_weight
    )

    return problem


def grouping_solver(
    members: List[Member],
    num_teams: int,
    settings: GroupingSettings,
) -> List[List[Member]]:
    if not members:
        raise HTTPException(status_code=400, detail="メンバーが指定されていません。")

    # --- 問題定義 ---
    instance_data = {
        "K": num_teams,
        "grade": [
            [1 if member.grade == grade else 0 for member in members]
            for grade in [1, 2, 3]
        ],
        "sex": [
            [1 if member.gender == gender else 0 for member in members]
            for gender in ["M", "F"]
        ],
        "role": [
            [1 if member.role_fixed == role else 0 for member in members]
            for role in [RoleFixed.Equipment, RoleFixed.Weather, RoleFixed.Meal]
        ],
        "cancl": [
            1 if member.role_authoritative == RoleAuthoritative.CL else 0
            for member in members
        ],
        "cansl": [
            1
            if member.role_authoritative == RoleAuthoritative.SL
            or member.role_authoritative == RoleAuthoritative.CL
            else 0
            for member in members
        ],
        "driver": [1 if member.driver else 0 for member in members],
        "carrier": [
            [1 if member.carrier == carrier else 0 for member in members]
            for carrier in ["docomo", "au", "softbank", "rakuten"]
        ],
        "experience": [member.exp_years for member in members],
        "groupSizeWeight": settings.groupSizeWeight,
        "gradePopulationWeight": settings.gradePopulationWeight,
        "genderShouldBeZeroWeight": settings.genderShouldBeZeroWeight,
        "genderPairBonusWeight": settings.genderPairBonusWeight,
        "rolePopulationWeight": settings.rolePopulationWeight,
        "driverPopulationWeight": settings.driverPopulationWeight,
        "carrierPopulationWeight": settings.carrierPopulationWeight,
        "interTeamExperienceSimilarityWeight": settings.interTeamExperienceSimilarityWeight,
        "intraTeamExperienceSimilarityWeight": settings.intraTeamExperienceSimilarityWeight,
    }
    interpreter = jm.Interpreter(instance_data)
    instance: Instance = interpreter.eval_problem(grouping_problem())

    # --- ソルバーによる解法 ---
    # num_reads は試行回数。多いほど安定する。
    result = OMMXOpenJijSAAdapter.sample(instance, num_reads=settings.num_reads)

    # --- 結果の取得 ---
    # 最良の解を取得
    try:
        best_sample = result.best_feasible_unrelaxed.extract_decision_variables("x")
    except RuntimeError:
        raise HTTPException(
            status_code=500,
            detail="有効な解が見つかりませんでした。制約条件が厳しすぎるか、試行回数が不足している可能性があります。",
        )

    # x_ij = 1 となったメンバーを抽出
    teams: List[List[Member]] = [[] for _ in range(num_teams)]
    for (k_i, m_i), v in best_sample.items():
        if v == 1:
            teams[k_i].append(members[m_i])

    return teams

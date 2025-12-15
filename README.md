# 🏔️ Quantum Mountain Optimizer

### 量子アニーリングを用いた登山チーム編成・装備配分最適化システム

## 📖 Overview

**Quantum Mountain Optimizer** は、登山計画における最も複雑なタスクである「安全なチーム分け」と「公平な装備配分」を、量子アニーリング（Ising Model / QUBO）を用いて自動化するシステムです。

従来の経験則に頼った計画ではなく、**通信キャリアの分散**、**運転免許の確保**、**個人の体力差に応じた負荷平準化**などの多次元的な制約条件を数理的に満たす最適解を瞬時に導き出します。

## 🚀 Key Features

### 1\. 安全性を担保するチーム編成 (Team Optimization)

  * **通信リスク分散:** ドコモ、au、SoftBankなどのキャリアが特定の班に偏らないよう分散（通信途絶リスクの低減）。
  * **スキルセット確保:** 各班にリーダー(CL/SL)、医療担当(天気)、食事担当、装備担当を必須配置。
  * **ドライバー確保:** レンタカー運用に必要な運転免許保持者を各班に最適配置。

### 2\. 「不公平感」をなくす装備配分 (Load Balancing)

  * **体力相対評価:** 学年、性別、経験年数から「基礎体力スコア」を算出。
  * **負荷率の平準化:** 「重いテントは体力のある装備係へ」「かさばるが軽い食材は女性メンバーへ」など、全員の\*\*負荷率（積載重量 / 体力スコア）\*\*が均一になるよう最適化。

## 🛠️ Tech Stack

  * **Language:** Python 3.10+
  * **Package Manager:** [uv](https://github.com/astral-sh/uv) (Ultra-fast Python package installer)
  * **Web Framework:** [FastAPI](https://fastapi.tiangolo.com/)
  * **Server:** Uvicorn
  * **Optimization Solver:**
      * Formulation: `PyQUBO`
      * Sampler: `OpenJij` (Simulated Annealing for local demo) / `D-Wave Ocean SDK` (Quantum Hardware ready)

## 📐 Mathematical Model (QUBO)

本システムは、問題を2段階のハミルトニアン（コスト関数）として定式化しています。

### Phase 1: Team Clustering & Equipment Assignment

チーム編成行列 $x_{i,k}$ と装備割当行列 $z_{j,k}$ を同時最適化します。

$$
H_{Phase1} = H_{OneTeam} + H_{RoleBalance} + H_{CarrierDiv}
$$

### Phase 2: Equipment Distribution (Knapsack Variant)

装備配分行列 $y_{m,i}$ を最適化し、全員の「つらさ」を等しくします。

$$
H_{Phase2} = H_{RoleConstraint} + \sum_{i} \left( \text{Load}_i - \text{Capacity}_i \times \alpha \right)^2
$$

-----

## ⚡ Quick Start

パッケージマネージャーに `uv` を使用しています。

### 1\. Setup Environment

```bash
uv sync
```

### 2\. Run Server

```bash
# 開発サーバーの起動
uv run uvicorn main:app --reload
```

## 📡 API Usage

### `POST /optimize`

メンバーリストを受け取り、最適な計画を返します。

**Request Body (JSON):**

```json
{
  "members": [
    {"id": 1, "name": "Sato", "grade": 3, "role": "CL", "gender": "M", "driver": true, "carrier": "au", "exp_years": 2.5},
    {"id": 2, "name": "Tanaka", "grade": 1, "role": "Equip", "gender": "F", "driver": false, "carrier": "docomo", "exp_years": 0.5},
    ...
  ],
  "equipments": [
    {"id": "t1", "name": "Montbell V6", "capacity": 6, "weight_kg": 4.5},
    {"id": "t2", "name": "AirRaiz 2", "capacity": 3, "weight_kg": 2.1}
  ],
  "num_teams": 4
}
```

**Response (JSON):**

```json
{
  "teams": {
    "Team_A": {
      "members": ["Sato", "Suzuki", ...],
      "tent": "Montbell V6",
      "safety_score": 98
    }
  },
  "packing_list": {
    "Sato": {
      "items": ["Montbell V6", "Gas Canister"],
      "total_weight": 18.5,
      "load_ratio": 0.85
    }
  }
}
```

## 📂 Project Structure

```
.
├── main.py             # FastAPI entry point
├── solver/
│   ├── models.py       # Pydantic models
│   ├── loader.py       # Read data from JSON
│   └── solver.py       # Solver execution
├── data/
│   ├── members.json    # Sample input data
│   └── equipments.json # Equipment data
├── README.md
└── pyproject.toml
```

## 📝 Future Work

  * D-Wave Leap (Hybrid Solver) への接続実装。
  * 食料消費による日毎の重量変化を考慮した動的計画法への拡張。
  * Google Forms とのAPI連携による自動エントリー機能。

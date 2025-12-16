# Quantum Mountain Optimizer - Demo Page

## 📋 概要

登山チーム編成・装備配分最適化システムのデモページです。4 つのフェーズで構成されたステップウィザード形式の UI を提供します。

## 🎯 実装フェーズ

### Phase 1: メンバー選択

- メンバーリストの表示（テーブル形式）
- チェックボックスによる選択機能（全選択/個別選択）
- メンバーの追加・削除機能
- 役割・キャリア・免許などの属性表示

### Phase 2: 班分け結果表示

- 量子アニーリング最適化の実行（モック実装）
- カード形式での班編成結果表示
- 安全性スコアの可視化
- メンバー属性（ドライバー、キャリア）の表示
- 班ごとの統計情報

### Phase 3: 装備選択

- 装備リストの表示（テーブル形式）
- カテゴリー別フィルタリング
- 装備の選択・追加・削除機能
- 重量・収容人数の表示

### Phase 4: 最終配分結果

- 個人別装備配分の表示
- 負荷率の可視化（プログレスバー・グラフ）
- 班別サマリー表示
- JSON 出力機能
- 3 つの表示モード切り替え（個人別/班別/グラフ）

## 🛠️ 技術スタック

- **Framework**: Nuxt 3
- **Language**: TypeScript
- **Style**: SCSS (Scoped)
- **Component Pattern**: `<script setup>`
- **State Management**: `ref`, `computed`
- **Transitions**: Vue `<Transition>` & `<TransitionGroup>`

## 📁 ファイル構成

```
frontend/app/
├── pages/
│   └── demo/
│       └── index.vue              # メインデモページ（ステップウィザード）
├── components/
│   └── demo/
│       ├── MemberSelection.vue    # Phase 1: メンバー選択
│       ├── GroupingResult.vue     # Phase 2: 班分け結果
│       ├── EquipmentSelection.vue # Phase 3: 装備選択
│       └── FinalAllocation.vue    # Phase 4: 最終結果
├── composables/
│   └── useOptimizationApi.ts      # API通信とモックデータ管理
├── types/
│   └── index.d.ts                 # TypeScript型定義
└── assets/
    └── scss/
        └── _variables.scss         # SCSS変数
```

## 🎨 主要機能

### アニメーション

- ページ遷移時のフェード・スライドアニメーション
- リストアイテムの追加/削除アニメーション
- プログレスバーのスムーズな変化
- カードのホバーエフェクト

### インタラクション

- テーブル行のクリック選択
- モーダルダイアログ
- タブ切り替え
- キーボードナビゲーション（ESC キーで戻る）

### レスポンシブデザイン

- モバイル対応
- 可変グリッドレイアウト
- オーバーフロー時のスクロール

## 🔌 API 統合

### モックモード（開発用）

`composables/useOptimizationApi.ts`の`USE_MOCK`フラグで制御：

```typescript
const USE_MOCK = true; // 開発中はtrue、本番APIが完成したらfalse
```

### 本番 API 統合

環境変数で API ベース URL を設定：

```bash
NUXT_PUBLIC_API_BASE=http://localhost:8000
```

### エンドポイント

- `GET /members` - メンバーリスト取得
- `GET /equipment` - 装備リスト取得
- `POST /grouping` - 班分け実行
- `POST /equipment` - 装備配分実行

## 🚀 実行方法

### 1. 依存関係のインストール

```bash
cd frontend
npm install
# または
pnpm install
```

### 2. 開発サーバー起動

```bash
npm run dev
# または
pnpm dev
```

### 3. デモページにアクセス

```
http://localhost:3000/demo
```

## 📊 データフロー

```
Phase 1: メンバー選択
    ↓ (選択されたメンバー)
Phase 2: 班分け実行 (POST /grouping)
    ↓ (班分け結果)
Phase 3: 装備選択
    ↓ (選択された装備 + 班分け結果)
Phase 4: 配分最適化 (POST /equipment)
    ↓ (最終配分結果)
表示 & JSON出力
```

## 🎯 主要な型定義

```typescript
interface Member {
  id: number;
  name: string;
  grade: number;
  role: "CL" | "SL" | "Equip" | "Food" | "Medic" | "Member";
  gender: "M" | "F";
  driver: boolean;
  carrier: "docomo" | "au" | "SoftBank" | "Rakuten" | "Other";
  exp_years: number;
}

interface Equipment {
  id: string;
  name: string;
  capacity: number;
  weight_kg: number;
}

interface Team {
  name: string;
  members: Member[];
  tent?: string;
  safety_score?: number;
}

interface MemberAllocation {
  member_name: string;
  items: AllocationItem[];
  total_weight: number;
  load_ratio: number;
  capacity_score: number;
}
```

## 🎨 カラーパレット

- Primary: `#299967` (グリーン)
- Secondary: `#825dab` (パープル)
- Success: `#20bf7a`
- Warning: `#ffb900`
- Error: `#fd5c5c`

## 📝 今後の拡張

- [ ] リアルタイムバリデーション
- [ ] エラーハンドリングの強化（トースト通知）
- [ ] 結果の PDF 出力
- [ ] 履歴機能
- [ ] ユーザー認証連携
- [ ] D-Wave Leap 連携

## 🐛 デバッグ

開発者ツールのコンソールで以下の情報を確認できます：

- API 呼び出しのログ
- エラーメッセージ
- 状態遷移のログ

## 📄 ライセンス

プロジェクトのライセンスに従います。

<template>
  <div class="demo">
    <div class="island">
      <header class="hero">
        <div class="hero__title">
          <h1>🏔️ Q-Sherpa Demo</h1>
          <p>
            量子アニーリング風の最適化で「安全な班分け」と「装備配分」を体験できます。
          </p>
        </div>

        <nav class="stepper" aria-label="Wizard steps">
          <ol class="stepper__list">
            <li
              :class="[
                'stepper__item',
                currentStep === 'members' && 'is-active',
              ]"
            >
              1. メンバー選択
            </li>
            <li
              :class="[
                'stepper__item',
                currentStep === 'grouping' && 'is-active',
              ]"
            >
              2. 班分け結果
            </li>
            <li
              :class="[
                'stepper__item',
                currentStep === 'equipment' && 'is-active',
              ]"
            >
              3. 装備選択
            </li>
            <li
              :class="[
                'stepper__item',
                currentStep === 'result' && 'is-active',
              ]"
            >
              4. 配分結果
            </li>
          </ol>
        </nav>
      </header>

      <section class="noticeRegion" aria-live="polite">
        <Transition name="notice" mode="out-in">
          <div
            v-if="notice"
            :key="notice.key"
            :class="['notice', `is-${notice.kind}`]"
          >
            <strong class="notice__label">{{
              noticeLabel(notice.kind)
            }}</strong>
            <span class="notice__message">{{ notice.message }}</span>
            <button class="notice__close" type="button" @click="notice = null">
              ×
            </button>
          </div>
        </Transition>
      </section>

      <Transition name="step" mode="out-in">
        <section
          v-if="currentStep === 'members'"
          key="step-members"
          class="section"
        >
          <div class="panel__head">
            <h2>Phase 1: Member Selection</h2>
            <div class="panel__meta">
              <label class="field">
                <span class="field__label">チーム数</span>
                <select v-model.number="numTeams" class="field__control">
                  <option v-for="n in teamOptions" :key="n" :value="n">
                    {{ n }}
                  </option>
                </select>
              </label>
            </div>
          </div>

          <div class="card card--settings">
            <h3>班分け設定（重み）</h3>
            <p class="muted">
              係・運転・キャリア分散などの重みを調整して、班分けの傾向を変えられます。
            </p>

            <div class="sliderGrid">
              <div class="sliderRow">
                <div class="sliderRow__label">num_reads</div>
                <input
                  v-model.number="groupingSettings.num_reads"
                  class="sliderRow__range"
                  type="range"
                  min="100"
                  max="5000"
                  step="50"
                />
                <div class="sliderRow__value">
                  {{ groupingSettings.num_reads }}
                </div>
              </div>

              <div v-for="s in weightSliders" :key="s.key" class="sliderRow">
                <div class="sliderRow__label">{{ s.key }}</div>
                <input
                  :value="groupingSettings[s.key]"
                  class="sliderRow__range"
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  @input="
                    setGroupingWeight(
                      s.key,
                      ($event.target as HTMLInputElement).value
                    )
                  "
                />
                <div class="sliderRow__value">
                  {{ groupingSettings[s.key].toFixed(2) }}
                </div>
              </div>
            </div>
          </div>

          <div v-if="membersLoading" class="status">
            <div class="spinner" aria-hidden="true" />
            <p>メンバー一覧を取得中...</p>
          </div>

          <div v-else class="tableWrap">
            <table class="table">
              <thead>
                <tr>
                  <th class="table__check">
                    <input
                      aria-label="Select all members"
                      type="checkbox"
                      :checked="isAllMembersSelected"
                      :indeterminate.prop="isSomeMembersSelected"
                      @change="
                        toggleAllMembers(
                          ($event.target as HTMLInputElement).checked
                        )
                      "
                    />
                  </th>
                  <th>名前</th>
                  <th>学年</th>
                  <th>性別</th>
                  <th>固定係</th>
                  <th>CL/SL</th>
                  <th>運転</th>
                  <th>キャリア</th>
                  <th>経験年数</th>
                  <th class="table__actions">操作</th>
                </tr>
              </thead>

              <TransitionGroup name="row" tag="tbody">
                <tr v-for="m in members" :key="m.id" class="table__row">
                  <td class="table__check">
                    <input
                      :aria-label="`Select ${m.name}`"
                      type="checkbox"
                      :checked="selectedMemberIdSet.has(m.id)"
                      @change="
                        toggleMember(
                          m.id,
                          ($event.target as HTMLInputElement).checked
                        )
                      "
                    />
                  </td>
                  <td class="mono">{{ m.name }}</td>
                  <td>{{ m.grade }}</td>
                  <td>{{ genderLabel(m.gender) }}</td>
                  <td>{{ m.role_fixed ?? "-" }}</td>
                  <td>{{ m.role_authoritative ?? "-" }}</td>
                  <td>{{ m.driver ? "あり" : "なし" }}</td>
                  <td>{{ m.carrier ?? "-" }}</td>
                  <td>{{ m.exp_years }}</td>
                  <td class="table__actions">
                    <button
                      class="btn btn--ghost"
                      type="button"
                      @click="removeMember(m.id)"
                    >
                      削除
                    </button>
                  </td>
                </tr>
              </TransitionGroup>
            </table>
          </div>

          <div class="panel__split">
            <div class="card">
              <h3>選択中</h3>
              <p class="muted">
                {{ selectedMembers.length }}名 / {{ members.length }}名
              </p>
              <TransitionGroup name="chip" tag="div" class="chips">
                <span
                  v-for="m in selectedMembers"
                  :key="m.id"
                  class="chip"
                  :title="`${m.name} (${m.grade})`"
                >
                  {{ m.name }}
                </span>
              </TransitionGroup>
            </div>

            <div class="card">
              <h3>メンバー追加（シミュレーション）</h3>
              <form class="form" @submit.prevent="addMember()">
                <div class="form__grid">
                  <label class="field">
                    <span class="field__label">名前</span>
                    <input
                      v-model.trim="newMember.name"
                      class="field__control"
                      required
                    />
                  </label>
                  <label class="field">
                    <span class="field__label">学年</span>
                    <input
                      v-model.number="newMember.grade"
                      class="field__control"
                      type="number"
                      min="1"
                      max="6"
                      required
                    />
                  </label>
                  <label class="field">
                    <span class="field__label">性別</span>
                    <select v-model="newMember.gender" class="field__control">
                      <option value="male">male</option>
                      <option value="female">female</option>
                    </select>
                  </label>
                  <label class="field">
                    <span class="field__label">固定係</span>
                    <select
                      v-model="newMember.role_fixed"
                      class="field__control"
                    >
                      <option :value="null">(なし)</option>
                      <option value="equipment">equipment</option>
                      <option value="weather">weather</option>
                      <option value="meal">meal</option>
                    </select>
                  </label>
                  <label class="field">
                    <span class="field__label">CL/SL</span>
                    <select
                      v-model="newMember.role_authoritative"
                      class="field__control"
                    >
                      <option :value="null">(なし)</option>
                      <option value="CL">CL</option>
                      <option value="SL">SL</option>
                    </select>
                  </label>
                  <label class="field field--inline">
                    <span class="field__label">運転</span>
                    <input v-model="newMember.driver" type="checkbox" />
                  </label>
                  <label class="field">
                    <span class="field__label">キャリア</span>
                    <select v-model="newMember.carrier" class="field__control">
                      <option :value="null">(なし)</option>
                      <option value="docomo">docomo</option>
                      <option value="au">au</option>
                      <option value="softbank">softbank</option>
                      <option value="rakuten">rakuten</option>
                    </select>
                  </label>
                  <label class="field">
                    <span class="field__label">経験年数</span>
                    <input
                      v-model.number="newMember.exp_years"
                      class="field__control"
                      type="number"
                      min="0"
                      step="0.5"
                      required
                    />
                  </label>
                </div>
                <div class="form__actions">
                  <button class="btn" type="submit">追加</button>
                </div>
              </form>
            </div>
          </div>

          <div class="panel__actions">
            <button
              class="btn btn--primary"
              type="button"
              :disabled="selectedMembers.length === 0 || membersLoading"
              @click="runGrouping()"
            >
              班分けを実行
            </button>
          </div>
        </section>

        <section
          v-else-if="currentStep === 'grouping'"
          key="step-grouping"
          class="section"
        >
          <div class="panel__head">
            <h2>Phase 2: Grouping Visualization</h2>
            <p class="muted">選択したメンバーを班分けします。</p>
          </div>

          <div v-if="groupingLoading" class="status status--big">
            <div class="spinner spinner--pulse" aria-hidden="true" />
            <div>
              <h3>量子アニーリング中...</h3>
              <p class="muted">制約条件を満たす解を探索しています。</p>
            </div>
          </div>

          <div v-else-if="groupingError" class="card card--error">
            <h3>エラー</h3>
            <p>{{ groupingError }}</p>
          </div>

          <div v-else class="teamGrid">
            <TransitionGroup name="card" tag="div" class="teamGrid__inner">
              <article
                v-for="(team, idx) in teams"
                :key="`team-${idx}`"
                class="teamCard"
              >
                <header class="teamCard__head">
                  <h3>Team {{ String.fromCharCode(65 + idx) }}</h3>
                  <div
                    class="teamCard__score"
                    :title="'簡易スコア（フロント側の参考値）'"
                  >
                    Safety
                    <span class="teamCard__scoreValue">{{
                      safetyScore(team)
                    }}</span>
                  </div>
                </header>

                <dl class="teamCard__stats">
                  <div>
                    <dt>人数</dt>
                    <dd>{{ team.length }}</dd>
                  </div>
                  <div>
                    <dt>運転</dt>
                    <dd>{{ team.filter((m) => m.driver).length }}</dd>
                  </div>
                  <div>
                    <dt>キャリア</dt>
                    <dd>{{ carrierVariety(team) }}</dd>
                  </div>
                </dl>

                <TransitionGroup name="row" tag="ul" class="teamCard__members">
                  <li v-for="m in team" :key="m.id" class="memberRow">
                    <span class="memberRow__name">{{ m.name }}</span>
                    <span class="memberRow__meta">
                      {{ m.role_authoritative ?? "-" }} /
                      {{ m.role_fixed ?? "-" }} · {{ m.grade }}年 ·
                      {{ genderLabel(m.gender) }} · {{ m.exp_years }}年
                    </span>
                  </li>
                </TransitionGroup>
              </article>
            </TransitionGroup>
          </div>

          <div class="panel__actions panel__actions--between">
            <button
              class="btn btn--ghost"
              type="button"
              :disabled="groupingLoading"
              @click="goMemberSelection()"
            >
              メンバー選択に戻る
            </button>
            <button
              class="btn btn--primary"
              type="button"
              :disabled="!teams || teams.length === 0 || groupingLoading"
              @click="goEquipmentSelection()"
            >
              装備選択へ進む
            </button>
          </div>
        </section>

        <section
          v-else-if="currentStep === 'equipment'"
          key="step-equipment"
          class="section"
        >
          <div class="panel__head">
            <h2>Phase 3: Equipment Selection</h2>
            <p class="muted">装備一覧を選択して、配分最適化を実行します。</p>
          </div>

          <div class="card card--settings">
            <h3>装備配分設定（パラメータ）</h3>
            <p class="muted">
              配分最適化のパラメータをスライダーで調整できます。
            </p>

            <div class="sliderGrid">
              <div class="sliderRow">
                <div class="sliderRow__label">num_reads</div>
                <input
                  v-model.number="equipmentSettings.num_reads"
                  class="sliderRow__range"
                  type="range"
                  min="10"
                  max="5000"
                  step="10"
                />
                <div class="sliderRow__value">
                  {{ Math.round(equipmentSettings.num_reads) }}
                </div>
              </div>

              <div class="sliderRow">
                <div class="sliderRow__label">P</div>
                <input
                  v-model.number="equipmentSettings.P"
                  class="sliderRow__range"
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                />
                <div class="sliderRow__value">
                  {{ equipmentSettings.P.toFixed(2) }}
                </div>
              </div>

              <div class="sliderRow">
                <div class="sliderRow__label">weightWeight</div>
                <input
                  v-model.number="equipmentSettings.weightWeight"
                  class="sliderRow__range"
                  type="range"
                  min="0"
                  max="5"
                  step="0.1"
                />
                <div class="sliderRow__value">
                  {{ equipmentSettings.weightWeight.toFixed(1) }}
                </div>
              </div>
            </div>
          </div>

          <div v-if="equipmentsLoading" class="status">
            <div class="spinner" aria-hidden="true" />
            <p>装備一覧を取得中...</p>
          </div>

          <div v-else class="tableWrap">
            <table class="table">
              <thead>
                <tr>
                  <th class="table__check">
                    <input
                      aria-label="Select all equipments"
                      type="checkbox"
                      :checked="isAllEquipmentsSelected"
                      :indeterminate.prop="isSomeEquipmentsSelected"
                      @change="
                        toggleAllEquipments(
                          ($event.target as HTMLInputElement).checked
                        )
                      "
                    />
                  </th>
                  <th>名前</th>
                  <th>重量(kg)</th>
                  <th>容量(任意)</th>
                  <th class="table__actions">操作</th>
                </tr>
              </thead>

              <TransitionGroup name="row" tag="tbody">
                <tr v-for="e in equipments" :key="e.id" class="table__row">
                  <td class="table__check">
                    <input
                      :aria-label="`Select ${e.name}`"
                      type="checkbox"
                      :checked="selectedEquipmentIdSet.has(e.id)"
                      @change="
                        toggleEquipment(
                          e.id,
                          ($event.target as HTMLInputElement).checked
                        )
                      "
                    />
                  </td>
                  <td class="mono">{{ e.name }}</td>
                  <td>{{ e.weight }}</td>
                  <td>{{ e.capacity ?? "-" }}</td>
                  <td class="table__actions">
                    <button
                      class="btn btn--ghost"
                      type="button"
                      @click="removeEquipment(e.id)"
                    >
                      削除
                    </button>
                  </td>
                </tr>
              </TransitionGroup>
            </table>
          </div>

          <div class="panel__split">
            <div class="card">
              <h3>選択中</h3>
              <p class="muted">
                {{ selectedEquipments.length }}件 / {{ equipments.length }}件
              </p>
              <TransitionGroup name="chip" tag="div" class="chips">
                <span v-for="e in selectedEquipments" :key="e.id" class="chip">
                  {{ e.name }}
                </span>
              </TransitionGroup>
            </div>

            <div class="card">
              <h3>装備追加（シミュレーション）</h3>
              <form class="form" @submit.prevent="addEquipment()">
                <div class="form__grid">
                  <label class="field">
                    <span class="field__label">名前</span>
                    <input
                      v-model.trim="newEquipment.name"
                      class="field__control"
                      required
                    />
                  </label>
                  <label class="field">
                    <span class="field__label">重量(kg)</span>
                    <input
                      v-model.number="newEquipment.weight"
                      class="field__control"
                      type="number"
                      min="0.1"
                      step="0.1"
                      required
                    />
                  </label>
                  <label class="field">
                    <span class="field__label">容量(任意)</span>
                    <input
                      v-model.number="newEquipment.capacity"
                      class="field__control"
                      type="number"
                      min="0"
                      step="0.1"
                    />
                  </label>
                </div>
                <div class="form__actions">
                  <button class="btn" type="submit">追加</button>
                </div>
              </form>
            </div>
          </div>

          <div class="panel__actions">
            <button
              class="btn btn--primary"
              type="button"
              :disabled="selectedEquipments.length === 0 || equipmentsLoading"
              @click="runEquipmentAllocation()"
            >
              配分最適化を実行
            </button>
          </div>
        </section>

        <section v-else key="step-result" class="panel">
          <div class="panel__head">
            <h2>Phase 4: Final Allocation Result</h2>
            <p class="muted">誰が何を持つかを表示します。</p>
          </div>

          <div v-if="allocationLoading" class="status status--big">
            <div class="spinner spinner--pulse" aria-hidden="true" />
            <div>
              <h3>配分最適化中...</h3>
              <p class="muted">装備の割り当てを探索しています。</p>
            </div>
          </div>

          <div v-else-if="allocationError" class="card card--error">
            <h3>エラー</h3>
            <p>{{ allocationError }}</p>
          </div>

          <div v-else class="result">
            <div class="panel__actions panel__actions--between">
              <button
                class="btn btn--ghost"
                type="button"
                :disabled="allocationLoading"
                @click="goEquipmentSelectionFromResult()"
              >
                装備選択に戻る
              </button>
            </div>
            <div class="result__summary card">
              <h3>サマリー</h3>
              <dl class="summary">
                <div>
                  <dt>チーム数</dt>
                  <dd>{{ teams.length }}</dd>
                </div>
                <div>
                  <dt>メンバー数</dt>
                  <dd>{{ selectedMembers.length }}</dd>
                </div>
                <div>
                  <dt>装備数</dt>
                  <dd>{{ selectedEquipments.length }}</dd>
                </div>
              </dl>
              <p class="muted">
                Safetyスコアはフロント側の簡易計算（参考値）です。
              </p>
            </div>

            <div class="teamGrid">
              <div class="teamGrid__inner">
                <article
                  v-for="(team, idx) in teams"
                  :key="`alloc-team-${idx}`"
                  class="teamCard"
                >
                  <header class="teamCard__head">
                    <h3>Team {{ String.fromCharCode(65 + idx) }}</h3>
                    <div class="teamCard__score">
                      Safety
                      <span class="teamCard__scoreValue">{{
                        safetyScore(team)
                      }}</span>
                    </div>
                  </header>

                  <div class="allocList">
                    <div v-for="m in team" :key="m.id" class="allocRow">
                      <div class="allocRow__head">
                        <div class="allocRow__name">{{ m.name }}</div>
                        <div class="allocRow__weight">
                          {{ memberTotalWeight(m.id).toFixed(1) }} kg
                        </div>
                      </div>
                      <ul class="allocRow__items">
                        <li
                          v-for="eq in allocationByMemberId.get(m.id) ?? []"
                          :key="eq.id"
                        >
                          {{ eq.name }}
                          <span class="muted">({{ eq.weight }}kg)</span>
                        </li>
                        <li
                          v-if="
                            (allocationByMemberId.get(m.id) ?? []).length === 0
                          "
                          class="muted"
                        >
                          (割り当てなし)
                        </li>
                      </ul>
                    </div>
                  </div>
                </article>
              </div>
            </div>
          </div>
        </section>
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { EquipmentAPI, EquipmentAssignmentAPI, MemberAPI } from "~/types";
import { useQsherpaApi } from "~/composables/useQsherpaApi";

useSeoMeta({
  title: "Demo",
});

useHead({
  bodyAttrs: {
    class: "demo-body",
  },
});

type Step = "members" | "grouping" | "equipment" | "result";
type NoticeKind = "success" | "error" | "info" | 200 | 201;

const { fetchMembers, fetchEquipments, postGrouping, postEquipmentAllocation } =
  useQsherpaApi();

const currentStep = ref<Step>("members");
const teamOptions = [2, 3, 4, 5, 6, 7, 8];
const numTeams = ref<number>(7);

type GroupingSettingsKey =
  | "groupSizeWeight"
  | "gradePopulationWeight"
  | "genderShouldBeZeroWeight"
  | "genderPairBonusWeight"
  | "rolePopulationWeight"
  | "driverPopulationWeight"
  | "carrierPopulationWeight"
  | "interTeamExperienceSimilarityWeight"
  | "intraTeamExperienceSimilarityWeight";

const weightSliders = [
  { key: "groupSizeWeight" },
  { key: "gradePopulationWeight" },
  { key: "genderShouldBeZeroWeight" },
  { key: "genderPairBonusWeight" },
  { key: "rolePopulationWeight" },
  { key: "driverPopulationWeight" },
  { key: "carrierPopulationWeight" },
  { key: "interTeamExperienceSimilarityWeight" },
  { key: "intraTeamExperienceSimilarityWeight" },
] as const satisfies ReadonlyArray<{ key: GroupingSettingsKey }>;

const groupingSettings = ref<
  { num_reads: number } & Record<GroupingSettingsKey, number>
>({
  num_reads: 3000,
  groupSizeWeight: 0.04,
  gradePopulationWeight: 0.03,
  genderShouldBeZeroWeight: 0,
  genderPairBonusWeight: 0,
  rolePopulationWeight: 0.06,
  driverPopulationWeight: 0.03,
  carrierPopulationWeight: 0.02,
  interTeamExperienceSimilarityWeight: 0,
  intraTeamExperienceSimilarityWeight: 0.02,
});

const setGroupingWeight = (key: GroupingSettingsKey, raw: string) => {
  const value = Number(raw);
  groupingSettings.value = {
    ...groupingSettings.value,
    [key]: Number.isFinite(value) ? value : groupingSettings.value[key],
  };
};

type EquipmentSettings = {
  num_reads: number;
  P: number;
  weightWeight: number;
};

const clamp = (v: number, min: number, max: number) =>
  Math.max(min, Math.min(max, v));

const equipmentSettings = ref<EquipmentSettings>({
  num_reads: 100,
  P: 0.5,
  weightWeight: 1,
});

const notice = ref<null | { key: string; kind: NoticeKind; message: string }>(
  null
);
const showNotice = (kind: NoticeKind, message: string) => {
  notice.value = { key: `${Date.now()}-${kind}`, kind, message };
};
const noticeLabel = (kind: NoticeKind) =>
  kind === "success" ? "成功" : kind === "error" ? "エラー" : "情報";

type ErrorDataLike = { detail?: unknown };
const asObject = (v: unknown): Record<string, unknown> | null =>
  v && typeof v === "object" ? (v as Record<string, unknown>) : null;
const getErrorMessage = (err: unknown, fallback: string) => {
  const obj = asObject(err);
  if (!obj) return fallback;
  const data = obj.data as unknown;
  const dataObj = asObject(data) as ErrorDataLike | null;
  const detail = dataObj?.detail;
  if (typeof detail === "string" && detail.length > 0) return detail;
  const msg = obj.message;
  if (typeof msg === "string" && msg.length > 0) return msg;
  return fallback;
};

// --- Phase 1: members ---
const membersLoading = ref(false);
const members = ref<MemberAPI[]>([]);
const selectedMemberIds = ref<number[]>([]);
const selectedMemberIdSet = computed(() => new Set(selectedMemberIds.value));

const newMember = ref<MemberAPI>({
  id: -1,
  name: "",
  grade: 1,
  gender: "male",
  role_fixed: null,
  role_authoritative: null,
  driver: false,
  carrier: null,
  exp_years: 0.5,
});

const selectedMembers = computed(() =>
  members.value.filter((m) => selectedMemberIdSet.value.has(m.id))
);
const isAllMembersSelected = computed(
  () =>
    members.value.length > 0 &&
    selectedMembers.value.length === members.value.length
);
const isSomeMembersSelected = computed(
  () =>
    selectedMembers.value.length > 0 &&
    selectedMembers.value.length < members.value.length
);

const toggleMember = (id: number, checked: boolean) => {
  const set = new Set(selectedMemberIds.value);
  if (checked) set.add(id);
  else set.delete(id);
  selectedMemberIds.value = [...set];
};

const toggleAllMembers = (checked: boolean) => {
  selectedMemberIds.value = checked ? members.value.map((m) => m.id) : [];
};

const removeMember = (id: number) => {
  members.value = members.value.filter((m) => m.id !== id);
  selectedMemberIds.value = selectedMemberIds.value.filter((x) => x !== id);
  showNotice("info", "メンバーを削除しました（UI上のシミュレーション）");
};

const addMember = () => {
  if (!newMember.value.name) return;
  const maxId = members.value.reduce((acc, m) => Math.max(acc, m.id), 0);
  const nextId = Math.max(maxId + 1, 1);
  const added: MemberAPI = {
    ...newMember.value,
    id: nextId,
    role_fixed: newMember.value.role_fixed ?? null,
    role_authoritative: newMember.value.role_authoritative ?? null,
    carrier: newMember.value.carrier ?? null,
  };
  members.value = [added, ...members.value];
  showNotice("success", "メンバーを追加しました（UI上のシミュレーション）");
  newMember.value = {
    id: -1,
    name: "",
    grade: 1,
    gender: "male",
    role_fixed: null,
    role_authoritative: null,
    driver: false,
    carrier: null,
    exp_years: 0.5,
  };
};

const genderLabel = (g: string) =>
  g === "male" ? "male" : g === "female" ? "female" : g;

const normalizeGender = (g: unknown): "male" | "female" | string => {
  if (g === "M") return "male";
  if (g === "F") return "female";
  if (g === "male" || g === "female") return g;
  return typeof g === "string" ? g : "male";
};

const loadMembers = async () => {
  membersLoading.value = true;
  try {
    const res = await fetchMembers();
    members.value = res.map((m) => ({
      ...m,
      gender: normalizeGender(m.gender),
      driver: Boolean(m.driver),
    }));
    showNotice(200, "メンバー一覧を取得しました");
  } catch (err: unknown) {
    showNotice("error", getErrorMessage(err, "メンバー取得に失敗しました"));
  } finally {
    membersLoading.value = false;
  }
};

// --- Phase 2: grouping ---
const groupingLoading = ref(false);
const groupingError = ref<string | null>(null);
const teams = ref<MemberAPI[][]>([]);

const carrierVariety = (team: MemberAPI[]) => {
  const carriers = team.map((m) => m.carrier).filter(Boolean) as string[];
  return new Set(carriers).size;
};

const safetyScore = (team: MemberAPI[]) => {
  const hasCL = team.some((m) => m.role_authoritative === "CL");
  const hasSL = team.some((m) => m.role_authoritative === "SL");
  const drivers = team.filter((m) => m.driver).length;
  const carriers = carrierVariety(team);
  const roleFixedKinds = new Set(team.map((m) => m.role_fixed).filter(Boolean))
    .size;

  // Very small, intentionally simple heuristic score for UX (not from API)
  let score = 50;
  score += hasCL ? 15 : -10;
  score += hasSL ? 15 : -10;
  score += Math.min(drivers, 2) * 5;
  score += Math.min(carriers, 3) * 3;
  score += Math.min(roleFixedKinds, 3) * 2;
  score = Math.max(0, Math.min(100, Math.round(score)));
  return score;
};

const runGrouping = async () => {
  groupingError.value = null;
  teams.value = [];

  if (selectedMembers.value.length === 0) {
    showNotice("error", "メンバーを1名以上選択してください");
    return;
  }
  if (!teamOptions.includes(numTeams.value)) {
    showNotice("error", "チーム数が不正です");
    return;
  }

  currentStep.value = "grouping";
  groupingLoading.value = true;
  try {
    const res = await postGrouping({
      members: selectedMembers.value,
      numTeams: numTeams.value,
      settings: {
        ...groupingSettings.value,
        num_reads: Math.round(groupingSettings.value.num_reads),
      },
    });
    teams.value = res;
    showNotice(200, "班分けが完了しました");
  } catch (err: unknown) {
    const message = getErrorMessage(err, "班分けに失敗しました");
    groupingError.value = message;
    showNotice("error", message);
  } finally {
    groupingLoading.value = false;
  }
};

const goEquipmentSelection = async () => {
  currentStep.value = "equipment";
  await loadEquipments();
};

const goMemberSelection = () => {
  // Reset the visualization state so the user can tweak inputs and rerun.
  groupingError.value = null;
  teams.value = [];
  currentStep.value = "members";
};

// --- Phase 3: equipments ---
const equipmentsLoading = ref(false);
const equipments = ref<EquipmentAPI[]>([]);
const selectedEquipmentIds = ref<number[]>([]);
const selectedEquipmentIdSet = computed(
  () => new Set(selectedEquipmentIds.value)
);

const newEquipment = ref<EquipmentAPI>({
  id: -1,
  name: "",
  weight: 1.0,
  capacity: null,
});

const selectedEquipments = computed(() =>
  equipments.value.filter((e) => selectedEquipmentIdSet.value.has(e.id))
);
const isAllEquipmentsSelected = computed(
  () =>
    equipments.value.length > 0 &&
    selectedEquipments.value.length === equipments.value.length
);
const isSomeEquipmentsSelected = computed(
  () =>
    selectedEquipments.value.length > 0 &&
    selectedEquipments.value.length < equipments.value.length
);

const toggleEquipment = (id: number, checked: boolean) => {
  const set = new Set(selectedEquipmentIds.value);
  if (checked) set.add(id);
  else set.delete(id);
  selectedEquipmentIds.value = [...set];
};
const toggleAllEquipments = (checked: boolean) => {
  selectedEquipmentIds.value = checked ? equipments.value.map((e) => e.id) : [];
};

const removeEquipment = (id: number) => {
  equipments.value = equipments.value.filter((e) => e.id !== id);
  selectedEquipmentIds.value = selectedEquipmentIds.value.filter(
    (x) => x !== id
  );
  showNotice("info", "装備を削除しました（UI上のシミュレーション）");
};

const addEquipment = () => {
  if (!newEquipment.value.name) return;
  const maxId = equipments.value.reduce((acc, e) => Math.max(acc, e.id), 0);
  const nextId = Math.max(maxId + 1, 1);
  const added: EquipmentAPI = {
    ...newEquipment.value,
    id: nextId,
    capacity: newEquipment.value.capacity ?? null,
  };
  equipments.value = [added, ...equipments.value];
  showNotice("success", "装備を追加しました（UI上のシミュレーション）");
  newEquipment.value = { id: -1, name: "", weight: 1.0, capacity: null };
};

const loadEquipments = async () => {
  equipmentsLoading.value = true;
  try {
    const res = await fetchEquipments();
    equipments.value = res;
    showNotice(200, "装備一覧を取得しました");
  } catch (err: unknown) {
    showNotice("error", getErrorMessage(err, "装備取得に失敗しました"));
  } finally {
    equipmentsLoading.value = false;
  }
};

// --- Phase 4: allocation ---
const allocationLoading = ref(false);
const allocationError = ref<string | null>(null);
const allocation = ref<EquipmentAssignmentAPI[]>([]);
const allocationByMemberId = computed(() => {
  const map = new Map<number, EquipmentAPI[]>();
  for (const row of allocation.value) {
    map.set(row.member.id, row.equipment);
  }
  return map;
});

const memberTotalWeight = (memberId: number) => {
  const items = allocationByMemberId.value.get(memberId) ?? [];
  return items.reduce((sum, eq) => sum + (Number(eq.weight) || 0), 0);
};

const runEquipmentAllocation = async () => {
  allocationError.value = null;
  allocation.value = [];

  if (!teams.value || teams.value.length === 0) {
    showNotice(
      "error",
      "班分け結果がありません。先に班分けを実行してください。"
    );
    currentStep.value = "members";
    return;
  }
  if (selectedEquipments.value.length === 0) {
    showNotice("error", "装備を1件以上選択してください");
    return;
  }

  currentStep.value = "result";
  allocationLoading.value = true;
  try {
    const res = await postEquipmentAllocation({
      teams: teams.value,
      equipments: selectedEquipments.value,
      settings: {
        num_reads: Math.max(1, Math.round(equipmentSettings.value.num_reads)),
        P: clamp(Number(equipmentSettings.value.P), 0, 1),
        weightWeight: Number(equipmentSettings.value.weightWeight),
      },
    });
    allocation.value = res;
    showNotice(200, "配分最適化が完了しました");
  } catch (err: unknown) {
    const message = getErrorMessage(err, "配分最適化に失敗しました");
    allocationError.value = message;
    showNotice("error", message);
  } finally {
    allocationLoading.value = false;
  }
};

const goEquipmentSelectionFromResult = () => {
  // Reset allocation output so rerunning feels explicit.
  allocationError.value = null;
  allocation.value = [];
  currentStep.value = "equipment";
};

onMounted(async () => {
  await loadMembers();
});
</script>

<style scoped lang="scss">
:global(body.demo-body) {
  background: $surface;
}

.demo {
  max-width: 1100px;
  margin: 1.5rem auto 3rem;
}

.island {
  background: $color-bg-primary;
  border: 1px solid rgba($color-border, 0.85);
  border-radius: 16px;
  padding: 1.25rem;
}

.hero {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1rem;
}

.hero__title {
  padding: 0 0.25rem;

  h1 {
    color: $on-surface-variant;
    font-size: 1.4rem;
    margin-bottom: 0.25rem;
  }
  p {
    color: $on-surface;
    line-height: 1.6;
  }
}

.stepper {
  padding: 0.25rem 0;
}

.stepper__list {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.5rem;
  list-style: none;
}

.stepper__item {
  color: $on-surface;
  font-size: 0.9rem;
  padding: 0.5rem 0.75rem;
  border-radius: 10px;
  border: 1px dashed rgba($color-border, 0.8);
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;

  &.is-active {
    border-style: solid;
    border-color: rgba($primary, 0.9);
    color: $on-surface-variant;
    background: rgba($primary, 0.1);
    font-weight: 700;
  }
}

.noticeRegion {
  margin: 0.75rem 0 0.25rem;
}

.section {
  padding: 0.75rem 0;
}

.panel__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;

  h2 {
    color: $on-surface-variant;
    font-size: 1.2rem;
  }
}

.panel__meta {
  display: flex;
  gap: 0.75rem;
}

.panel__actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 1rem;
  gap: 0.75rem;
}

.panel__actions--between {
  justify-content: space-between;
}

.panel__split {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-top: 1rem;
}

.card {
  background: transparent;
  border: 1px solid rgba($color-border, 0.65);
  border-radius: 12px;
  padding: 1rem;

  h3 {
    color: $on-surface-variant;
    font-size: 1rem;
    margin-bottom: 0.25rem;
  }

  &.card--error {
    border-color: rgba($error, 0.9);
    background: rgba($error, 0.06);
  }
}

.card--settings {
  margin-bottom: 1rem;
}

.sliderGrid {
  display: grid;
  gap: 0.6rem;
  margin-top: 0.75rem;
}

.sliderRow {
  display: grid;
  grid-template-columns: minmax(180px, 260px) 1fr 70px;
  align-items: center;
  gap: 0.75rem;
  padding: 0.55rem 0.65rem;
  border-radius: 12px;
  border: 1px solid rgba($color-border, 0.55);
  background: rgba($surface, 0.55);
}

.sliderRow__label {
  font-size: 0.85rem;
  color: $on-surface-variant;
  font-weight: 700;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sliderRow__value {
  text-align: right;
  font-variant-numeric: tabular-nums;
  color: $on-surface-variant;
  font-weight: 800;
}

.sliderRow__range {
  width: 100%;
  accent-color: $primary;
}

.muted {
  color: $on-surface;
  opacity: 0.9;
}

.tableWrap {
  overflow: auto;
  border-radius: 12px;
  border: 1px solid rgba($color-border, 0.7);
  background: transparent;
}

.table {
  width: 100%;
  border-collapse: collapse;
  min-width: 820px;

  thead th {
    position: sticky;
    top: 0;
    background: $color-bg-primary;
    text-align: left;
    font-size: 0.85rem;
    padding: 0.75rem 0.75rem;
    color: $on-surface-variant;
    border-bottom: 1px solid rgba($color-border, 0.8);
  }

  tbody td {
    padding: 0.65rem 0.75rem;
    border-bottom: 1px solid rgba($color-border, 0.55);
    font-size: 0.9rem;
    color: $on-surface-variant;
  }
}

.table__row {
  transition: background 120ms ease;
  &:hover {
    background: rgba($primary, 0.08);
  }
}

.table__check {
  width: 44px;
}

.table__actions {
  width: 90px;
  text-align: right;
}

.mono {
  font-variant-numeric: tabular-nums;
}

.chips {
  display: flex;
  gap: 0.4rem;
  flex-wrap: wrap;
  margin-top: 0.5rem;
}

.chip {
  display: inline-flex;
  align-items: center;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  background: rgba($secondary, 0.08);
  border: 1px solid rgba($secondary, 0.25);
  color: $on-surface-variant;
  font-size: 0.85rem;
}

.form {
  margin-top: 0.5rem;
}

.form__grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.form__actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 0.75rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.field--inline {
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}

.field__label {
  font-size: 0.85rem;
  color: $on-surface;
}

.field__control {
  border-radius: 10px;
  border: 1px solid rgba($color-border, 0.8);
  background: rgba($color-bg-primary, 0.9);
  padding: 0.55rem 0.65rem;
  color: $on-surface-variant;
  outline: none;

  &:focus {
    border-color: rgba($primary, 0.8);
    box-shadow: 0 0 0 3px rgba($primary, 0.12);
  }
}

.btn {
  border-radius: 10px;
  border: 1px solid rgba($color-border, 0.8);
  background: rgba($color-bg-primary, 0.9);
  padding: 0.55rem 0.8rem;
  color: $on-surface-variant;
  cursor: pointer;
  transition: transform 80ms ease, background 120ms ease;

  &:hover {
    background: rgba($primary, 0.08);
  }
  &:active {
    transform: translateY(1px);
  }
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.btn--ghost {
  background: transparent;
}

.btn--primary {
  background: rgba($primary, 0.14);
  border-color: rgba($primary, 0.6);
}

.status {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
}

.status--big {
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid rgba($color-border, 0.7);
  background: transparent;
}

.spinner {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 3px solid rgba($primary, 0.18);
  border-top-color: rgba($primary, 0.85);
  animation: spin 0.9s linear infinite;
}

.spinner--pulse {
  width: 22px;
  height: 22px;
  animation: spin 0.9s linear infinite, pulse 1.2s ease-in-out infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes pulse {
  0%,
  100% {
    transform: scale(1) rotate(0deg);
  }
  50% {
    transform: scale(1.06) rotate(180deg);
  }
}

.teamGrid {
  margin-top: 0.5rem;
}

.teamGrid__inner {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.teamCard {
  border: 1px solid rgba($color-border, 0.7);
  border-radius: 12px;
  padding: 1rem;
}

.teamCard__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;

  h3 {
    margin: 0;
    color: $on-surface-variant;
    font-size: 1.05rem;
  }
}

.teamCard__score {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  border-radius: 999px;
  padding: 0.15rem 0.6rem;
  border: 1px solid rgba($primary, 0.35);
  background: rgba($primary, 0.1);
  color: $on-surface-variant;
  font-size: 0.85rem;
}

.teamCard__scoreValue {
  font-variant-numeric: tabular-nums;
  font-weight: 800;
}

.teamCard__stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.5rem;
  margin: 0.75rem 0;

  dt {
    font-size: 0.75rem;
    color: $on-surface;
  }
  dd {
    margin: 0;
    color: $on-surface-variant;
    font-weight: 700;
  }
}

.teamCard__members {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.memberRow {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.45rem 0.55rem;
  border-radius: 10px;
  border: 1px solid rgba($color-border, 0.55);
  background: transparent;
}

.memberRow__name {
  font-weight: 700;
  color: $on-surface-variant;
}

.memberRow__meta {
  font-size: 0.82rem;
  color: $on-surface;
}

.result {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.75rem;

  dt {
    font-size: 0.75rem;
    color: $on-surface;
  }
  dd {
    margin: 0;
    font-weight: 800;
    color: $on-surface-variant;
  }
}

.allocList {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 0.75rem;
}

.allocRow {
  border-radius: 12px;
  border: 1px solid rgba($color-border, 0.55);
  background: transparent;
  padding: 0.75rem;
}

.allocRow__head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.75rem;
}

.allocRow__name {
  font-weight: 800;
  color: $on-surface-variant;
}

.allocRow__weight {
  font-variant-numeric: tabular-nums;
  color: $on-surface;
}

.allocRow__items {
  margin-top: 0.4rem;
  padding-left: 1.1rem;
  color: $on-surface-variant;
}

.notice {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  border-radius: 12px;
  border: 1px solid rgba($color-border, 0.7);
  background: transparent;
  padding: 0.75rem 0.9rem;
}

.notice__label {
  display: inline-flex;
  min-width: 3rem;
  justify-content: center;
  font-size: 0.85rem;
  border-radius: 999px;
  padding: 0.1rem 0.55rem;
  border: 1px solid rgba($color-border, 0.8);
  background: rgba($surface, 0.75);
}

.notice__message {
  flex: 1;
  color: $on-surface-variant;
}

.notice__close {
  appearance: none;
  border: none;
  background: transparent;
  cursor: pointer;
  color: $on-surface;
  font-size: 1.1rem;
  line-height: 1;
}

.notice.is-success {
  border-color: rgba($success, 0.7);
}

.notice.is-error {
  border-color: rgba($error, 0.7);
}

.notice.is-info {
  border-color: rgba($secondary, 0.55);
}

/* Step transition */
.step-enter-active,
.step-leave-active {
  transition: opacity 180ms ease, transform 180ms ease;
}
.step-enter-from,
.step-leave-to {
  opacity: 0;
  transform: translateY(6px);
}

/* Notice transition */
.notice-enter-active,
.notice-leave-active {
  transition: opacity 140ms ease, transform 140ms ease;
}
.notice-enter-from,
.notice-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

/* Row / chip / card transitions */
.row-enter-active,
.row-leave-active,
.chip-enter-active,
.chip-leave-active,
.card-enter-active,
.card-leave-active {
  transition: opacity 160ms ease, transform 160ms ease;
}
.row-enter-from,
.row-leave-to,
.chip-enter-from,
.chip-leave-to,
.card-enter-from,
.card-leave-to {
  opacity: 0;
  transform: translateY(6px);
}
.row-move,
.chip-move,
.card-move {
  transition: transform 180ms ease;
}

@media (max-width: 960px) {
  .panel__split {
    grid-template-columns: 1fr;
  }
  .teamGrid__inner {
    grid-template-columns: 1fr;
  }
  .stepper__list {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 560px) {
  .sliderRow {
    grid-template-columns: 1fr;
    gap: 0.35rem;
    align-items: stretch;
  }
  .sliderRow__value {
    text-align: left;
  }
}
</style>

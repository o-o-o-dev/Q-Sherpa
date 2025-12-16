import type {
  EquipmentAPI,
  EquipmentAssignmentAPI,
  GroupingAPIResponse,
  MemberAPI,
} from "~/types";

type GroupingSettings = {
  num_reads?: number;
  groupSizeWeight?: number;
  gradePopulationWeight?: number;
  genderShouldBeZeroWeight?: number;
  genderPairBonusWeight?: number;
  rolePopulationWeight?: number;
  driverPopulationWeight?: number;
  carrierPopulationWeight?: number;
  interTeamExperienceSimilarityWeight?: number;
  intraTeamExperienceSimilarityWeight?: number;
};

type EquipmentSettings = {
  num_reads?: number;
  P?: number;
  weightWeight?: number;
};

export function useQsherpaApi() {
  const config = useRuntimeConfig();
  const apiBase = (config.public.apiBase as string) || "/api";

  const fetchMembers = async () => {
    return await $fetch<MemberAPI[]>(`${apiBase}/members`);
  };

  const fetchEquipments = async () => {
    return await $fetch<EquipmentAPI[]>(`${apiBase}/equipment`);
  };

  const postGrouping = async (params: {
    members: MemberAPI[];
    numTeams: number;
    settings?: GroupingSettings;
  }) => {
    return await $fetch<GroupingAPIResponse>(`${apiBase}/grouping`, {
      method: "POST",
      body: {
        members: params.members,
        num_teams: params.numTeams,
        settings: params.settings ?? {},
      },
    });
  };

  const postEquipmentAllocation = async (params: {
    teams: GroupingAPIResponse;
    equipments: EquipmentAPI[];
    settings?: EquipmentSettings;
  }) => {
    return await $fetch<EquipmentAssignmentAPI[]>(`${apiBase}/equipment`, {
      method: "POST",
      body: {
        teams: params.teams,
        equipments: params.equipments,
        settings: params.settings ?? {},
      },
    });
  };

  return {
    fetchMembers,
    fetchEquipments,
    postGrouping,
    postEquipmentAllocation,
  };
}

// バックエンドAPIのレスポンス型
export interface MemberAPI {
  id: number;
  name: string;
  grade: number;
  gender: string;
  role_fixed?: "equipment" | "weather" | "meal" | null;
  role_authoritative?: "SL" | "CL" | null;
  driver: boolean;
  carrier?: "docomo" | "au" | "softbank" | "rakuten" | null;
  exp_years: number;
}

// フロントエンド用の型（UIで使用）
export interface Member {
  id: number;
  name: string;
  grade: number;
  role: "CL" | "SL" | "Equip" | "Food" | "Medic" | "Member";
  gender: "M" | "F";
  driver: boolean;
  carrier: "docomo" | "au" | "SoftBank" | "Rakuten" | "Other";
  exp_years: number;
}

// バックエンドAPIのレスポンス型
export interface EquipmentAPI {
  id: number;
  name: string;
  weight: number;
  capacity?: number | null;
}

// フロントエンド用の型（UIで使用）
export interface Equipment {
  id: string;
  name: string;
  capacity: number;
  weight_kg: number;
}

export interface OptimizeRequest {
  members: Member[];
  equipments: Equipment[];
  num_teams: number;
}

export interface OptimizeResponse {
  teams: Record<
    string,
    {
      members: string[];
      tent: string;
      safety_score: number;
    }
  >;
  packing_list: Record<
    string,
    {
      items: string[];
      total_weight: number;
      load_ratio: number;
    }
  >;
}

export interface Team {
  name: string;
  members: Member[];
  tent?: string;
  safety_score?: number;
}

export interface GroupingResponse {
  teams: Team[];
  message?: string;
}

// バックエンドのグループ化レスポンス（List[List[Member]]）
export type GroupingAPIResponse = MemberAPI[][];

export interface AllocationItem {
  equipment_name: string;
  weight_kg: number;
}

export interface MemberAllocation {
  member_name: string;
  items: AllocationItem[];
  total_weight: number;
  load_ratio: number;
  capacity_score: number;
}

export interface FinalAllocationResponse {
  allocations: MemberAllocation[];
  teams: Team[];
}

// バックエンドの装備配分レスポンス（List[EquipmentAssignment]）
export interface EquipmentAssignmentAPI {
  member: MemberAPI;
  equipment: EquipmentAPI[];
}

export type FinalAllocationAPIResponse = EquipmentAssignmentAPI[];

declare module "#app" {
  interface NuxtApp {
    $typesetMath?: () => Promise<void>;
  }
}

declare module "vue" {
  interface ComponentCustomProperties {
    $typesetMath?: () => Promise<void>;
  }
}

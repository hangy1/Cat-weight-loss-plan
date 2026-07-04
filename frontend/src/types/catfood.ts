export interface CatFood {
  id: number;
  name: string;
  brand: string | null;
  type: 'wet' | 'dry' | null;
  protein_pct: number | null;
  fat_pct: number | null;
  moisture_pct: number | null;
  kcal_per_kg: number | null;
  kcal_per_serving: number | null;
  serving_unit: string | null;
}

export interface CatFoodDetail extends CatFood {
  url: string | null;
  fiber_pct: number | null;
  ash_pct: number | null;
  taurine_pct: number | null;
  ga_basis: string | null;
  sizes: Array<{
    size: string;
    price: number | null;
  }>;
}

export interface ServingCalculationRequest {
  product_id: number;
  amount: number;
  unit: string;
}

export interface ServingCalculationResponse {
  product_id: number;
  product_name: string;
  amount: number;
  unit: string;
  grams: number;
  calories: number | null;
  protein_g: number | null;
  fat_g: number | null;
  fiber_g: number | null;
  moisture_g: number | null;
  protein_pct: number | null;
  fat_pct: number | null;
  fiber_pct: number | null;
  moisture_pct: number | null;
}

export interface MealPlanItem {
  id: string;
  food: CatFood;
  amount: number;
  unit: string;
  nutrition: ServingCalculationResponse | null;
}

export interface AllowedUnitsResponse {
  food_type: string;
  allowed_units: string[];
  note: string | null;
}

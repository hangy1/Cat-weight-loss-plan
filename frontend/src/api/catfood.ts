import type {
  CatFood,
  CatFoodDetail,
  ServingCalculationRequest,
  ServingCalculationResponse,
  AllowedUnitsResponse,
} from '../types/catfood';

const API_BASE_URL = 'http://localhost:8000/api';

export const catfoodApi = {
  /**
   * Search for cat foods
   */
  async searchFoods(params: {
    query?: string;
    brand?: string;
    food_type?: 'wet' | 'dry';
    limit?: number;
  }): Promise<CatFood[]> {
    const searchParams = new URLSearchParams();
    if (params.query) searchParams.append('query', params.query);
    if (params.brand) searchParams.append('brand', params.brand);
    if (params.food_type) searchParams.append('food_type', params.food_type);
    if (params.limit) searchParams.append('limit', params.limit.toString());

    const response = await fetch(`${API_BASE_URL}/catfood/search?${searchParams}`);
    if (!response.ok) {
      throw new Error('Failed to search foods');
    }
    return response.json();
  },

  /**
   * Get food details by ID
   */
  async getFoodById(id: number): Promise<CatFoodDetail> {
    const response = await fetch(`${API_BASE_URL}/catfood/${id}`);
    if (!response.ok) {
      throw new Error('Failed to get food details');
    }
    return response.json();
  },

  /**
   * Get allowed units for food type
   */
  async getAllowedUnits(foodType: 'wet' | 'dry'): Promise<AllowedUnitsResponse> {
    const response = await fetch(`${API_BASE_URL}/catfood/units/${foodType}`);
    if (!response.ok) {
      throw new Error('Failed to get allowed units');
    }
    return response.json();
  },

  /**
   * Get all brands
   */
  async getBrands(): Promise<string[]> {
    const response = await fetch(`${API_BASE_URL}/catfood/brands`);
    if (!response.ok) {
      throw new Error('Failed to get brands');
    }
    return response.json();
  },

  /**
   * Calculate nutrition for a serving
   */
  async calculateServing(
    request: ServingCalculationRequest
  ): Promise<ServingCalculationResponse> {
    const response = await fetch(`${API_BASE_URL}/catfood/calculate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to calculate nutrition');
    }

    return response.json();
  },
};

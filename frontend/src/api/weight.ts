import type {
  WeightEntry,
  WeightEntryCreate,
  WeightEntryUpdate,
  WeightEntryList,
} from '../types/weight';

const API_BASE_URL = 'http://localhost:8000/api';

export const weightApi = {
  /**
   * Get all weight entries
   */
  async getAllEntries(): Promise<WeightEntryList> {
    const response = await fetch(`${API_BASE_URL}/weight/entries`);
    if (!response.ok) {
      throw new Error('Failed to fetch weight entries');
    }
    return response.json();
  },

  /**
   * Create a new weight entry
   */
  async createEntry(data: WeightEntryCreate): Promise<WeightEntry> {
    const response = await fetch(`${API_BASE_URL}/weight/entries`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create weight entry');
    }

    return response.json();
  },

  /**
   * Update a weight entry
   */
  async updateEntry(id: number, data: WeightEntryUpdate): Promise<WeightEntry> {
    const response = await fetch(`${API_BASE_URL}/weight/entries/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update weight entry');
    }

    return response.json();
  },

  /**
   * Delete a weight entry
   */
  async deleteEntry(id: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/weight/entries/${id}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete weight entry');
    }
  },
};

import { useState, useEffect } from 'react';
import { catfoodApi } from '../api/catfood';
import type { CatFood, MealPlanItem } from '../types/catfood';
import './CatFoodMealPlanner.css';

export function CatFoodMealPlanner() {
  // Food search state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<CatFood[]>([]);
  const [selectedFood, setSelectedFood] = useState<CatFood | null>(null);
  const [showDropdown, setShowDropdown] = useState(false);
  const [isSearching, setIsSearching] = useState(false);

  // Selected food input state
  const [amount, setAmount] = useState('');
  const [unit, setUnit] = useState('grams');
  const [allowedUnits, setAllowedUnits] = useState<string[]>(['grams']);

  // Meal plan state
  const [mealItems, setMealItems] = useState<MealPlanItem[]>([]);
  const [isCalculating, setIsCalculating] = useState(false);
  const [error, setError] = useState('');

  // Search for foods when query changes
  useEffect(() => {
    const searchFoods = async () => {
      if (searchQuery.trim().length < 2) {
        setSearchResults([]);
        return;
      }

      setIsSearching(true);
      try {
        const results = await catfoodApi.searchFoods({
          query: searchQuery,
          limit: 10,
        });
        // Filter only foods with calorie data
        const foodsWithCalories = results.filter(f => f.kcal_per_kg !== null);
        setSearchResults(foodsWithCalories);
        setShowDropdown(true);
      } catch (err) {
        console.error('Search failed:', err);
        setSearchResults([]);
      } finally {
        setIsSearching(false);
      }
    };

    const timeoutId = setTimeout(searchFoods, 300);
    return () => clearTimeout(timeoutId);
  }, [searchQuery]);

  // Update allowed units when food type changes
  useEffect(() => {
    const updateUnits = async () => {
      if (!selectedFood || !selectedFood.type) {
        setAllowedUnits(['grams']);
        return;
      }

      try {
        const unitsData = await catfoodApi.getAllowedUnits(selectedFood.type as 'wet' | 'dry');
        setAllowedUnits(unitsData.allowed_units);
        // Set default unit
        if (!unitsData.allowed_units.includes(unit)) {
          setUnit(unitsData.allowed_units[0]);
        }
      } catch (err) {
        console.error('Failed to get allowed units:', err);
      }
    };

    updateUnits();
  }, [selectedFood]);

  const handleSelectFood = (food: CatFood) => {
    setSelectedFood(food);
    setSearchQuery(food.name);
    setShowDropdown(false);
    setAmount('');
  };

  const handleAddToMeal = async () => {
    if (!selectedFood || !amount || parseFloat(amount) <= 0) {
      setError('Please select a food and enter a valid amount');
      return;
    }

    setIsCalculating(true);
    setError('');

    try {
      const nutrition = await catfoodApi.calculateServing({
        product_id: selectedFood.id,
        amount: parseFloat(amount),
        unit: unit,
      });

      const newItem: MealPlanItem = {
        id: `${Date.now()}-${selectedFood.id}`,
        food: selectedFood,
        amount: parseFloat(amount),
        unit: unit,
        nutrition: nutrition,
      };

      setMealItems([...mealItems, newItem]);

      // Reset form
      setSearchQuery('');
      setSelectedFood(null);
      setAmount('');
      setUnit('grams');
      setError('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to calculate nutrition');
    } finally {
      setIsCalculating(false);
    }
  };

  const handleRemoveItem = (id: string) => {
    setMealItems(mealItems.filter(item => item.id !== id));
  };

  const calculateTotals = () => {
    return mealItems.reduce(
      (totals, item) => {
        if (item.nutrition) {
          totals.calories += item.nutrition.calories || 0;
          totals.protein_g += item.nutrition.protein_g || 0;
          totals.fat_g += item.nutrition.fat_g || 0;
          totals.fiber_g += item.nutrition.fiber_g || 0;
          totals.moisture_g += item.nutrition.moisture_g || 0;
          totals.grams += item.nutrition.grams || 0;
        }
        return totals;
      },
      { calories: 0, protein_g: 0, fat_g: 0, fiber_g: 0, moisture_g: 0, grams: 0 }
    );
  };

  const totals = calculateTotals();
  const hasWetFood = mealItems.some(item => item.food.type === 'wet');
  const hasDryFood = mealItems.some(item => item.food.type === 'dry');

  return (
    <div className="meal-planner">
      <div className="planner-header">
        <h2>🍽️ Cat Food Meal Planner</h2>
        <p>Add wet and dry foods to create a complete meal plan</p>
      </div>

      {/* Food Search & Add Section */}
      <div className="add-food-section">
        <h3>Add Food to Meal Plan</h3>

        <div className="form-row">
          <div className="form-group food-search-group">
            <label>Search Food</label>
            <div className="search-wrapper">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onFocus={() => searchResults.length > 0 && setShowDropdown(true)}
                placeholder="Search by brand or product name..."
                className="search-input"
              />
              {isSearching && <span className="search-loading">Searching...</span>}

              {showDropdown && searchResults.length > 0 && (
                <div className="search-dropdown">
                  {searchResults.map((food) => (
                    <div
                      key={food.id}
                      className="search-result-item"
                      onClick={() => handleSelectFood(food)}
                    >
                      <div className="result-name">
                        {food.name}
                        {food.type === 'wet' && food.serving_unit && !food.name.includes(food.serving_unit) && (
                          <span className="can-size-info"> ({food.serving_unit})</span>
                        )}
                      </div>
                      <div className="result-details">
                        <span className={`food-type-badge ${food.type}`}>
                          {food.type?.toUpperCase()}
                        </span>
                        <span className="result-calories">
                          {food.kcal_per_kg} kcal/kg
                        </span>
                        {food.brand && (
                          <span className="result-brand">{food.brand}</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
            {searchQuery.length > 0 && searchResults.length === 0 && !isSearching && (
              <small className="no-results">No foods found with calorie data</small>
            )}
          </div>
        </div>

        {selectedFood && (
          <div className="selected-food-info">
            <div className="selected-food-header">
              <span className={`food-type-badge ${selectedFood.type}`}>
                {selectedFood.type?.toUpperCase()}
              </span>
              <span className="selected-food-name">{selectedFood.name}</span>
            </div>
            <div className="selected-food-details">
              <span>Protein: {selectedFood.protein_pct}%</span>
              <span>Fat: {selectedFood.fat_pct}%</span>
              <span>Calories: {selectedFood.kcal_per_kg} kcal/kg</span>
              {selectedFood.type === 'wet' && selectedFood.serving_unit && (
                <span>Can Size: {selectedFood.serving_unit}</span>
              )}
            </div>
          </div>
        )}

        {selectedFood && (
          <div className="form-row">
            <div className="form-group">
              <label>Amount</label>
              <input
                type="number"
                step="0.1"
                min="0.1"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="e.g., 40"
                className="amount-input"
              />
            </div>

            <div className="form-group">
              <label>Unit</label>
              <select
                value={unit}
                onChange={(e) => setUnit(e.target.value)}
                className="unit-select"
              >
                {allowedUnits.map((u) => (
                  <option key={u} value={u}>
                    {u}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>&nbsp;</label>
              <button
                onClick={handleAddToMeal}
                disabled={isCalculating || !selectedFood || !amount}
                className="add-btn"
              >
                {isCalculating ? 'Adding...' : 'Add to Meal'}
              </button>
            </div>
          </div>
        )}

        {error && <div className="error-message">{error}</div>}
      </div>

      {/* Meal Plan Items */}
      {mealItems.length > 0 && (
        <div className="meal-plan-section">
          <h3>Current Meal Plan</h3>

          <div className="meal-items">
            {mealItems.map((item) => (
              <div key={item.id} className="meal-item">
                <div className="meal-item-header">
                  <div className="meal-item-title">
                    <span className={`food-type-badge ${item.food.type}`}>
                      {item.food.type?.toUpperCase()}
                    </span>
                    <span className="meal-item-name">
                      {item.food.name}
                      {item.food.type === 'wet' && item.food.serving_unit && !item.food.name.includes(item.food.serving_unit) && (
                        <span className="can-size-info"> ({item.food.serving_unit})</span>
                      )}
                    </span>
                  </div>
                  <button
                    onClick={() => handleRemoveItem(item.id)}
                    className="remove-btn"
                    title="Remove from meal"
                  >
                    ✕
                  </button>
                </div>

                <div className="meal-item-details">
                  <div className="meal-amount">
                    <strong>
                      {item.amount} {item.unit}
                    </strong>
                    {item.nutrition && (
                      <span className="grams-equivalent">
                        ({item.nutrition.grams.toFixed(1)}g)
                      </span>
                    )}
                  </div>

                  {item.nutrition && (
                    <div className="meal-nutrition">
                      <div className="nutrition-item highlight">
                        <span className="nutrition-label">Calories</span>
                        <span className="nutrition-value">
                          {item.nutrition.calories?.toFixed(1)} kcal
                        </span>
                      </div>
                      {item.nutrition.protein_g && (
                        <div className="nutrition-item">
                          <span className="nutrition-label">Protein</span>
                          <span className="nutrition-value">
                            {item.nutrition.protein_g.toFixed(1)}g
                          </span>
                        </div>
                      )}
                      {item.nutrition.fat_g && (
                        <div className="nutrition-item">
                          <span className="nutrition-label">Fat</span>
                          <span className="nutrition-value">
                            {item.nutrition.fat_g.toFixed(1)}g
                          </span>
                        </div>
                      )}
                      {item.nutrition.moisture_g && (
                        <div className="nutrition-item">
                          <span className="nutrition-label">Moisture</span>
                          <span className="nutrition-value">
                            {item.nutrition.moisture_g.toFixed(1)}g
                          </span>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Totals Section */}
          <div className="meal-totals">
            <h3>Meal Plan Summary</h3>
            <div className="totals-grid">
              <div className="total-item total-calories">
                <span className="total-label">Total Calories</span>
                <span className="total-value">{totals.calories.toFixed(1)} kcal</span>
              </div>
              <div className="total-item">
                <span className="total-label">Total Weight</span>
                <span className="total-value">{totals.grams.toFixed(1)}g</span>
              </div>
              <div className="total-item">
                <span className="total-label">Protein</span>
                <span className="total-value">{totals.protein_g.toFixed(1)}g</span>
              </div>
              <div className="total-item">
                <span className="total-label">Fat</span>
                <span className="total-value">{totals.fat_g.toFixed(1)}g</span>
              </div>
              {totals.moisture_g > 0 && (
                <div className="total-item">
                  <span className="total-label">Moisture</span>
                  <span className="total-value">{totals.moisture_g.toFixed(1)}g</span>
                </div>
              )}
              {totals.fiber_g > 0 && (
                <div className="total-item">
                  <span className="total-label">Fiber</span>
                  <span className="total-value">{totals.fiber_g.toFixed(1)}g</span>
                </div>
              )}
            </div>

            <div className="meal-composition">
              <div className="composition-bar">
                {hasDryFood && (
                  <div
                    className="composition-segment dry"
                    style={{
                      width: `${(mealItems.filter(i => i.food.type === 'dry').reduce((sum, i) => sum + (i.nutrition?.calories || 0), 0) / totals.calories * 100)}%`
                    }}
                    title={`Dry food: ${(mealItems.filter(i => i.food.type === 'dry').reduce((sum, i) => sum + (i.nutrition?.calories || 0), 0)).toFixed(0)} kcal`}
                  >
                    Dry
                  </div>
                )}
                {hasWetFood && (
                  <div
                    className="composition-segment wet"
                    style={{
                      width: `${(mealItems.filter(i => i.food.type === 'wet').reduce((sum, i) => sum + (i.nutrition?.calories || 0), 0) / totals.calories * 100)}%`
                    }}
                    title={`Wet food: ${(mealItems.filter(i => i.food.type === 'wet').reduce((sum, i) => sum + (i.nutrition?.calories || 0), 0)).toFixed(0)} kcal`}
                  >
                    Wet
                  </div>
                )}
              </div>
              <div className="composition-labels">
                {hasDryFood && (
                  <span className="composition-label">
                    🟤 Dry: {(mealItems.filter(i => i.food.type === 'dry').reduce((sum, i) => sum + (i.nutrition?.calories || 0), 0) / totals.calories * 100).toFixed(0)}%
                  </span>
                )}
                {hasWetFood && (
                  <span className="composition-label">
                    🔵 Wet: {(mealItems.filter(i => i.food.type === 'wet').reduce((sum, i) => sum + (i.nutrition?.calories || 0), 0) / totals.calories * 100).toFixed(0)}%
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {mealItems.length === 0 && (
        <div className="empty-state">
          <p>No foods added yet. Search and add foods to create a meal plan.</p>
        </div>
      )}
    </div>
  );
}

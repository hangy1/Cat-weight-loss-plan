import { useState, useEffect } from 'react'
import './App.css'
import { CatFoodMealPlanner } from './components/CatFoodMealPlanner'
import { WeightTracker } from './components/WeightTracker'

interface CalorieResult {
  current_weight_kg: number;
  ideal_weight_kg: number;
  bcs: number;
  rer: number;
  life_stage_factor: number;
  activity_factor: number;
  calories: {
    min: number;
    recommended: number;
  };
}

interface LifeStage {
  id: string;
  name: string;
  factors: {
    min: number;
    recommended: number;
    max: number;
  };
  description: string;
}

interface ActivityLevel {
  id: string;
  name: string;
  factor: number;
  description: string;
}

interface BCSScore {
  score: number;
  adjustment: number;
  description: string;
}

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [activeTab, setActiveTab] = useState<'calculator' | 'mealplanner' | 'weighttracker'>('calculator')
  const [weight, setWeight] = useState<string>('')
  const [unit, setUnit] = useState<'kg' | 'lb'>('lb')
  const [lifeStage, setLifeStage] = useState<string>('neutered_adult')
  const [activity, setActivity] = useState<string>('typical')
  const [bcs, setBcs] = useState<number>(5)
  const [result, setResult] = useState<CalorieResult | null>(null)
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string>('')
  const [lifeStages, setLifeStages] = useState<LifeStage[]>([])
  const [activityLevels, setActivityLevels] = useState<ActivityLevel[]>([])
  const [bcsScores, setBcsScores] = useState<BCSScore[]>([])

  // Fetch all options on component mount
  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const [lifeStagesRes, activityRes, bcsRes] = await Promise.all([
          fetch(`${API_BASE_URL}/life-stages`),
          fetch(`${API_BASE_URL}/activity-levels`),
          fetch(`${API_BASE_URL}/bcs-scores`)
        ]);

        if (lifeStagesRes.ok && activityRes.ok && bcsRes.ok) {
          const lifeStagesData = await lifeStagesRes.json();
          const activityData = await activityRes.json();
          const bcsData = await bcsRes.json();

          setLifeStages(lifeStagesData.life_stages);
          setActivityLevels(activityData.activity_levels);
          setBcsScores(bcsData.bcs_scores);
        }
      } catch (err) {
        console.error('Failed to fetch options:', err);
      }
    };

    fetchOptions();
  }, [])

  const handleUnitChange = async (newUnit: 'kg' | 'lb') => {
    if (!weight || unit === newUnit) {
      setUnit(newUnit);
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/convert-weight`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          weight: parseFloat(weight),
          from_unit: unit,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setWeight(newUnit === 'kg' ? data.weight_kg.toString() : data.weight_lb.toString());
        setUnit(newUnit);
      }
    } catch (err) {
      console.error('Failed to convert weight:', err);
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      // Convert to kg if the current unit is lb
      let weightInKg = parseFloat(weight);
      if (unit === 'lb') {
        const conversionResponse = await fetch(`${API_BASE_URL}/convert-weight`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            weight: weightInKg,
            from_unit: 'lb',
          }),
        });

        if (conversionResponse.ok) {
          const conversionData = await conversionResponse.json();
          weightInKg = conversionData.weight_kg;
        }
      }

      const response = await fetch(`${API_BASE_URL}/calculate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          weight_kg: weightInKg,
          life_stage: lifeStage,
          activity: activity,
          bcs: bcs,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to calculate calories')
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1>🐱 Cat Weight Loss Planner</h1>
          <p>Calculate calorie needs and plan meals for your cat</p>
        </header>

        <div className="tabs">
          <button
            className={`tab ${activeTab === 'calculator' ? 'active' : ''}`}
            onClick={() => setActiveTab('calculator')}
          >
            📊 Calorie Calculator
          </button>
          <button
            className={`tab ${activeTab === 'mealplanner' ? 'active' : ''}`}
            onClick={() => setActiveTab('mealplanner')}
          >
            🍽️ Meal Planner
          </button>
          <button
            className={`tab ${activeTab === 'weighttracker' ? 'active' : ''}`}
            onClick={() => setActiveTab('weighttracker')}
          >
            📈 Weight Tracker
          </button>
        </div>

        {activeTab === 'calculator' && (
        <>
        <form onSubmit={handleSubmit} className="form">
          <div className="form-group">
            <label htmlFor="weight">
              Cat's Current Weight
            </label>
            <div className="weight-input-group">
              <input
                id="weight"
                type="number"
                step="0.1"
                min="0.1"
                value={weight}
                onChange={(e) => setWeight(e.target.value)}
                placeholder={unit === 'kg' ? 'e.g., 4.5' : 'e.g., 10'}
                required
              />
              <select
                className="unit-select"
                value={unit}
                onChange={(e) => handleUnitChange(e.target.value as 'kg' | 'lb')}
              >
                <option value="lb">lb</option>
                <option value="kg">kg</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="lifeStage">
              Life Stage
            </label>
            <select
              id="lifeStage"
              value={lifeStage}
              onChange={(e) => setLifeStage(e.target.value)}
            >
              {lifeStages.length > 0 ? (
                lifeStages.map(stage => (
                  <option key={stage.id} value={stage.id}>
                    {stage.name}
                  </option>
                ))
              ) : (
                <>
                  <option value="neutered_adult">Neutered Adult</option>
                  <option value="intact_adult">Intact Adult</option>
                  <option value="inactive_obese_prone">Inactive/Obese Prone</option>
                  <option value="kitten_growth">Kitten Growth</option>
                </>
              )}
            </select>
            {lifeStages.find(s => s.id === lifeStage)?.description && (
              <small className="field-description">
                {lifeStages.find(s => s.id === lifeStage)?.description}
              </small>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="activity">
              Activity Level <span className="optional-label">(optional)</span>
            </label>
            <select
              id="activity"
              value={activity}
              onChange={(e) => setActivity(e.target.value)}
            >
              {activityLevels.length > 0 ? (
                activityLevels.map(level => (
                  <option key={level.id} value={level.id}>
                    {level.name}
                  </option>
                ))
              ) : (
                <>
                  <option value="sedentary">Sedentary</option>
                  <option value="typical">Typical</option>
                  <option value="active">Active</option>
                  <option value="outdoor">Outdoor</option>
                </>
              )}
            </select>
            {activityLevels.find(a => a.id === activity)?.description && (
              <small className="field-description">
                {activityLevels.find(a => a.id === activity)?.description}
              </small>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="bcs">
              Body Condition Score (BCS) <span className="optional-label">(1-9, optional)</span>
            </label>
            <select
              id="bcs"
              value={bcs}
              onChange={(e) => setBcs(Number(e.target.value))}
            >
              {bcsScores.length > 0 ? (
                bcsScores.map(score => (
                  <option key={score.score} value={score.score}>
                    {score.score} - {score.description}
                  </option>
                ))
              ) : (
                <>
                  <option value="1">1 - Severely underweight</option>
                  <option value="2">2 - Underweight</option>
                  <option value="3">3 - Lean</option>
                  <option value="4">4 - Slightly lean</option>
                  <option value="5">5 - Ideal</option>
                  <option value="6">6 - Slightly overweight</option>
                  <option value="7">7 - Overweight</option>
                  <option value="8">8 - Obese</option>
                  <option value="9">9 - Severely obese</option>
                </>
              )}
            </select>
            <small className="field-description">
              Determines ideal weight calculation. 5 = ideal body condition.
            </small>
          </div>

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? 'Calculating...' : 'Calculate'}
          </button>
        </form>

        {error && (
          <div className="error">
            {error}
          </div>
        )}

        {result && (
          <div className="results">
            <h2>Results</h2>

            <div className="result-card">
              <h3>Weight Information</h3>
              <div className="info-grid">
                <div className="info-item">
                  <span className="info-label">Current Weight</span>
                  <span className="info-value">{result.current_weight_kg.toFixed(2)} kg ({(result.current_weight_kg * 2.20462).toFixed(2)} lb)</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Ideal Weight</span>
                  <span className="info-value">{result.ideal_weight_kg.toFixed(2)} kg ({(result.ideal_weight_kg * 2.20462).toFixed(2)} lb)</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Body Condition Score</span>
                  <span className="info-value">{result.bcs} / 9</span>
                </div>
              </div>
            </div>

            <div className="result-card highlight">
              <h3>Daily Calorie Target</h3>
              <div className="calorie-range">
                <div className="calorie-item recommended">
                  <span className="calorie-label">Recommended</span>
                  <span className="calorie-value">{result.calories.recommended} kcal</span>
                </div>
                <div className="calorie-item">
                  <span className="calorie-label">Minimum (Safety Floor)</span>
                  <span className="calorie-value">{result.calories.min} kcal</span>
                </div>
              </div>
            </div>

            <div className="result-card">
              <h3>Calculation Details</h3>
              <div className="info-grid">
                <div className="info-item">
                  <span className="info-label">RER (Ideal Weight)</span>
                  <span className="info-value">{result.rer} kcal</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Life Stage Factor</span>
                  <span className="info-value">{result.life_stage_factor}×</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Activity Factor</span>
                  <span className="info-value">{result.activity_factor}×</span>
                </div>
              </div>
            </div>
          </div>
        )}
        </>
        )}

        {activeTab === 'mealplanner' && (
          <CatFoodMealPlanner />
        )}

        {activeTab === 'weighttracker' && (
          <WeightTracker />
        )}
      </div>
    </div>
  )
}

export default App

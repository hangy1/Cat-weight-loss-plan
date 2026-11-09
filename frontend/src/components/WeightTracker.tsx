import { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { weightApi } from '../api/weight';
import type {
  WeightEntry,
  WeightEntryCreate,
  ChartDataPoint,
} from '../types/weight';
import './WeightTracker.css';

export function WeightTracker() {
  // State for entries
  const [entries, setEntries] = useState<WeightEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Form state
  const [date, setDate] = useState('');
  const [weight, setWeight] = useState('');
  const [unit, setUnit] = useState<'kg' | 'lb'>('lb');
  const [notes, setNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Edit state
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editWeight, setEditWeight] = useState('');
  const [editUnit, setEditUnit] = useState<'kg' | 'lb'>('lb');
  const [editDate, setEditDate] = useState('');
  const [editNotes, setEditNotes] = useState('');

  // Fetch entries on mount
  useEffect(() => {
    fetchEntries();
  }, []);

  // Set current date/time on mount
  useEffect(() => {
    const now = new Date();
    const localDateTime = new Date(now.getTime() - now.getTimezoneOffset() * 60000)
      .toISOString()
      .slice(0, 16);
    setDate(localDateTime);
  }, []);

  const fetchEntries = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await weightApi.getAllEntries();
      setEntries(data.entries);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load entries');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      const entryData: WeightEntryCreate = {
        date: new Date(date).toISOString(),
        weight: parseFloat(weight),
        unit: unit,
        notes: notes.trim() || undefined,
      };

      await weightApi.createEntry(entryData);
      await fetchEntries();

      // Reset form
      setWeight('');
      setNotes('');
      const now = new Date();
      const localDateTime = new Date(now.getTime() - now.getTimezoneOffset() * 60000)
        .toISOString()
        .slice(0, 16);
      setDate(localDateTime);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add entry');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this entry?')) {
      return;
    }

    try {
      await weightApi.deleteEntry(id);
      await fetchEntries();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete entry');
    }
  };

  const startEdit = (entry: WeightEntry) => {
    setEditingId(entry.id);
    setEditWeight(unit === 'kg' ? entry.weight_kg.toString() : entry.weight_lb.toString());
    setEditUnit(unit);
    setEditDate(new Date(entry.date).toISOString().slice(0, 16));
    setEditNotes(entry.notes || '');
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditWeight('');
    setEditDate('');
    setEditNotes('');
  };

  const handleUpdate = async (id: number) => {
    setError('');
    try {
      await weightApi.updateEntry(id, {
        date: new Date(editDate).toISOString(),
        weight: parseFloat(editWeight),
        unit: editUnit,
        notes: editNotes.trim() || undefined,
      });
      await fetchEntries();
      cancelEdit();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update entry');
    }
  };

  // Transform data for chart
  const chartData: ChartDataPoint[] = entries.map((entry) => ({
    date: new Date(entry.date).toLocaleDateString(),
    weight: unit === 'kg' ? entry.weight_kg : entry.weight_lb,
    fullDate: new Date(entry.date),
  }));

  return (
    <div className="weight-tracker">
      <div className="tracker-header">
        <h2>Weight Tracker</h2>
        <p>Track your cat's weight over time</p>
      </div>

      {/* Add Entry Form */}
      <div className="add-entry-section">
        <h3>Add Weight Entry</h3>
        <form onSubmit={handleSubmit} className="weight-form">
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="date">Date & Time</label>
              <input
                id="date"
                type="datetime-local"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                max={new Date().toISOString().slice(0, 16)}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="weight">Weight</label>
              <div className="weight-input-group">
                <input
                  id="weight"
                  type="number"
                  step="0.01"
                  min="0.1"
                  value={weight}
                  onChange={(e) => setWeight(e.target.value)}
                  placeholder={unit === 'kg' ? 'e.g., 4.5' : 'e.g., 10'}
                  required
                />
                <select
                  value={unit}
                  onChange={(e) => setUnit(e.target.value as 'kg' | 'lb')}
                  className="unit-select"
                >
                  <option value="lb">lb</option>
                  <option value="kg">kg</option>
                </select>
              </div>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="notes">Notes (Optional)</label>
            <input
              id="notes"
              type="text"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="e.g., After morning meal"
              maxLength={500}
            />
          </div>

          <button type="submit" disabled={isSubmitting} className="submit-btn">
            {isSubmitting ? 'Adding...' : 'Add Entry'}
          </button>
        </form>

        {error && <div className="error-message">{error}</div>}
      </div>

      {/* Chart Section */}
      {entries.length > 0 && (
        <div className="chart-section">
          <h3>Weight History</h3>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis
                  label={{
                    value: `Weight (${unit})`,
                    angle: -90,
                    position: 'insideLeft',
                  }}
                />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="weight"
                  stroke="#8884d8"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Entries List */}
      {loading ? (
        <div className="loading">Loading entries...</div>
      ) : entries.length > 0 ? (
        <div className="entries-section">
          <h3>All Entries ({entries.length})</h3>
          <div className="entries-list">
            {entries.map((entry) => (
              <div key={entry.id} className="entry-item">
                {editingId === entry.id ? (
                  // Edit mode
                  <div className="edit-form">
                    <div className="form-row">
                      <input
                        type="datetime-local"
                        value={editDate}
                        onChange={(e) => setEditDate(e.target.value)}
                        max={new Date().toISOString().slice(0, 16)}
                      />
                      <div className="weight-input-group">
                        <input
                          type="number"
                          step="0.01"
                          min="0.1"
                          value={editWeight}
                          onChange={(e) => setEditWeight(e.target.value)}
                        />
                        <select
                          value={editUnit}
                          onChange={(e) => setEditUnit(e.target.value as 'kg' | 'lb')}
                        >
                          <option value="lb">lb</option>
                          <option value="kg">kg</option>
                        </select>
                      </div>
                    </div>
                    <input
                      type="text"
                      value={editNotes}
                      onChange={(e) => setEditNotes(e.target.value)}
                      placeholder="Notes (optional)"
                      maxLength={500}
                    />
                    <div className="edit-actions">
                      <button onClick={() => handleUpdate(entry.id)} className="save-btn">
                        Save
                      </button>
                      <button onClick={cancelEdit} className="cancel-btn">
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  // View mode
                  <>
                    <div className="entry-info">
                      <div className="entry-date">
                        {new Date(entry.date).toLocaleString()}
                      </div>
                      <div className="entry-weight">
                        <strong>
                          {unit === 'kg'
                            ? `${entry.weight_kg.toFixed(2)} kg`
                            : `${entry.weight_lb.toFixed(2)} lb`}
                        </strong>
                        <span className="secondary-unit">
                          ({unit === 'kg'
                            ? `${entry.weight_lb.toFixed(2)} lb`
                            : `${entry.weight_kg.toFixed(2)} kg`})
                        </span>
                      </div>
                      {entry.notes && <div className="entry-notes">{entry.notes}</div>}
                    </div>
                    <div className="entry-actions">
                      <button onClick={() => startEdit(entry)} className="edit-btn">
                        Edit
                      </button>
                      <button onClick={() => handleDelete(entry.id)} className="delete-btn">
                        Delete
                      </button>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="empty-state">
          <p>No weight entries yet. Add your first entry above!</p>
        </div>
      )}
    </div>
  );
}

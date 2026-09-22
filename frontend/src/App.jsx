import { useState } from 'react';
import WeekGrid, { parseISOComponents, formatDayLabel } from './WeekGrid';
import './App.css';

const API_URL = 'cadence-production-75f6.up.railway.app';

const CATEGORY_LABELS = {
  work: 'Work',
  learning: 'Learning',
  health: 'Health',
  personal: 'Personal',
  social: 'Social',
  default: 'Other',
};

function buildTasksById(tasks) {
  return (tasks || []).reduce((acc, task) => {
    acc[task.id] = task;
    return acc;
  }, {});
}

function computeSummary(result) {
  const tasks = result?.tasks?.tasks || [];
  const scheduled = result?.schedule?.scheduled || [];
  const tasksById = buildTasksById(tasks);

  const dayMinutes = {};
  const categoryCounts = {};
  let totalMinutes = 0;

  scheduled.forEach((item) => {
    const start = parseISOComponents(item.start);
    const end = parseISOComponents(item.end);
    if (!start || !end) return;

    const duration = (end.hour * 60 + end.minute) - (start.hour * 60 + start.minute);
    totalMinutes += duration;
    dayMinutes[start.dateKey] = (dayMinutes[start.dateKey] || 0) + duration;

    const category = tasksById[item.task_id]?.category || 'default';
    categoryCounts[category] = (categoryCounts[category] || 0) + 1;
  });

  let busiestDay = null;
  let busiestMinutes = 0;
  Object.entries(dayMinutes).forEach(([day, minutes]) => {
    if (minutes > busiestMinutes) {
      busiestMinutes = minutes;
      busiestDay = day;
    }
  });

  return {
    totalTasks: tasks.length,
    scheduledCount: scheduled.length,
    totalHours: Math.round((totalMinutes / 60) * 10) / 10,
    busiestDayLabel: busiestDay ? formatDayLabel(busiestDay) : null,
    categoryCounts,
  };
}

function App() {
  const [goals, setGoals] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (event) => setGoals(event.target.value);

  const handleSubmit = async () => {
    if (!goals.trim()) {
      setError('Add a few goals or responsibilities before generating a plan.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ raw_text: goals }),
      });

      if (!response.ok) {
        throw new Error(`Server responded with status ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error('Error fetching plan:', err);
      setError("Couldn't reach the planner. Check that the backend is running, then try again.");
    } finally {
      setLoading(false);
    }
  };

  const tasksById = buildTasksById(result?.tasks?.tasks);
  const unscheduledCount = result?.schedule?.unscheduled?.length || 0;
  const summary = result ? computeSummary(result) : null;

  return (
    <div className="app">
      <section className="hero">
        <span className="pill">synced with Google Calendar</span>
        <h1 className="display">Cadence</h1>
        <p className="subheadline">Describe what's on your plate. Cadence lays out the week.</p>
      </section>

      <section className="input-section">
        <textarea
          className="goal-input"
          value={goals}
          onChange={handleChange}
          placeholder="This week I need to..."
          rows={6}
        />
        <button className="cta" onClick={handleSubmit} disabled={loading}>
          {loading ? 'Planning…' : 'Generate my week'}
        </button>
        {error && <div className="error-banner">{error}</div>}

        <div className="tips-row">
          <span>Mention deadlines, workouts, chores — whatever needs a slot.</span>
          <span>Checks your real calendar for open time.</span>
          <span>Returns an hour-by-hour week, not a to-do list.</span>
        </div>
      </section>

      {result && (
        <section className="results">
          <div className="stats-strip">
            <div className="stat-card">
              <span className="stat-value">{summary.scheduledCount}<span className="stat-of">/{summary.totalTasks}</span></span>
              <span className="stat-label">Tasks placed</span>
            </div>
            <div className="stat-card">
              <span className="stat-value">{summary.totalHours}h</span>
              <span className="stat-label">Scheduled this week</span>
            </div>
            <div className="stat-card">
              <span className="stat-value">
                {summary.busiestDayLabel ? summary.busiestDayLabel.weekday : '—'}
              </span>
              <span className="stat-label">Busiest day</span>
            </div>
            <div className="stat-card categories-card">
              <div className="category-tags">
                {Object.entries(summary.categoryCounts).map(([cat, count]) => (
                  <span className="category-tag" key={cat}>
                    {CATEGORY_LABELS[cat] || cat} · {count}
                  </span>
                ))}
              </div>
              <span className="stat-label">By category</span>
            </div>
          </div>

          <div className="results-scroll">
            <WeekGrid
              freeBlocks={result.free_blocks}
              scheduledTasks={result.schedule?.scheduled}
              tasksById={tasksById}
            />
          </div>

          {unscheduledCount > 0 && (
            <div className="unscheduled-banner">
              {unscheduledCount} task{unscheduledCount > 1 ? 's' : ''} didn't fit in your free time this week.
            </div>
          )}
        </section>
      )}
    </div>
  );
}

export default App;
import { useMemo } from 'react';

const DAY_START_HOUR = 8;
const DAY_END_HOUR = 22;
const HOUR_HEIGHT = 52; // pixels per hour

// Free/busy blocks and scheduled tasks come back as ISO strings with an
// explicit offset (e.g. "2026-09-06T08:00:00-04:00"). We parse the wall-clock
// components directly rather than going through Date/getHours(), since the
// latter converts into the *browser's* local timezone — which may not match
// the offset the backend actually scheduled against.
export function parseISOComponents(iso) {
  const match = iso.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/);
  if (!match) return null;
  const [, year, month, day, hour, minute] = match;
  return {
    hour: Number(hour),
    minute: Number(minute),
    dateKey: `${year}-${month}-${day}`,
  };
}

export function formatDayLabel(dateKey) {
  const [year, month, day] = dateKey.split('-').map(Number);
  const date = new Date(year, month - 1, day);
  return {
    weekday: date.toLocaleDateString(undefined, { weekday: 'short' }),
    date: date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' }),
  };
}

function minutesFromDayStart({ hour, minute }) {
  return (hour - DAY_START_HOUR) * 60 + minute;
}

export default function WeekGrid({ freeBlocks, scheduledTasks, tasksById }) {
  const dayKeys = useMemo(() => {
    const set = new Set();
    (freeBlocks || []).forEach((block) => {
      const start = parseISOComponents(block.start);
      if (start) set.add(start.dateKey);
    });
    return Array.from(set).sort();
  }, [freeBlocks]);

  if (dayKeys.length === 0) {
    return (
      <div className="week-grid-empty">
        No week to show yet. Describe your goals above and generate a plan.
      </div>
    );
  }

  const hours = [];
  for (let h = DAY_START_HOUR; h < DAY_END_HOUR; h++) hours.push(h);
  const totalHeight = (DAY_END_HOUR - DAY_START_HOUR) * HOUR_HEIGHT;

  return (
    <div
      className="week-grid"
      style={{ gridTemplateColumns: `56px repeat(${dayKeys.length}, 1fr)` }}
    >
      <div className="week-grid-corner" />
      {dayKeys.map((dayKey) => {
        const { weekday, date } = formatDayLabel(dayKey);
        return (
          <div className="week-grid-day-header" key={dayKey}>
            <span className="weekday">{weekday}</span>
            <span className="date">{date}</span>
          </div>
        );
      })}

      <div className="week-grid-hours" style={{ height: totalHeight }}>
        {hours.map((hour) => (
          <div className="week-grid-hour-label" key={hour} style={{ height: HOUR_HEIGHT }}>
            {hour % 12 === 0 ? 12 : hour % 12}{hour < 12 ? 'am' : 'pm'}
          </div>
        ))}
      </div>

      {dayKeys.map((dayKey) => (
        <div className="week-grid-column" key={dayKey} style={{ height: totalHeight }}>
          {hours.map((hour) => (
            <div className="staff-line" key={hour} style={{ top: (hour - DAY_START_HOUR) * HOUR_HEIGHT }} />
          ))}

          {(scheduledTasks || [])
            .filter((item) => {
              const start = parseISOComponents(item.start);
              return start && start.dateKey === dayKey;
            })
            .map((item) => {
              const start = parseISOComponents(item.start);
              const end = parseISOComponents(item.end);
              const top = minutesFromDayStart(start);
              const duration = minutesFromDayStart(end) - top;
              const task = tasksById[item.task_id];
              const isUrgent = (task?.priority || 0) >= 5;

              return (
                <div
                  className="week-grid-block"
                  key={item.task_id}
                  style={{
                    top: `${(top / 60) * HOUR_HEIGHT}px`,
                    height: `${Math.max((duration / 60) * HOUR_HEIGHT, 24)}px`,
                  }}
                  title={task?.title || 'Untitled task'}
                >
                  {isUrgent && <span className="priority-dot" aria-hidden="true" />}
                  <span className="block-category">{task?.category || 'other'}</span>
                  <span className="block-title">{task?.title || 'Untitled task'}</span>
                </div>
              );
            })}
        </div>
      ))}
    </div>
  );
}
interface MetricGaugeProps {
  label: string;
  value: number;
  detail?: string;
}

function getColor(value: number): string {
  if (value < 60) return "text-emerald-400";
  if (value < 80) return "text-yellow-400";
  return "text-red-400";
}

function getTrackColor(value: number): string {
  if (value < 60) return "stroke-emerald-400";
  if (value < 80) return "stroke-yellow-400";
  return "stroke-red-400";
}

export function MetricGauge({ label, value, detail }: MetricGaugeProps) {
  const radius = 40;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (value / 100) * circumference;

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-24 h-24">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
          <circle
            cx="50"
            cy="50"
            r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth="8"
            className="text-slate-700"
          />
          <circle
            cx="50"
            cy="50"
            r={radius}
            fill="none"
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            className={`${getTrackColor(value)} transition-all duration-500`}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={`text-lg font-bold ${getColor(value)}`}>
            {Math.round(value)}%
          </span>
        </div>
      </div>
      <span className="text-sm text-slate-400 mt-1">{label}</span>
      {detail && (
        <span className="text-xs text-slate-500">{detail}</span>
      )}
    </div>
  );
}

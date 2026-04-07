interface StatusBadgeProps {
  isOnline: boolean;
}

export function StatusBadge({ isOnline }: StatusBadgeProps) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
        isOnline
          ? "bg-emerald-400/10 text-emerald-400"
          : "bg-red-400/10 text-red-400"
      }`}
    >
      <span
        className={`w-2 h-2 rounded-full ${
          isOnline ? "bg-emerald-400 animate-pulse" : "bg-red-400"
        }`}
      />
      {isOnline ? "Online" : "Offline"}
    </span>
  );
}

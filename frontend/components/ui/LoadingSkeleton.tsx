export default function LoadingSkeleton({ lines = 3 }: { lines?: number }) {
  return (
    <div className="animate-pulse space-y-3 p-4 bg-surface rounded-xl border border-border">
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="h-4 bg-surfaceHigh rounded"
          style={{ width: `${100 - i * 15}%` }}
        />
      ))}
    </div>
  );
}

interface ErrorBannerProps {
  message?: string;
  onRetry?: () => void;
}

export default function ErrorBanner({
  message = "Something went wrong.",
  onRetry,
}: ErrorBannerProps) {
  return (
    <div className="flex items-center justify-between gap-4 p-4 bg-danger/10 border border-danger/30 rounded-xl text-sm text-danger">
      <span>⚠️ {message}</span>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-3 py-1 rounded-lg border border-danger/40 hover:bg-danger/20 transition-colors text-xs font-medium"
        >
          Retry
        </button>
      )}
    </div>
  );
}

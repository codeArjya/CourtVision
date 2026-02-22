"use client";

import TakeCard from "./TakeCard";
import LoadingSpinner from "../ui/LoadingSpinner";
import ErrorBanner from "../ui/ErrorBanner";

interface TakesFeedProps {
  takes: any[];
  isLoading: boolean;
  isError: boolean;
  refetch: () => void;
}

export default function TakesFeed({
  takes,
  isLoading,
  isError,
  refetch,
}: TakesFeedProps) {
  if (isLoading) return <LoadingSpinner />;
  if (isError)
    return <ErrorBanner message="Failed to load takes." onRetry={refetch} />;
  if (!takes || takes.length === 0) {
    return (
      <p className="text-secondary text-center py-12">
        No takes yet. Check back soon.
      </p>
    );
  }

  return (
    // 2-column masonry grid — cards self-align to their natural height
    <div className="columns-1 md:columns-2 gap-4 space-y-0">
      {takes.map((take) => (
        <div key={take.id} className="break-inside-avoid mb-4">
          <TakeCard take={take} />
        </div>
      ))}
    </div>
  );
}

"use client";

import { useQuery } from "@tanstack/react-query";
import { MOCK_TAKES } from "@/lib/mockData";
import TakesFeed from "@/components/takes/TakesFeed";

export default function TakesPage() {
  const {
    data: takes,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ["takes"],
    queryFn: async () => MOCK_TAKES,
  });

  return (
    // max-w-6xl matches Games and Predictions pages (was max-w-3xl — too narrow)
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-primary">Media Takes</h1>
        <p className="text-secondary text-sm mt-1">
          Hot NBA opinions — vote and get an AI verdict
        </p>
      </div>

      <TakesFeed
        takes={takes || MOCK_TAKES}
        isLoading={isLoading}
        isError={isError}
        refetch={refetch}
      />
    </div>
  );
}

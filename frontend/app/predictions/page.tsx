"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import {
  MOCK_GAMES,
  MOCK_PREDICTIONS,
  FALLBACK_PREDICTION,
} from "@/lib/mockData";
import PredictionCard from "@/components/predictions/PredictionCard";
import LoadingSkeleton from "@/components/ui/LoadingSkeleton";
import ErrorBanner from "@/components/ui/ErrorBanner";

export default function PredictionsPage() {
  const { data: games } = useQuery({
    queryKey: ["games"],
    queryFn: async () => {
      try {
        const res = await api.get("/api/games");
        return res.data;
      } catch {
        return MOCK_GAMES;
      }
    },
  });

  const {
    data: predictions,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ["predictions", games],
    enabled: !!games,
    queryFn: async () => {
      const gamesData = games || MOCK_GAMES;
      try {
        return await Promise.all(
          gamesData.map(async (game: any) => {
            try {
              const res = await api.get(`/api/predictions/${game.game_id}`);
              return { game, prediction: res.data };
            } catch {
              const mock = MOCK_PREDICTIONS.find(
                (p) => p.game_id === game.game_id,
              );
              return { game, prediction: mock || FALLBACK_PREDICTION };
            }
          }),
        );
      } catch {
        return (games || MOCK_GAMES).map((game: any) => {
          const mock = MOCK_PREDICTIONS.find((p) => p.game_id === game.game_id);
          return { game, prediction: mock || FALLBACK_PREDICTION };
        });
      }
    },
  });

  const displayGames = games || MOCK_GAMES;

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Heading */}
      <div className="mb-2">
        <h1 className="text-2xl font-bold text-primary">AI Predictions</h1>
        <p className="text-secondary text-sm mt-1">
          Powered by Gemini 1.5 Flash · Updated before each tip-off
        </p>
      </div>

      {/* Disclaimer */}
      <div className="mb-6">
        <span className="inline-block bg-orange-dim text-orange text-xs px-3 py-1 rounded-full font-medium">
          🤖 AI-generated analysis · Not financial advice
        </span>
      </div>

      {isError && (
        <ErrorBanner message="Failed to load predictions." onRetry={refetch} />
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {isLoading || !predictions
          ? displayGames.map((_: any, i: number) => (
              <LoadingSkeleton key={i} lines={5} />
            ))
          : predictions.map(({ game, prediction }: any) => (
              <PredictionCard
                key={game.game_id}
                game={game}
                prediction={prediction}
              />
            ))}
      </div>
    </div>
  );
}

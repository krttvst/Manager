import { useQuery } from "@tanstack/react-query";
import { getDashboardOverview } from "../api/dashboard.js";

const DASHBOARD_KEY = ["dashboard", { scope: "overview" }];

export function useDashboardOverviewQuery(token) {
  const query = useQuery({
    queryKey: DASHBOARD_KEY,
    queryFn: () => getDashboardOverview(token),
    enabled: Boolean(token),
    refetchInterval: 30_000
  });

  return {
    ...query,
    overview: query.data ?? null
  };
}


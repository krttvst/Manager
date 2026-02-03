import { useQuery, useQueryClient } from "@tanstack/react-query";
import { listChannels } from "../api/channels.js";

const CHANNELS_KEY = ["channels", { scope: "all" }];

export function useChannelsQuery(token) {
  const queryClient = useQueryClient();

  const channelsQuery = useQuery({
    queryKey: CHANNELS_KEY,
    queryFn: () => listChannels(token),
    enabled: Boolean(token)
  });

  function addChannel(channel) {
    queryClient.setQueryData(CHANNELS_KEY, (prev = []) => [channel, ...prev]);
  }

  return {
    ...channelsQuery,
    channels: channelsQuery.data ?? [],
    addChannel
  };
}


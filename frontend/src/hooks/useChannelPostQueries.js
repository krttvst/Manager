import { useMemo } from "react";
import { useInfiniteQuery, useQueryClient } from "@tanstack/react-query";
import { listPosts } from "../api/posts.js";

export function useChannelPostQueries({ channelId, token, activeTab, statusFilter, pageSize }) {
  const queryClient = useQueryClient();

  const postsQuery = useInfiniteQuery({
    queryKey: ["posts", { channelId, statusFilter: statusFilter || null, limit: pageSize }],
    queryFn: ({ pageParam = 0 }) =>
      listPosts(token, channelId, { statusFilter, limit: pageSize, offset: pageParam }),
    getNextPageParam: (lastPage, allPages) =>
      lastPage.length === pageSize ? allPages.length * pageSize : undefined,
    enabled: activeTab === "queue" && Boolean(token && channelId)
  });

  const publishedQuery = useInfiniteQuery({
    queryKey: ["posts", { channelId, statusFilters: ["published"], limit: pageSize }],
    queryFn: ({ pageParam = 0 }) =>
      listPosts(token, channelId, { statusFilters: ["published"], limit: pageSize, offset: pageParam }),
    getNextPageParam: (lastPage, allPages) =>
      lastPage.length === pageSize ? allPages.length * pageSize : undefined,
    enabled: activeTab === "queue" && Boolean(token && channelId)
  });

  const queueQuery = useInfiniteQuery({
    queryKey: ["posts", { channelId, statusFilters: ["pending", "approved", "scheduled"], limit: pageSize }],
    queryFn: ({ pageParam = 0 }) =>
      listPosts(token, channelId, {
        statusFilters: ["pending", "approved", "scheduled"],
        limit: pageSize,
        offset: pageParam
      }),
    getNextPageParam: (lastPage, allPages) =>
      lastPage.length === pageSize ? allPages.length * pageSize : undefined,
    enabled: activeTab === "queue" && Boolean(token && channelId)
  });

  const posts = useMemo(() => postsQuery.data?.pages.flat() ?? [], [postsQuery.data]);
  const publishedPosts = useMemo(() => publishedQuery.data?.pages.flat() ?? [], [publishedQuery.data]);
  const queuePosts = useMemo(() => queueQuery.data?.pages.flat() ?? [], [queueQuery.data]);

  async function invalidatePosts() {
    await queryClient.invalidateQueries({
      predicate: (query) => query.queryKey[0] === "posts" && query.queryKey[1]?.channelId === channelId
    });
  }

  return {
    postsQuery,
    publishedQuery,
    queueQuery,
    posts,
    publishedPosts,
    queuePosts,
    hasPublishedMore: Boolean(publishedQuery.hasNextPage),
    hasQueueMore: Boolean(queueQuery.hasNextPage),
    invalidatePosts
  };
}


import { useMutation } from "@tanstack/react-query";
import {
  submitApproval as submitApprovalApi,
  approvePost as approvePostApi,
  rejectPost as rejectPostApi,
  schedulePost as schedulePostApi,
  publishNow as publishNowApi,
  deletePost as deletePostApi
} from "../api/posts.js";
import { deleteChannel as deleteChannelApi } from "../api/channels.js";

export function useChannelActions({ token, channelId, navigate, invalidatePosts, onError }) {
  const submitApprovalMutation = useMutation({
    mutationFn: (postId) => submitApprovalApi(token, postId),
    onSuccess: invalidatePosts,
    onError
  });

  const approveMutation = useMutation({
    mutationFn: (postId) => approvePostApi(token, postId),
    onSuccess: invalidatePosts,
    onError
  });

  const rejectMutation = useMutation({
    mutationFn: ({ postId, comment }) => rejectPostApi(token, postId, { comment }),
    onSuccess: invalidatePosts,
    onError
  });

  const scheduleMutation = useMutation({
    mutationFn: ({ postId, iso }) => schedulePostApi(token, postId, { scheduled_at: iso }),
    onSuccess: invalidatePosts,
    onError
  });

  const publishNowMutation = useMutation({
    mutationFn: (postId) => publishNowApi(token, postId),
    onSuccess: invalidatePosts,
    onError
  });

  const deleteMutation = useMutation({
    mutationFn: (postId) => deletePostApi(token, postId),
    onSuccess: invalidatePosts,
    onError
  });

  const deleteChannelMutation = useMutation({
    mutationFn: () => deleteChannelApi(token, channelId),
    onSuccess: () => navigate("/"),
    onError
  });

  return {
    submitApprovalMutation,
    approveMutation,
    rejectMutation,
    scheduleMutation,
    publishNowMutation,
    deleteMutation,
    deleteChannelMutation,
    async submitApproval(postId) {
      try {
        await submitApprovalMutation.mutateAsync(postId);
      } catch {}
    },
    async approve(postId) {
      try {
        await approveMutation.mutateAsync(postId);
      } catch {}
    },
    async reject(postId, comment) {
      try {
        await rejectMutation.mutateAsync({ postId, comment });
      } catch {}
    },
    async schedule(postId, iso) {
      try {
        await scheduleMutation.mutateAsync({ postId, iso });
      } catch {}
    },
    async publishNow(postId) {
      try {
        await publishNowMutation.mutateAsync(postId);
      } catch {}
    },
    async removePost(postId) {
      try {
        await deleteMutation.mutateAsync(postId);
      } catch {}
    },
    async removeChannel() {
      try {
        await deleteChannelMutation.mutateAsync();
      } catch {}
    }
  };
}


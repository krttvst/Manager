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
  async function mutateSafe(mutation, payload) {
    try {
      // tanstack v5: mutateAsync returns a promise and throws on error.
      return await mutation.mutateAsync(payload);
    } catch {
      return null;
    }
  }

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
    submitApproval: (postId) => mutateSafe(submitApprovalMutation, postId),
    approve: (postId) => mutateSafe(approveMutation, postId),
    reject: (postId, comment) => mutateSafe(rejectMutation, { postId, comment }),
    schedule: (postId, iso) => mutateSafe(scheduleMutation, { postId, iso }),
    publishNow: (postId) => mutateSafe(publishNowMutation, postId),
    removePost: (postId) => mutateSafe(deleteMutation, postId),
    removeChannel: () => mutateSafe(deleteChannelMutation)
  };
}

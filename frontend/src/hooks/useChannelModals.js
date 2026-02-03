import { useState } from "react";

export function useChannelModals() {
  const [confirmDeletePostId, setConfirmDeletePostId] = useState(null);
  const [confirmDeleteChannel, setConfirmDeleteChannel] = useState(false);
  const [rejectPostId, setRejectPostId] = useState(null);
  const [schedulePostId, setSchedulePostId] = useState(null);
  const [confirmApprovePostId, setConfirmApprovePostId] = useState(null);
  const [confirmPublishPostId, setConfirmPublishPostId] = useState(null);

  return {
    confirmDeletePostId,
    confirmDeleteChannel,
    rejectPostId,
    schedulePostId,
    confirmApprovePostId,
    confirmPublishPostId,
    openDeletePost: (postId) => setConfirmDeletePostId(postId),
    openDeleteChannel: () => setConfirmDeleteChannel(true),
    openReject: (postId) => setRejectPostId(postId),
    openSchedule: (postId) => setSchedulePostId(postId),
    openApprove: (postId) => setConfirmApprovePostId(postId),
    openPublish: (postId) => setConfirmPublishPostId(postId),
    closeDeletePost: () => setConfirmDeletePostId(null),
    closeDeleteChannel: () => setConfirmDeleteChannel(false),
    closeReject: () => setRejectPostId(null),
    closeSchedule: () => setSchedulePostId(null),
    closeApprove: () => setConfirmApprovePostId(null),
    closePublish: () => setConfirmPublishPostId(null)
  };
}


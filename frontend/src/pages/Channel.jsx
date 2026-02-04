import { useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "../state/auth.jsx";
import { getChannel } from "../api/channels.js";
import { getChannelStats } from "../api/stats.js";
import { listSuggestions, acceptSuggestion, rejectSuggestion } from "../api/suggestions.js";
import CreatePostModal from "./CreatePostModal.jsx";
import PostPreviewModal from "./PostPreviewModal.jsx";
import EditPostModal from "./EditPostModal.jsx";
import ChannelHeader from "../components/channel/ChannelHeader.jsx";
import ChannelContent from "../components/channel/ChannelContent.jsx";
import ConfirmModal from "../components/modals/ConfirmModal.jsx";
import RejectPostModal from "../components/modals/RejectPostModal.jsx";
import SchedulePostModal from "../components/modals/SchedulePostModal.jsx";
import { useChannelPostQueries } from "../hooks/useChannelPostQueries.js";
import { useChannelModals } from "../hooks/useChannelModals.js";
import { useChannelActions } from "../hooks/useChannelActions.js";
import { useChannelPostPreview } from "../hooks/useChannelPostPreview.js";

const STATUSES = ["draft", "pending", "approved", "scheduled", "published", "rejected", "failed"];
const STATUS_LABELS = {
  draft: "Черновик",
  pending: "На согласовании",
  approved: "Одобрен",
  scheduled: "Запланирован",
  published: "Опубликован",
  rejected: "Отклонён",
  failed: "Ошибка"
};

const PAGE_SIZE = 50;

export default function Channel() {
  const { id } = useParams();
  const { token } = useAuth();
  const { user } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState("queue");
  const [statusFilter, setStatusFilter] = useState("");
  const [error, setError] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const {
    activePost,
    showPreview,
    showEdit,
    setShowPreview,
    setShowEdit,
    openPreview,
    openEditFromActive
  } = useChannelPostPreview({
    token,
    onError: (err) => setError(err.message)
  });
  const {
    confirmDeletePostId,
    confirmDeleteChannel,
    rejectPostId,
    schedulePostId,
    confirmApprovePostId,
    confirmPublishPostId,
    openDeletePost,
    openDeleteChannel,
    openReject,
    openSchedule,
    openApprove,
    openPublish,
    closeDeletePost,
    closeDeleteChannel,
    closeReject,
    closeSchedule,
    closeApprove,
    closePublish
  } = useChannelModals();

  const role = user?.role || null;
  const canCreatePost = role === "admin" || role === "editor" || role === "author";
  const canApprove = role === "admin" || role === "editor";
  const canDeleteChannel = role === "admin";
  const canDeletePost = role === "admin";

  const channelQuery = useQuery({
    queryKey: ["channel", { channelId: id }],
    queryFn: () => getChannel(token, id),
    enabled: Boolean(token && id)
  });

  const {
    postsQuery,
    publishedQuery,
    queueQuery,
    posts,
    publishedPosts,
    queuePosts,
    hasPublishedMore,
    hasQueueMore,
    invalidatePosts
  } = useChannelPostQueries({
    channelId: id,
    token,
    activeTab,
    statusFilter,
    pageSize: PAGE_SIZE
  });

  const statsQuery = useQuery({
    queryKey: ["channel-stats", { channelId: id }],
    queryFn: () => getChannelStats(token, id),
    enabled: activeTab === "stats" && Boolean(token && id)
  });

  const suggestionsQuery = useQuery({
    queryKey: ["suggestions", { channelId: id }],
    queryFn: () => listSuggestions(token, id, { limit: 50, offset: 0 }),
    enabled: activeTab === "queue" && Boolean(token && id)
  });

  const badges = useMemo(
    () =>
      STATUSES.map((st) => (
        <button
          key={st}
          className={`badge ${statusFilter === st ? "active" : ""} status-${st}`}
          onClick={() => setStatusFilter(statusFilter === st ? "" : st)}
        >
          {STATUS_LABELS[st] || st}
        </button>
      )),
    [statusFilter]
  );

  const {
    submitApprovalMutation,
    approveMutation,
    rejectMutation,
    scheduleMutation,
    publishNowMutation,
    deleteMutation,
    deleteChannelMutation,
    submitApproval,
    approve,
    reject,
    schedule,
    publishNow,
    removePost,
    removeChannel
  } = useChannelActions({
    token,
    channelId: id,
    navigate,
    invalidatePosts,
    onError: (err) => setError(err.message)
  });

  const isSubmitting = submitApprovalMutation.isPending;
  const isApproving = approveMutation.isPending;
  const isRejecting = rejectMutation.isPending;
  const isScheduling = scheduleMutation.isPending;
  const isPublishing = publishNowMutation.isPending;
  const isDeleting = deleteMutation.isPending;

  async function openDeleteChannelModal() {
    openDeleteChannel();
  }

  const queryError =
    channelQuery.error?.message ||
    postsQuery.error?.message ||
    publishedQuery.error?.message ||
    queueQuery.error?.message ||
    statsQuery.error?.message ||
    suggestionsQuery.error?.message;
  const channel = channelQuery.data;
  const stats = statsQuery.data;
  const suggestions = suggestionsQuery.data || [];

  const acceptSuggestionMutation = useMutation({
    mutationFn: (suggestionId) => acceptSuggestion(token, id, suggestionId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["suggestions", { channelId: id }] });
      await invalidatePosts();
    },
    onError: (err) => setError(err.message)
  });

  const rejectSuggestionMutation = useMutation({
    mutationFn: (suggestionId) => rejectSuggestion(token, id, suggestionId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["suggestions", { channelId: id }] });
    },
    onError: (err) => setError(err.message)
  });

  async function handleAcceptSuggestion(suggestionId) {
    try {
      await acceptSuggestionMutation.mutateAsync(suggestionId);
    } catch {}
  }

  async function handleRejectSuggestion(suggestionId) {
    try {
      await rejectSuggestionMutation.mutateAsync(suggestionId);
    } catch {}
  }

  return (
    <section>
      <ChannelHeader
        channel={channel}
        canCreatePost={canCreatePost}
        canDeleteChannel={canDeleteChannel}
        onCreatePost={() => setShowCreate(true)}
        onDeleteChannel={openDeleteChannelModal}
      />

      <ChannelContent
        activeTab={activeTab}
        onChangeTab={setActiveTab}
        isLoading={
          channelQuery.isLoading ||
          postsQuery.isLoading ||
          publishedQuery.isLoading ||
          queueQuery.isLoading ||
          statsQuery.isLoading ||
          suggestionsQuery.isLoading
        }
        error={error || queryError}
        publishedPosts={publishedPosts}
        queuePosts={queuePosts}
        hasPublishedMore={hasPublishedMore}
        hasQueueMore={hasQueueMore}
        onLoadMorePublished={() => publishedQuery.fetchNextPage()}
        onLoadMoreQueue={() => queueQuery.fetchNextPage()}
        isPublishedFetching={publishedQuery.isFetching}
        isQueueFetching={queueQuery.isFetching}
        posts={posts}
        badges={badges}
        onOpenPost={openPreview}
        onSubmitApproval={submitApproval}
        onApprove={approve}
        onReject={reject}
        onSchedule={schedule}
        onPublishNow={publishNow}
        onDeletePost={removePost}
        canCreatePost={canCreatePost}
        canApprove={canApprove}
        canModerateSuggestions={canApprove}
        statusLabels={STATUS_LABELS}
        isSubmitting={isSubmitting}
        isApproving={isApproving}
        isRejecting={isRejecting}
        isScheduling={isScheduling}
        isPublishing={isPublishing}
        isDeleting={isDeleting}
        hasPostsMore={postsQuery.hasNextPage}
        onLoadMorePosts={() => postsQuery.fetchNextPage()}
        isPostsFetching={postsQuery.isFetching}
        stats={stats}
        suggestions={suggestions}
        isSuggestionsLoading={suggestionsQuery.isLoading}
        isSuggestionsMutating={acceptSuggestionMutation.isPending || rejectSuggestionMutation.isPending}
        onAcceptSuggestion={handleAcceptSuggestion}
        onRejectSuggestion={handleRejectSuggestion}
        onOpenAgentSettings={() => navigate(`/channels/${id}/agent-settings`)}
      />

      {showPreview && activePost && (
        <PostPreviewModal
          post={activePost}
          onClose={() => setShowPreview(false)}
          canEdit={canCreatePost}
          canDelete={canDeletePost}
          onEdit={() => {
            if (!canCreatePost) return;
            setShowPreview(false);
            openEditFromActive();
          }}
          onDelete={() => {
            if (!canDeletePost) return;
            setShowPreview(false);
            openDeletePost(activePost.id);
          }}
          isDeleting={isDeleting}
        />
      )}

      {showEdit && activePost && (
        <EditPostModal
          post={activePost}
          canApprove={canApprove}
          onClose={() => setShowEdit(false)}
          onUpdated={async () => {
            setShowEdit(false);
            await invalidatePosts();
          }}
        />
      )}

      {showCreate && (
        <CreatePostModal
          channelId={id}
          canApprove={canApprove}
          onClose={() => setShowCreate(false)}
          onCreated={async () => {
            await invalidatePosts();
          }}
        />
      )}


      <ConfirmModal
        isOpen={Boolean(confirmDeletePostId)}
        title="Удалить пост"
        message="Пост будет удалён без возможности восстановления."
        confirmLabel="Удалить"
        onCancel={closeDeletePost}
        onConfirm={async () => {
          if (!confirmDeletePostId) return;
          await removePost(confirmDeletePostId);
          closeDeletePost();
        }}
        isLoading={isDeleting}
      />

      <ConfirmModal
        isOpen={confirmDeleteChannel}
        title="Удалить канал"
        message="Канал и все его посты будут удалены."
        confirmLabel="Удалить"
        onCancel={closeDeleteChannel}
        onConfirm={async () => {
          await removeChannel();
          closeDeleteChannel();
        }}
        isLoading={deleteChannelMutation.isPending}
      />

      <ConfirmModal
        isOpen={Boolean(confirmApprovePostId)}
        title="Одобрить пост"
        message="Пост будет одобрен и готов к публикации."
        confirmLabel="Одобрить"
        onCancel={closeApprove}
        onConfirm={async () => {
          if (!confirmApprovePostId) return;
          await approve(confirmApprovePostId);
          closeApprove();
        }}
        isLoading={isApproving}
      />

      <ConfirmModal
        isOpen={Boolean(confirmPublishPostId)}
        title="Опубликовать сразу"
        message="Пост будет опубликован немедленно."
        confirmLabel="Опубликовать"
        onCancel={closePublish}
        onConfirm={async () => {
          if (!confirmPublishPostId) return;
          await publishNow(confirmPublishPostId);
          closePublish();
        }}
        isLoading={isPublishing}
      />

      <RejectPostModal
        isOpen={Boolean(rejectPostId)}
        onCancel={closeReject}
        onConfirm={async (comment) => {
          if (!rejectPostId) return;
          await reject(rejectPostId, comment);
          closeReject();
        }}
        isLoading={isRejecting}
      />

      <SchedulePostModal
        isOpen={Boolean(schedulePostId)}
        onCancel={closeSchedule}
        onConfirm={async (iso) => {
          if (!schedulePostId) return;
          await schedule(schedulePostId, iso);
          closeSchedule();
        }}
        isLoading={isScheduling}
      />
    </section>
  );
}

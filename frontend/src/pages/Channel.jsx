import { useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "../state/auth.jsx";
import { getChannel } from "../api/channels.js";
import { getPost } from "../api/posts.js";
import { getChannelStats } from "../api/stats.js";
import CreatePostModal from "./CreatePostModal.jsx";
import AiGenerateModal from "./AiGenerateModal.jsx";
import PostPreviewModal from "./PostPreviewModal.jsx";
import EditPostModal from "./EditPostModal.jsx";
import ChannelHeader from "../components/channel/ChannelHeader.jsx";
import PostsGridSection from "../components/channel/PostsGridSection.jsx";
import PostsList from "../components/channel/PostsList.jsx";
import ConfirmModal from "../components/modals/ConfirmModal.jsx";
import RejectPostModal from "../components/modals/RejectPostModal.jsx";
import SchedulePostModal from "../components/modals/SchedulePostModal.jsx";
import { useChannelPostQueries } from "../hooks/useChannelPostQueries.js";
import { useChannelModals } from "../hooks/useChannelModals.js";
import { useChannelActions } from "../hooks/useChannelActions.js";

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
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState("queue");
  const [statusFilter, setStatusFilter] = useState("");
  const [error, setError] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [showAi, setShowAi] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [showEdit, setShowEdit] = useState(false);
  const [activePost, setActivePost] = useState(null);
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

  const canCreatePost = true;
  const canApprove = true;

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

  const badges = useMemo(
    () =>
      STATUSES.map((st) => (
        <button
          key={st}
          className={statusFilter === st ? "badge active" : "badge"}
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

  async function fetchPost(postId) {
    try {
      return await queryClient.fetchQuery({
        queryKey: ["post", postId],
        queryFn: () => getPost(token, postId)
      });
    } catch (err) {
      setError(err.message);
      return null;
    }
  }

  async function openPreview(post) {
    const fullPost = await fetchPost(post.id);
    if (!fullPost) return;
    setActivePost(fullPost);
    setShowPreview(true);
  }

  async function openDeleteChannelModal() {
    openDeleteChannel();
  }

  const queryError =
    channelQuery.error?.message ||
    postsQuery.error?.message ||
    publishedQuery.error?.message ||
    queueQuery.error?.message ||
    statsQuery.error?.message;
  const channel = channelQuery.data;
  const stats = statsQuery.data;

  return (
    <section>
      <ChannelHeader
        channel={channel}
        canCreatePost={canCreatePost}
        onAiGenerate={() => setShowAi(true)}
        onCreatePost={() => setShowCreate(true)}
        onDeleteChannel={openDeleteChannelModal}
      />

      <div className="tabs">
        <button className={activeTab === "queue" ? "tab active" : "tab"} onClick={() => setActiveTab("queue")}>
          Публикации
        </button>
        <button className={activeTab === "stats" ? "tab active" : "tab"} onClick={() => setActiveTab("stats")}>
          Статистика
        </button>
      </div>

      {(channelQuery.isLoading || postsQuery.isLoading || publishedQuery.isLoading || queueQuery.isLoading || statsQuery.isLoading) && (
        <div className="hint">Загрузка...</div>
      )}
      {(error || queryError) && <div className="error">{error || queryError}</div>}

      {activeTab === "queue" && (
        <div>
          <PostsGridSection
            title="Лента"
            posts={publishedPosts}
            emptyText="Пока нет опубликованных постов."
            onOpen={openPreview}
            getMeta={() => "Опубликован"}
            getTime={(post) => post.published_at || post.scheduled_at}
            showLoadMore={hasPublishedMore}
            onLoadMore={() => publishedQuery.fetchNextPage()}
            isLoadingMore={publishedQuery.isFetching}
          />

          <PostsGridSection
            title="Очередь"
            posts={queuePosts}
            emptyText="В очереди пока нет постов."
            onOpen={openPreview}
            getMeta={(post) => STATUS_LABELS[post.status] || post.status}
            getTime={(post) => post.scheduled_at || post.published_at}
            showLoadMore={hasQueueMore}
            onLoadMore={() => queueQuery.fetchNextPage()}
            isLoadingMore={queueQuery.isFetching}
          />

          <div className="grid-section">
            <h2>Предложения от агента</h2>
            <div className="empty">Пока нет предложений.</div>
          </div>

          <div className="badge-row">{badges}</div>
          <PostsList
            posts={posts}
            onOpen={openPreview}
            onSubmitApproval={submitApproval}
            onApprove={approve}
            onReject={reject}
            onSchedule={schedule}
            onPublishNow={publishNow}
            onDelete={removePost}
            canCreatePost={canCreatePost}
            canApprove={canApprove}
            statusLabels={STATUS_LABELS}
            isSubmitting={isSubmitting}
            isApproving={isApproving}
            isRejecting={isRejecting}
            isScheduling={isScheduling}
            isPublishing={isPublishing}
            isDeleting={isDeleting}
          />
          {postsQuery.hasNextPage && (
            <div className="actions">
              <button className="ghost-dark" onClick={() => postsQuery.fetchNextPage()} disabled={postsQuery.isFetching}>
                {postsQuery.isFetching ? "Загрузка..." : "Показать еще"}
              </button>
            </div>
          )}
        </div>
      )}

      {activeTab === "stats" && (
        <div className="stats">
          <div className="stat-card">
            <div className="label">Views доступно</div>
            <div className="value">{stats?.views_available ? "Да" : "Нет"}</div>
          </div>
          <div className="stat-card">
            <div className="label">Средние просмотры</div>
            <div className="value">{stats?.avg_views_last_n ?? "—"}</div>
          </div>
          <div className="stat-card">
            <div className="label">Подписчики</div>
            <div className="value">{stats?.subscribers ?? "—"}</div>
          </div>
        </div>
      )}

      {showPreview && activePost && (
        <PostPreviewModal
          post={activePost}
          onClose={() => setShowPreview(false)}
          onEdit={() => {
            setShowPreview(false);
            setShowEdit(true);
          }}
        />
      )}

      {showEdit && activePost && (
        <EditPostModal
          post={activePost}
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
          onClose={() => setShowCreate(false)}
          onCreated={async () => {
            await invalidatePosts();
          }}
        />
      )}
      {showAi && (
        <AiGenerateModal
          channelId={id}
          onClose={() => setShowAi(false)}
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

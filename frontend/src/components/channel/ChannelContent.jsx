import PostsGridSection from "./PostsGridSection.jsx";
import PostsGridList from "./PostsGridList.jsx";

export default function ChannelContent({
  activeTab,
  onChangeTab,
  isLoading,
  error,
  publishedPosts,
  queuePosts,
  hasPublishedMore,
  hasQueueMore,
  onLoadMorePublished,
  onLoadMoreQueue,
  isPublishedFetching,
  isQueueFetching,
  posts,
  badges,
  onOpenPost,
  statusLabels,
  hasPostsMore,
  onLoadMorePosts,
  isPostsFetching,
  stats,
  onOpenAgentSettings
}) {
  return (
    <>
      <div className="tabs">
        <button className={activeTab === "queue" ? "tab active" : "tab"} onClick={() => onChangeTab("queue")}>
          Публикации
        </button>
        <button className={activeTab === "stats" ? "tab active" : "tab"} onClick={() => onChangeTab("stats")}>
          Статистика
        </button>
      </div>

      {isLoading && (
        <div className="skeleton-grid">
          {Array.from({ length: 6 }).map((_, idx) => (
            <div key={idx} className="skeleton-card">
              <div className="skeleton-line title" />
              <div className="skeleton-line" />
              <div className="skeleton-line" />
              <div className="skeleton-line short" />
            </div>
          ))}
        </div>
      )}
      {error && <div className="error">{error}</div>}

      {activeTab === "queue" && (
        <div>
          <PostsGridSection
            title="Лента"
            posts={publishedPosts}
            emptyText="Пока нет опубликованных постов."
            onOpen={onOpenPost}
            getMeta={() => "Опубликован"}
            getTime={(post) => post.published_at || post.scheduled_at}
            showLoadMore={hasPublishedMore}
            onLoadMore={onLoadMorePublished}
            isLoadingMore={isPublishedFetching}
          />

          <PostsGridSection
            title="Очередь"
            posts={queuePosts}
            emptyText="В очереди пока нет постов."
            onOpen={onOpenPost}
            getMeta={(post) => statusLabels[post.status] || post.status}
            getTime={(post) => post.scheduled_at || post.published_at}
            showLoadMore={hasQueueMore}
            onLoadMore={onLoadMoreQueue}
            isLoadingMore={isQueueFetching}
          />

          <div className="grid-section">
          <div className="section-header">
            <h2>Предложения</h2>
            <button type="button" className="icon-button ghost" onClick={onOpenAgentSettings} aria-label="Настройки агента">
              <svg className="icon-gear" viewBox="0 0 24 24" aria-hidden="true">
                <path
                  d="M12 8.5a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7Zm9 3.5a7.7 7.7 0 0 0-.12-1.35l2.12-1.65-2-3.46-2.52 1a7.98 7.98 0 0 0-2.35-1.36l-.38-2.68h-4l-.38 2.68a7.98 7.98 0 0 0-2.35 1.36l-2.52-1-2 3.46 2.12 1.65A7.7 7.7 0 0 0 3 12c0 .46.04.91.12 1.35L1 15l2 3.46 2.52-1c.7.56 1.5 1.01 2.35 1.36l.38 2.68h4l.38-2.68c.85-.35 1.65-.8 2.35-1.36l2.52 1 2-3.46-2.12-1.65c.08-.44.12-.89.12-1.35Z"
                  fill="currentColor"
                />
              </svg>
            </button>
          </div>
            <div className="empty">Пока нет предложений.</div>
          </div>

          <div className="badge-row sticky-filters">{badges}</div>
          <PostsGridList
            posts={posts}
            onOpen={onOpenPost}
            statusLabels={statusLabels}
          />
          {hasPostsMore && (
            <div className="actions">
              <button className="ghost-dark" onClick={onLoadMorePosts} disabled={isPostsFetching}>
                {isPostsFetching ? "Загрузка..." : "Показать еще"}
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
    </>
  );
}

export default function ChannelHeader({
  channel,
  canCreatePost,
  canDeleteChannel,
  onCreatePost,
  onDeleteChannel
}) {
  return (
    <div className="page-header">
      <div>
        <div className="header-with-avatar">
          {channel?.avatar_url && <img className="channel-avatar" src={channel.avatar_url} alt="" loading="lazy" />}
          <div>
            <h1>{channel?.title || "Канал"}</h1>
            <p className="muted">{channel?.telegram_channel_identifier}</p>
          </div>
        </div>
      </div>
      <div className="actions-inline">
        {canCreatePost && (
          <button className="primary" onClick={onCreatePost}>
            Создать пост
          </button>
        )}
        {canDeleteChannel && (
          <button className="ghost-dark" onClick={onDeleteChannel}>
            Удалить канал
          </button>
        )}
      </div>
    </div>
  );
}

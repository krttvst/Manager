import enum


class UserRole(str, enum.Enum):
    admin = "admin"
    author = "author"
    editor = "editor"
    viewer = "viewer"


class PostStatus(str, enum.Enum):
    draft = "draft"
    pending = "pending"
    approved = "approved"
    scheduled = "scheduled"
    published = "published"
    rejected = "rejected"
    failed = "failed"

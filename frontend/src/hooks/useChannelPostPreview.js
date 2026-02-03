import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { getPost } from "../api/posts.js";

export function useChannelPostPreview({ token, onError }) {
  const queryClient = useQueryClient();
  const [activePost, setActivePost] = useState(null);
  const [showPreview, setShowPreview] = useState(false);
  const [showEdit, setShowEdit] = useState(false);

  async function fetchPost(postId) {
    try {
      return await queryClient.fetchQuery({
        queryKey: ["post", postId],
        queryFn: () => getPost(token, postId)
      });
    } catch (err) {
      onError?.(err);
      return null;
    }
  }

  async function openPreview(post) {
    const fullPost = await fetchPost(post.id);
    if (!fullPost) return;
    setActivePost(fullPost);
    setShowPreview(true);
  }

  async function openEdit(post) {
    const fullPost = await fetchPost(post.id);
    if (!fullPost) return;
    setActivePost(fullPost);
    setShowEdit(true);
  }

  function openEditFromActive() {
    if (!activePost) return;
    setShowEdit(true);
  }

  return {
    activePost,
    showPreview,
    showEdit,
    setShowPreview,
    setShowEdit,
    openPreview,
    openEdit,
    openEditFromActive
  };
}


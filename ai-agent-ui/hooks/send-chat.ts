import axios from "axios";

export async function sendChat(
  userInput: string,
  state: any,
  threadId: string,
  file?: File | null,
  type?: "live_image" | "id_card" | null,
) {
  const formData = new FormData();
  formData.append("user_input", userInput);
  formData.append("state", JSON.stringify(state || {}));
  formData.append("thread_id", threadId);
  formData.append("type", type || "");
  if (file) formData.append("file", file);

  // CRITICAL: Send the ID back if we have one
  if (threadId) {
      formData.append("thread_id", threadId); 
  }
  const res = await axios.post("http://localhost:8000/chat", formData, { headers: { "Content-Type": "multipart/form-data" } });

  const data = await res.data;
  console.log("API response data:", data);
  return data;
}

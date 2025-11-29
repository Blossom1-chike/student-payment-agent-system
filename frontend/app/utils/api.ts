import axios from "axios";

export async function sendChat(
  userInput: string,
  state: any,
  file?: File
) {
  const formData = new FormData();
  formData.append("user_input", userInput);
  formData.append("state", JSON.stringify(state || {}));
  if (file) formData.append("file", file);

  const res = await axios.post("https://didactic-computing-machine-wxgg9qpqjq9396jg-8000.app.github.dev/chat", formData, { headers: { "Content-Type": "multipart/form-data" } });

  const data = await res.data;
  console.log("API response data:", data);
  return data;
}

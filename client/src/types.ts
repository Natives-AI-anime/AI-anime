export const HttpMethod = {
  GET: "GET",
  POST: "POST",
  PUT: "PUT",
  DELETE: "DELETE",
  PATCH: "PATCH",
  HEAD: "HEAD",
  OPTIONS: "OPTIONS",
} as const;

export type HttpMethod = (typeof HttpMethod)[keyof typeof HttpMethod];

export interface RequestConfig {
  url: string;
  method: HttpMethod;
  headers: { key: string; value: string }[];
  body: string;
}

export interface ResponseData {
  status: number;
  statusText: string;
  data: any;
  headers: any;
  duration: number;
}

export interface ChatMessage {
  id: string;
  role: "user" | "model" | "system";
  content: string;
  timestamp: number;
  isThinking?: boolean;
}

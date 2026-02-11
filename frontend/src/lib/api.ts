import { API_BASE_URL } from "./constants";
import type {
  CustomerOverview,
  SearchResult,
  UploadResponse,
  UploadStatus,
} from "./types";

/* ------------------------------------------------------------------ */
/*  Generic fetch helper                                               */
/* ------------------------------------------------------------------ */

async function request<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${path}`;
  const res = await fetch(url, options);

  if (!res.ok) {
    const body = await res.text().catch(() => "Unknown error");
    throw new Error(`API ${res.status}: ${body}`);
  }

  return res.json() as Promise<T>;
}

/* ------------------------------------------------------------------ */
/*  Upload endpoints                                                   */
/* ------------------------------------------------------------------ */

export async function uploadFile(
  type: string,
  file: File
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  return request<UploadResponse>(`/upload/${type}`, {
    method: "POST",
    body: formData,
  });
}

export async function getUploadStatus(): Promise<UploadStatus> {
  return request<UploadStatus>("/upload/status");
}

export async function clearData(): Promise<void> {
  await request<{ status: string }>("/upload/clear", {
    method: "DELETE",
  });
}

/* ------------------------------------------------------------------ */
/*  Search                                                             */
/* ------------------------------------------------------------------ */

export async function searchCustomer(
  query: string
): Promise<SearchResult[]> {
  return request<SearchResult[]>(
    `/customer/search?q=${encodeURIComponent(query)}`
  );
}

/* ------------------------------------------------------------------ */
/*  Customer overview                                                  */
/* ------------------------------------------------------------------ */

export async function getCustomerOverview(
  bcn: string
): Promise<CustomerOverview> {
  return request<CustomerOverview>(
    `/customer/${encodeURIComponent(bcn)}/overview`
  );
}

import { useQuery } from "@tanstack/react-query";
import { listAuditLogs } from "../api/auditLogs.js";

export function useAuditLogsQuery(token, params) {
  return useQuery({
    queryKey: ["auditLogs", params ?? {}],
    queryFn: () => listAuditLogs(token, params),
    enabled: Boolean(token)
  });
}

